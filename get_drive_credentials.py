"""
Find out google drive api secrets to be put into lamba environment
variables

1. Create client_secret.js in the google api console following this guide:
   https://developers.google.com/drive/v3/web/quickstart/python#step_1_turn_on_the_api_name
2. Store the client_secret.js into this projects directory
3. `pip install oauth2client`
4. Run script: `python get_drive_credentials.py`
5. Copy-paste script output into lambda environment variables
6. Delete client_secret.json
"""

from oauth2client import client, tools

class MyStorage(client.Storage):
	def locked_put(self, credentials):
		print('put those into your lambda functions environment variables:')
		print("="*70)
		print('UPLOAD_TYPE: gdrive')
		print("GDRIVE_CLIENT_ID: {}\nGDRIVE_CLIENT_SECRET: {}\nGDRIVE_REFRESH_TOKEN: {}".format(
			credentials.client_id, credentials.client_secret, credentials.refresh_token))
		print("="*70)

flow = client.flow_from_clientsecrets('client_secret.json', 'https://www.googleapis.com/auth/drive.file')
flow.user_agent = 'Scanner Uploader'
storage = MyStorage()
tools.run_flow(flow, storage)
