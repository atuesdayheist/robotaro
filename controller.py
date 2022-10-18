import json
from utils import upload_to_s3, download_from_s3
from datetime import datetime, timedelta

def set_pin():
    download_from_s3('pins.json', '/tmp/pins.json')
    with open('/tmp/pins.json') as jsonfile:
        PIN_REGISTRY = json.load(jsonfile)
    return PIN_REGISTRY

def update_pin(PIN_REGISTRY, BACKUP_INTERVAL):
    last_backup_date = datetime.strptime(PIN_REGISTRY["last_backup"], '%Y-%m-%d')
    new_backup = False
    
    if datetime.today() - timedelta(days=BACKUP_INTERVAL) > last_backup_date:
        today = datetime.today().strftime('%Y-%m-%d')
        PIN_REGISTRY["last_backup"] = today
        new_backup = True

    with open('/tmp/pins.json', 'w') as pinlist:
        json.dump(PIN_REGISTRY, pinlist)
    
    if new_backup == True:
        upload_to_s3('/tmp/pins.json', f'pinlist_backup/pin_backup_{today}.json')
    print("updating pin")
    upload_to_s3('/tmp/pins.json', f'pins.json')
    return "Pin Updated"