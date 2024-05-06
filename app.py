import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from telethon.sync import TelegramClient
import os


api_id = '28367018'
api_hash = 'dff8ebd3e6cb937d5a4fc91192262571'
phone_number = '+919360985570'
target_username = '+918098740973'
file_list_path = '/content/drive/My Drive/output_file.txt'

client = TelegramClient('session_name', api_id, api_hash)

def callback(current,total):
    print(current/total)

async def send_file(f):
    async with client as action:
          await client.start(phone=phone_number)
          try:
            await client.send_file(target_username, f,progress_callback=callback)
          except:
            print(f+"not uploaded")



credentials = service_account.Credentials.from_service_account_file(
        'drive2tele-b3e53b53d1ce.json',
        scopes=['https://www.googleapis.com/auth/drive']
    )

    # Build the Drive API service
service = build('drive', 'v3', credentials=credentials)

    # Define the folder ID
folder_id = '1-6BPHqRQftd4_uNlrdYqK21tFMJSAXRy'

page_token = None

while True:
    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="nextPageToken, files(name, size, id)",
        pageToken=page_token
    ).execute()

    files = results.get('files', [])
    for file in files:
        file_name = file['name']
        file_size = int(file.get('size', 0))
        
        # Check if the 'id' key exists in the file dictionary
        if 'id' not in file:
            print(f"Skipping '{file_name}' due to missing 'id' key.")
            continue

        print(file_name, file_size)
        if file_size < 250 * 1024 * 1024 and 'b' <= file_name[0].lower() <= 'z':  # Convert MB to bytes
            try:
                request = service.files().get_media(fileId=file['id'])
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                with open(file_name, 'wb') as f:
                    f.write(fh.getvalue())
                print(f"Downloaded '{file_name}' with size {file_size/1024} MB.")
                client.loop.run_until_complete(send_file(file_name))
                os.remove(file_name)
            except:
                print("skipped due to binary issue")
           
        else:
            print(f"Skipping '{file_name}' due to its large size ({file_size} bytes).")
                
    page_token = results.get('nextPageToken')
    if not page_token:
        break
