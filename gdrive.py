import httplib2
import os
from apiclient import discovery
from oauth2client import client
from apiclient.http import MediaFileUpload

client_id = os.environ['CLIENT_ID']
client_secret =  os.environ['CLIENT_SECRET']
refresh_token = os.environ['REFRESH_TOKEN']

credentials = client.GoogleCredentials(None, 
    client_id, 
    client_secret,
    refresh_token,
    None,
    "https://accounts.google.com/o/oauth2/token",
    'scanner-ocr')

http = credentials.authorize(httplib2.Http())
service = discovery.build('drive', 'v3', http=http)

file_metadata = {
	'name': 'photo.jpg',
	'parents': ['0B0uw1JCogWHubmNjbUFHdnFkTkk']
}
media = MediaFileUpload('photo.jpg',
                        mimetype='image/jpeg')
file = service.files().create(body=file_metadata,
                              media_body=media,
                              fields='id').execute()
print(file.get('id'))