import json
import os
import sys
import random
import requests

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from s3_upload import upload_to_s3
from backup import check_pin_backup

PUBLIC_KEY = os.environ.get("PUBLIC_KEY")
REGISTERED_COMMANDS = ["rt", "sr", "random", "pin_text", "pin_file"]
PIN_REGISTRY = {}
BACKUP_INTERVAL = 7

with open(os.path.join(sys.path[0], 'pins.json')) as jsonfile:
    PIN_REGISTRY = json.load(jsonfile)

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
            random_key = random.sample(all_keys, 1)[0]
            sr_url = PIN_REGISTRY["keywords"][random_key]["url"]
            if len(all_keys) == 0:
                return { "type": 4, "data": { "content": "None found" }}
            else:
                return { "type": 4, "data": { "content": f'{random_key} {sr_url}' }}

        # Gets a random pin
        elif command == "random":
            random_key = random.sample(PIN_REGISTRY["keywords"].keys(), 1)[0]
            random_url = PIN_REGISTRY["keywords"][random_key]["url"]
            return { "type": 4, "data": { "content": f'{random_key} {random_url}' }}

        # Makes a new Pin
        elif command == "pin_file":
            pin_name = data["options"][0]["value"]

            if pin_name in PIN_REGISTRY["keywords"].keys():
                return { "type": 4, "data": { "content": "Pin already exists" }}
            else: 
                # Backup the pins if last backup date was more than a week ago
                backed_up = check_pin_backup(PIN_REGISTRY["last_backup"], BACKUP_INTERVAL)
                if backed_up:
                    PIN_REGISTRY["last_backup"] = backed_up

                attachment_id = data["options"][1]["value"]
                attachment_url = data["resolved"]["attachments"][attachment_id]["url"]
                filename = data["resolved"]["attachments"][attachment_id]["filename"]

                print("Attachments?")
                print(attachment_url)

                if attachment_url[:4] == 'http' and (attachment_url[-4] == '.' or attachment_url[-5] == '.'):
                    r = requests.get(attachment_url)
                    if not r.ok:
                        return { "type": 4, "data": { "content": "This didn't work for some reason, ask Raph" }}
                    else:
                        print("Try uploading to S3")
                        open(f'backup/{filename}', 'wb').write(r.content)
                        upload_to_s3(f'backup/{filename}', f'{filename}')
                
                PIN_REGISTRY["keywords"][pin_name] = {
                    "url": attachment_url,
                    "usage": 0,
                    "pinned by": body["member"]["user"]["username"],
                    "include_random": True,
                    "ratpot": False
                }

                with open('pins.json', 'w') as pinlist:
                    json.dump(PIN_REGISTRY, pinlist)

            return { "type": 4, "data": { "content": "Successfully Pinned" }}

        elif command == "pin_text":
            pin_name = data["options"][0]["value"]

            if pin_name in PIN_REGISTRY["keywords"].keys():
                return { "type": 4, "data": { "content": "Pin already exists" }}
            else: 
                # Backup the pins if last backup date was more than a week ago
                backed_up = check_pin_backup(PIN_REGISTRY["last_backup"], BACKUP_INTERVAL)
                if backed_up:
                    PIN_REGISTRY["last_backup"] = backed_up

                pin_text = data["options"][1]["value"]
                if pin_text[:4] == 'http' and (pin_text[-4] == '.' or pin_text[-5] == '.'):
                    filename = pin_text.split("/")[-1]
                    r = requests.get(pin_text)
                    if not r.ok:
                        return { "type": 4, "data": { "content": "This didn't work for some reason, ask Raph" }}
                    else:
                        print("Try uploading to S3")
                        open(os.path.join(sys.path[0], f'backup/{filename}'), 'wb').write(r.content)
                        upload_to_s3(f'backup/{filename}', f'{filename}')

                PIN_REGISTRY["keywords"][pin_name] = {
                    "url": pin_text,
                    "usage": 0,
                    "pinned by": body["member"]["user"]["username"],
                    "include_random": True,
                    "ratpot": False
                }

                with open(os.path.join(sys.path[0], 'pins.json'), 'w') as pinlist:
                    json.dump(PIN_REGISTRY, pinlist)

            return { "type": 4, "data": { "content": "Successfully Pinned" }}
    else:
        print("Invalid Command. This is why your code doesn't work, you idiot.")