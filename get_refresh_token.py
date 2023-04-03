import os
import json
import tempfile
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

if __name__ == "__main__":
    with open("client_secret.json", "r") as secrets_file:
        secrets_data = json.load(secrets_file)

    # Add the required scope
    secrets_data["installed"]["scopes"] = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    # Save the updated secrets to a temporary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_secrets_file:
        json.dump(secrets_data, temp_secrets_file)
        temp_secrets_file.flush()

    # Get the credentials using the temporary file
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    flow = InstalledAppFlow.from_client_secrets_file(temp_secrets_file.name, scopes)
    credentials = flow.run_local_server(port=0)

    token_data = {
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "refresh_token": credentials.refresh_token,
        "type": "authorized_user"
    }

    with open("config.json", "w") as config_file:
        json.dump(token_data, config_file)

    print("Refresh token saved to config.json")

    # Remove the temporary file
    os.unlink(temp_secrets_file.name)

