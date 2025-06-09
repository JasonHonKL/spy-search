import urllib.parse
import requests
from notion_client import Client
from flask import Flask, request, redirect
import threading
import webbrowser
from .token_storage import TokenStorage

class NotionAuth:
    def __init__(self, token_storage):
        self.client_id = None
        self.client_secret = None
        self.redirect_uri = None
        self.integration_token = None
        self.token_storage = token_storage
        self.auth_url = None
        self.app = None
        self.auth_code = None
        self.access_token = None

    def get_user_credentials(self, user_id, auth_mode):
        """Prompt user for Notion credentials or token based on auth mode."""
        if auth_mode == "token":
            integration_token = self.token_storage.get_integration_token(user_id)
            if integration_token:
                print("Found stored integration token. Use this? (y/n)")
                if input().lower() == 'y':
                    return None, None, None, integration_token
            
            print("Please enter your Notion integration token (see README.md):")
            integration_token = input("Enter Integration Token (starts with 'secret_'): ").strip()
            self.token_storage.save_integration_token(user_id, integration_token)
            return None, None, None, integration_token
        else:
            # TODO: OAuth method commented out as Notion public integration requires additional verification and approval process
            # credentials = self.token_storage.get_credentials(user_id)
            # if credentials:
            #     print("Found stored OAuth credentials. Use these? (y/n)")
            #     if input().lower() == 'y':
            #         return credentials["client_id"], credentials["client_secret"], credentials["redirect_uri"], None
            # 
            # print("Please enter your Notion OAuth credentials (see README.md):")
            # client_id = input("Enter Client ID: ").strip()
            # client_secret = input("Enter Client Secret: ").strip()
            # redirect_uri = input("Enter Redirect URI (e.g., http://localhost:8000/callback): ").strip()
            # self.token_storage.save_credentials(user_id, client_id, client_secret, redirect_uri)
            # return client_id, client_secret, redirect_uri, None
            raise NotImplementedError("OAuth authentication is currently not supported as it requires Notion public integration approval.")

    # TODO: OAuth setup method commented out as Notion public integration requires additional verification and approval process
    # def setup_oauth(self, client_id, redirect_uri):
    #     """Set up OAuth parameters and Flask server."""
    #     self.auth_url = (
    #         f"https://api.notion.com/v1/oauth/authorize?"
    #         f"client_id={client_id}&"
    #         f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
    #         f"response_type=code&"
    #         f"owner=user"
    #     )
    #     self.app = Flask(__name__)
    #     self.setup_routes()

    # def setup_routes(self):
    #     """Set up Flask routes for OAuth callback."""
    #     @self.app.route('/callback')
    #     def callback():
    #         code = request.args.get('code')
    #         if code:
    #             self.auth_code = code
    #             return "Authorization successful! You can close this window."
    #         return "Error: No code provided.", 400

    # def start_flask_server(self):
    #     """Start Flask server in a separate thread."""
    #     threading.Thread(target=lambda: self.app.run(port=8000), daemon=True).start()

    # def get_access_token(self, user_id, code=None):
    #     """Get or refresh access token for a user."""
    #     stored_token = self.token_storage.get_token(user_id)
    #     if stored_token:
    #         return stored_token

    #     if not code and not self.auth_code:
    #         raise Exception("No authorization code provided.")

    #     code = code or self.auth_code
    #     url = "https://api.notion.com/v1/oauth/token"
    #     auth = (self.client_id, self.client_secret)
    #     data = {
    #         "grant_type": "authorization_code",
    #         "code": code,
    #         "redirect_uri": self.redirect_uri,
    #     }
    #     try:
    #         response = requests.post(url, auth=auth, json=data)
    #         response.raise_for_status()
    #         token_data = response.json()
    #         access_token = token_data["access_token"]
    #         refresh_token = token_data.get("refresh_token")
    #         self.token_storage.save_token(user_id, access_token, refresh_token)
    #         self.access_token = access_token
    #         return access_token
    #     except requests.RequestException as e:
    #         raise Exception(f"Error exchanging code: {str(e)}")

    # def refresh_access_token(self, user_id):
    #     """Refresh access token using stored refresh token."""
    #     refresh_token = self.token_storage.get_refresh_token(user_id)
    #     if not refresh_token:
    #         raise Exception("No refresh token available.")

    #     url = "https://api.notion.com/v1/oauth/token"
    #     auth = (self.client_id, self.client_secret)
    #     data = {
    #         "grant_type": "refresh_token",
    #         "refresh_token": refresh_token,
    #     }
    #     try:
    #         response = requests.post(url, auth=auth, json=data)
    #         response.raise_for_status()
    #         token_data = response.json()
    #         access_token = token_data["access_token"]
    #         new_refresh_token = token_data.get("refresh_token", refresh_token)
    #         self.token_storage.save_token(user_id, access_token, new_refresh_token)
    #         return access_token
    #     except requests.RequestException as e:
    #         raise Exception(f"Error refreshing token: {str(e)}")

    def get_integration_token(self, user_id):
        """Retrieve stored integration token or use provided one."""
        stored_token = self.token_storage.get_integration_token(user_id)
        if stored_token:
            return stored_token
        if self.integration_token:
            self.token_storage.save_integration_token(user_id, self.integration_token)
            return self.integration_token
        raise Exception("No integration token provided or stored.")

    def get_notion_client(self, token):
        """Initialize Notion client with access or integration token."""
        return Client(auth=token)

    def authenticate(self, user_id, auth_mode="oauth"):
        """Handle authentication based on mode."""
        # Get credentials or token
        self.client_id, self.client_secret, self.redirect_uri, self.integration_token = self.get_user_credentials(user_id, auth_mode)

        if auth_mode == "token":
            return self.get_integration_token(user_id)
        else:
            if self.client_id and self.redirect_uri:
                # TODO: OAuth setup method commented out as Notion public integration requires additional verification and approval process
                # self.setup_oauth(self.client_id, self.redirect_uri)
                pass
            if self.token_storage.get_token(user_id):
                try:
                    return self.refresh_access_token(user_id)
                except:
                    pass
            self.start_flask_server()
            webbrowser.open(self.auth_url)
            print("Waiting for OAuth authorization...")
            while not self.auth_code:
                pass
            return self.get_access_token(user_id)