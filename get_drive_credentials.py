"""
Find out google people api secrets to be put into GOOGLE_PEOPLE_ACCESS_TOKEN:

1. Create client_secret.js in the google api console following this guide:
   https://developers.google.com/people/quickstart/python
2. Store the client_secret.js into this projects directory
3. Run script: `python3 get_people_credentials.py`
4. From script output copy-paste the three strings into secrets.yml
5. Delete client_secret.json
"""

from oauth2client import client, tools

class MyStorage(client.Storage):
	def locked_put(self, credentials):
		print("="*70)
		print("client_id: {}\nclient_secret: {}\nrefresh_token: {}".format(
			credentials.client_id, credentials.client_secret, credentials.refresh_token))
		print("="*70)

flow = client.flow_from_clientsecrets('client_secret.json', 'https://www.googleapis.com/auth/drive.file')
flow.user_agent = 'Scanner Uploader'
storage = MyStorage()
tools.run_flow(flow, storage)
