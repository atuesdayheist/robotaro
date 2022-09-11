import requests
import os

APPLICATION_ID = os.environ.get('APPLICATION_ID')
BOT_SECRET_KEY = os.environ.get('BOT_SECRET_KEY')
PUBLIC_KEY = os.environ.get('PUBLIC_KEY')
TEST_GUILD_ID = os.environ.get('TEST_GUILD_ID')

url = f'https://discord.com/api/v10/applications/{APPLICATION_ID}/guilds/{TEST_GUILD_ID}/commands'

json = {
    'name': 'beep',
    'type': 1,
    'description': 'Beep boop'
}

headers = {
    'Authorization': f'Bot {BOT_SECRET_KEY}'
}

r = requests.post(url, headers=headers, json=json)
print(r.text)
