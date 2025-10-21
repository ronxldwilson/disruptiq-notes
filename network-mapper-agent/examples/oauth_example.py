# Example: OAuth flows
import requests
from oauthlib.oauth2 import WebApplicationClient

# OAuth flow
client = WebApplicationClient('client_id')
token_url = 'https://auth.example.com/token'
token = client.fetch_token(token_url, code='auth_code')

# API call with token
headers = {'Authorization': f'Bearer {token["access_token"]}'}
response = requests.get('https://api.example.com/data', headers=headers)
