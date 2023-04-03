import argparse
import json
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload

def get_credentials():
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    credentials = Credentials.from_authorized_user_info(info=config)
    return credentials

def upload_to_youtube(video_path, title, thumbnail_path=None, playlist_id=None):
    credentials = get_credentials()
    youtube = build("youtube", "v3", credentials=credentials)

    body = {
        "snippet": {
            "title": title,
            "description": "",
            "tags": [],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "unlisted"
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/*")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if response is not None:
            if "id" in response:
                print(f"Video uploaded: https://youtu.be/{response['id']}")
            else:
                print("The upload failed with an unexpected response: %s" % response)
        else:
            print("Upload failed with status %s" % status)

    if thumbnail_path:
        video_id = response["id"]
        media = MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
        youtube.thumbnails().set(videoId=video_id, media_body=media).execute()

    if playlist_id:
        video_id = response["id"]
        body = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
        youtube.playlistItems().insert(part="snippet", body=body).execute()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a video to YouTube")
    parser.add_argument("path", help="Path to the video file")
    parser.add_argument("title", help="Title of the video")
    parser.add_argument("--thumbnail", help="Path to the thumbnail image (optional)", default=None)
    parser.add_argument("--playlist", help="Playlist ID to add the video to (optional)", default=None)
    args = parser.parse_args()

    upload_to_youtube(args.path, args.title, args.thumbnail, args.playlist)

