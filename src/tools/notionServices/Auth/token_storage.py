import keyring
import json

class TokenStorage:
    def __init__(self, service_name="NotionChatbot"):
        self.service_name = service_name

    def save_token(self, user_id, access_token, refresh_token=None):
        """Save access and refresh tokens securely."""
        token_data = {"access_token": access_token}
        if refresh_token:
            token_data["refresh_token"] = refresh_token
        keyring.set_password(self.service_name, f"{user_id}_tokens", json.dumps(token_data))

    def get_token(self, user_id):
        """Retrieve access token."""
        token_data = keyring.get_password(self.service_name, f"{user_id}_tokens")
        if token_data:
            return json.loads(token_data).get("access_token")
        return None

    def get_refresh_token(self, user_id):
        """Retrieve refresh token."""
        token_data = keyring.get_password(self.service_name, f"{user_id}_tokens")
        if token_data:
            return json.loads(token_data).get("refresh_token")
        return None

    def delete_token(self, user_id):
        """Delete tokens for a user."""
        try:
            keyring.delete_password(self.service_name, f"{user_id}_tokens")
        except keyring.errors.PasswordDeleteError:
            pass

    def save_credentials(self, user_id, client_id, client_secret, redirect_uri):
        """Save OAuth credentials securely."""
        credentials = {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri
        }
        keyring.set_password(self.service_name, f"{user_id}_credentials", json.dumps(credentials))

    def get_credentials(self, user_id):
        """Retrieve OAuth credentials."""
        credentials_data = keyring.get_password(self.service_name, f"{user_id}_credentials")
        if credentials_data:
            return json.loads(credentials_data)
        return None

    def delete_credentials(self, user_id):
        """Delete OAuth credentials for a user."""
        try:
            keyring.delete_password(self.service_name, f"{user_id}_credentials")
        except keyring.errors.PasswordDeleteError:
            pass

    def save_integration_token(self, user_id, integration_token):
        """Save integration token securely."""
        keyring.set_password(self.service_name, f"{user_id}_integration_token", integration_token)

    def get_integration_token(self, user_id):
        """Retrieve integration token."""
        return keyring.get_password(self.service_name, f"{user_id}_integration_token")

    def delete_integration_token(self, user_id):
        """Delete integration token for a user."""
        try:
            keyring.delete_password(self.service_name, f"{user_id}_integration_token")
        except keyring.errors.PasswordDeleteError:
            pass