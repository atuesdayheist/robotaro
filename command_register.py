import requests
import os

APPLICATION_ID = os.environ.get('APPLICATION_ID')
BOT_SECRET_KEY = os.environ.get('BOT_SECRET_KEY')
PUBLIC_KEY = os.environ.get('PUBLIC_KEY')
TEST_GUILD_ID = os.environ.get('TEST_GUILD_ID')

test_url = f'https://discord.com/api/v10/applications/{APPLICATION_ID}/guilds/{TEST_GUILD_ID}/commands'
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

# json = {
#     'name': 'pin',
#     'type': 1,
#     'description': 'Adds a new pin',
#     'options': [
#         {
#             "name": "pin_name",
#             "description": "Name of the Pin",
#             "type": 3,
#             "required": True,
#         },
#         {
#             "name": "pin_value",
#             "description": "What should this return?",
#             "type": 3,
#             "required": True,
#         }
#     ]
# }

# json = {
#     'name': 'random',
#     'type': 1,
#     'description': 'Returns a random pin'
# }

json = {
    'name': 'pin_file',
    'type': 1,
    'description': 'Adds a new pin.',
    'options': [
        {
            "name": "pin_name",
            "description": "Name of the Pin",
            "type": 3,
            "required": True,
        },
        {
            "name": "pin_attach",
            "description": "Attach a file",
            "type": 11,
            "required": True,
        }
    ]
}

# json = {
#     'name': 'pin_text',
#     'type': 1,
#     'description': 'Adds a new pin.',
#     'options': [
#         {
#             "name": "pin_name",
#             "description": "Name of the Pin",
#             "type": 3,
#             "required": True,
#         },
#         {
#             "name": "pin_text",
#             "description": "Response Text",
#             "type": 3,
#             "required": True,
#         }
#     ]
# }



headers = {
    'Authorization': f'Bot {BOT_SECRET_KEY}'
}

r = requests.post(url, headers=headers, json=json)
print(r.text)
