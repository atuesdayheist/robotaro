from s3_upload import upload_to_s3
from datetime import datetime, timedelta

def check_pin_backup(backup_datestring):
    last_backup = datetime.strptime(backup_datestring, '%Y-%m-%d')
    if datetime.today() - timedelta(days=7) > last_backup:
        today = datetime.today().strftime('%Y-%m-%d')
        upload_to_s3('pins.json', f'pin_backup_{today}')