import argparse
import json
import os
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

def upload_to_youtube(path, title):
    """Upload the video at the given path to YouTube with the given title."""
    credentials = get_credentials()
    youtube = build("youtube", "v3", credentials=credentials)
    try:
        video_id = upload_video(youtube, path, title)
        print(f"Video uploaded with ID: {video_id}")
    except HttpError as e:
        print(f"An error occurred: {e}")
        video_id = None

    return video_id

def get_credentials():
    """Load credentials from the config.json file."""
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(info=config)
    return credentials

def upload_video(youtube, path, title):
    """Upload the video to YouTube and return the video ID."""
    body = {
        "snippet": {
            "title": title,
            "description": "",
            "tags": [],
            "categoryId": "22"  # People & Blogs
        },
        "status": {
            "privacyStatus": "unlisted"
        }
    }

    media = MediaFileUpload(path, mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        print("Uploading video...")
        _, response = request.next_chunk()
        print("Video uploaded.")

    return response["id"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a video to YouTube")
    parser.add_argument("path", type=str, help="Path to the video file")
    parser.add_argument("title", type=str, help="Title for the video on YouTube")
    args = parser.parse_args()

    upload_to_youtube(args.path, args.title)

