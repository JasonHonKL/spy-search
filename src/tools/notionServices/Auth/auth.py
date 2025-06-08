import urllib.parse
import requests
from notion_client import Client

class NotionAuth:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = (
            f"https://api.notion.com/v1/oauth/authorize?"
            f"client_id={client_id}&"
            f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
            f"response_type=code&"
            f"owner=user"
        )

    def get_auth_url(self):
        """Generate OAuth authorization URL."""
        return self.auth_url

    def get_access_token(self, code):
        """Exchange authorization code for access token."""
        url = "https://api.notion.com/v1/oauth/token"
        auth = (self.client_id, self.client_secret)
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        try:
            response = requests.post(url, auth=auth, json=data)
            response.raise_for_status()
            return response.json()["access_token"]
        except requests.RequestException as e:
            raise Exception(f"Error exchanging code: {str(e)}")

    def get_notion_client(self, access_token):
        """Initialize Notion client with access token."""
        return Client(auth=access_token) 