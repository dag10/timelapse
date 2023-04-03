Modify the `get_refresh_token.py` script to do all this for us, adding the scope and all. Have it accept a default `client_secrets.json` file (no scopes manually added) and have it add the scopes needed to that file before running the credentials flow.

For your reference, here's the existing get_refresh_token.py:

```
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

if __name__ == "__main__":
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes)
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
```

