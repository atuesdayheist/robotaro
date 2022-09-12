import requests
import os

APPLICATION_ID = os.environ.get('APPLICATION_ID')
BOT_SECRET_KEY = os.environ.get('BOT_SECRET_KEY')
PUBLIC_KEY = os.environ.get('PUBLIC_KEY')
TEST_GUILD_ID = os.environ.get('TEST_GUILD_ID')

url = f'https://discord.com/api/v10/applications/{APPLICATION_ID}/commands'

# json = {
#     'name': 'beep',
#     'type': 1,
#     'description': 'Beep boop'
# }

# json = {
#     'name': 'rt',
#     'type': 1,
#     'description': 'Get a pin',
#     'options': [
#         {
#             "name": "pin_name",
#             "description": "name of the pin",
#             "type": 3,
#             "required": True,
#         }
#     ]
# }

# json = {
#     'name': 'sr',
#     'type': 1,
#     'description': 'Returns a random pin that matches the search key',
#     'options': [
#         {
#             "name": "search_key",
#             "description": "Word to search for",
#             "type": 3,
#             "required": True,
#         }
#     ]
# }

json = {
    'name': 'random',
    'type': 1,
    'description': 'Returns a random pin'
}


headers = {
    'Authorization': f'Bot {BOT_SECRET_KEY}'
}

r = requests.post(url, headers=headers, json=json)
print(r.text)
