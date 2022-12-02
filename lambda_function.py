import json
import os
import random
import requests

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from controller import set_pin, update_pin
from utils import upload_to_s3

# Discord Setup Stuff
def verify_signature(event):
    raw_body = event.get("rawBody")
    auth_sig = event['params']['header'].get('x-signature-ed25519')
    auth_ts  = event['params']['header'].get('x-signature-timestamp')
    
    message = auth_ts.encode() + raw_body.encode()
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    verify_key.verify(message, bytes.fromhex(auth_sig)) # raises an error if unequal

def ping_pong(body):
    if body.get("type") == 1:
        return True
    return False

PUBLIC_KEY = os.environ.get("PUBLIC_KEY")
REGISTERED_COMMANDS = ["beep", "rt", "sr", "random", "pin", "pin_file", "search", "taro_response"]
BACKUP_INTERVAL = 7

# Download and set up Pin list
PIN_REGISTRY = set_pin()

def lambda_handler(event, context):
    print(f"event {event}") # debug print
    # verify the signature
    try:
        verify_signature(event)
    except Exception as e:
        raise Exception(f"[UNAUTHORIZED] Invalid request signature: {e}")

    body = event.get('body-json')
    
    # check if message is a ping
    if ping_pong(body):
        return {"type": 1}

    data = body["data"]

    if data["name"] in REGISTERED_COMMANDS:
        command = body["data"]["name"]

        # Status Check
        if command == "beep":
            return { "type": 4, "data": { "content": "Boop" }}

        # Gets a specific pin
        elif command == "rt":
            try:
                return { "type": 4, "data": { "content": PIN_REGISTRY["keywords"][data["options"][0]["value"]]["url"] }}
            except KeyError:
                return { "type": 4, "data": { "content": "No such pin" }}

        # Gets a random pin with the search key specified
        elif command == "sr":
            search_key = data["options"][0]["value"]
            all_keys = [pin_name for pin_name in PIN_REGISTRY["keywords"].keys() if search_key in pin_name and PIN_REGISTRY["keywords"][pin_name]["include_random"] == True]
            if len(all_keys) == 0:
                return { "type": 4, "data": { "content": "None found" }}
            random_key = random.sample(all_keys, 1)[0]
            sr_url = PIN_REGISTRY["keywords"][random_key]["url"]
            return { "type": 4, "data": { "content": f'{random_key} {sr_url}' }}

        # Searchs for a pin
        elif command == "search":
            search_key = data["options"][0]["value"]
            matches = [ key for key in PIN_REGISTRY["keywords"].keys() if search_key in key]
            if len(matches) > 0:
                match_string = ", ".join(matches)
                return { "type": 4, "data": { "content": f'```{match_string}```' }}
            else:
                return { "type": 4, "data": { "content": 'No matches were found' }}

        # Gets a random pin
        elif command == "random":
            random_key = random.sample(PIN_REGISTRY["keywords"].keys(), 1)[0]
            random_url = PIN_REGISTRY["keywords"][random_key]["url"]
            return { "type": 4, "data": { "content": f'{random_key} {random_url}' }}

        # Makes a new Pin
        elif command == "pin" or command == "pin_file":
            pin_name = data["options"][0]["value"]
            if pin_name in PIN_REGISTRY["keywords"].keys():
                return { "type": 4, "data": { "content": "Pin already exists" }}
            
            if command == "pin":
                pin_text = data["options"][1]["value"]
                # Check to see if the pin is a file url anyway
                if pin_text[:4] == 'http' and (pin_text[-4] == '.' or pin_text[-5] == '.'):
                    r = requests.get(pin_text)
                    if not r.ok:
                        print(json.loads(r.text))
                        return { "type": 4, "data": { "content": "This didn't work for some reason, ask Raph" }}
                    else:
                        # backing up the file since Discord keeps losing them
                        filename = ".".join([pin_name, pin_text.split(".")[-1]])
                        open(f'/tmp/{filename}', 'wb').write(r.content)
                        upload_to_s3(f'/tmp/{filename}', f'pin_backup/{filename}')
                        os.remove(f'/tmp/{filename}')

                PIN_REGISTRY["keywords"][pin_name] = {
                    "url": pin_text,
                    "usage": 0,
                    "pinned by": body["member"]["user"]["username"],
                    "include_random": True,
                    "ratpot": False
                }

                update_pin(PIN_REGISTRY, BACKUP_INTERVAL)
                return { "type": 4, "data": { "content": "Pin Updated" }}
                
            else:
                attachment_id = data["options"][1]["value"]
                attachment_url = data["resolved"]["attachments"][attachment_id]["url"]
                if attachment_url[:4] == 'http' and (attachment_url[-4] == '.' or attachment_url[-5] == '.'):
                    r = requests.get(attachment_url)
                    if not r.ok:
                        print(json.loads(r.text))
                        return { "type": 4, "data": { "content": "This didn't work for some reason, ask Raph" }}
                    else:
                        # backing up the file since Discord keeps losing them
                        filename = ".".join([pin_name, attachment_url.split(".")[-1]])
                        open(f'/tmp/{filename}', 'wb').write(r.content)
                        upload_to_s3(f'/tmp/{filename}', f'pin_backup/{filename}')
                        os.remove(f'/tmp/{filename}')

                        # Update pins.json
                        PIN_REGISTRY["keywords"][pin_name] = {
                            "url": attachment_url,
                            "usage": 0,
                            "pinned by": body["member"]["user"]["username"],
                            "include_random": True,
                            "ratpot": False
                        }

                        update_pin(PIN_REGISTRY, BACKUP_INTERVAL)
                        return { "type": 4, "data": { "content": "Pin Updated" }}

        # Testing responses
        elif command == "taro_response":
            interaction_id = event["rawBody"]["id"]
            interaction_token = event["rawBody"]["token"]
            response_url = f'https://discord.com/api/v10/interactions/{interaction_id}/{interaction_token}/callback'
            response_json = {
                "type": 4,
                "data": {
                    "content": "Congrats on sending your command!"
                }
            }
            response = requests.post(response_url, json=response_json)
            print(response)