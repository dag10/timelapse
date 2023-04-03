It all works! The video was uploaded, with the correct thumbnail, and added to the playlist. Thanks!

Some final changes to youtube.py:
- When we print out the uploaded video URL, if we also opted to add it to a playlist, print out the playlist URL as well. Example: "Added to playlist: https://www.youtube.com/playlist?list=PLnZFyIYD4hEnHwQw7_4GVGhtO-Qk8iXtt"
- The `upload_to_youtube` function needs to return the video_id; the timelapse.py script expects this.

For reference, here's the current youtube.py:

```
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
```

Also for your reference, here's the latest timelapse.py:

```
import argparse
import datetime
import os
import re
import subprocess
import sys
import tempfile
from sun import calculate_sunrise, calculate_sunset
from youtube import upload_to_youtube

# Constants
BASE_DIR = "/Volumes/DrewHA/Webcam/"
PLAYLIST_ID = "PLnZFyIYD4hEnHwQw7_4GVGhtO-Qk8iXtt"
VIDEO_TITLE_FORMAT = "{start_date} - {end_date} Construction Timelapse"

def datetime_range(start, end, delta):
    current = start
    while current <= end:
        yield current
        current += delta

def get_recent_monday():
    today = datetime.date.today()
    return today - datetime.timedelta(days=today.weekday())

def confirm(prompt):
    while True:
        response = input(prompt).lower()
        if response in ["y", "yes", ""]:
            return True
        elif response in ["n", "no"]:
            return False

parser = argparse.ArgumentParser(description="Create timelapse from webcam photos")
parser.add_argument("--date", type=str, default=get_recent_monday().strftime("%Y-%m-%d"), help="First date to copy photos from (default: most recent Monday)")
parser.add_argument("--days", type=int, default=5, help="Number of days from the --date to copy photos from, inclusive (default: 5)")
parser.add_argument("--start", type=str, help="Time of the first photo to copy for each day, inclusive (24hr format)")
parser.add_argument("--end", type=str, help="Time of the last photo to copy for each day, inclusive (24hr format)")
parser.add_argument("--no-video", action="store_true", help="Don't create timelapse video")
parser.add_argument("--no-copy", action="store_true", help="Don't transfer files, assume they're already transferred")
parser.add_argument("--no-upload", action="store_true", help="Don't upload the video to YouTube")
args = parser.parse_args()

start_date = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()
end_date = start_date + datetime.timedelta(days=args.days - 1)
dest_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{start_date.strftime('%Y_%m_%d')}-{end_date.strftime('%Y_%m_%d')}")
stills_dir = os.path.join(dest_dir, "stills")

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
if not os.path.exists(stills_dir):
    os.makedirs(stills_dir)

print(f"Destination directory: {dest_dir}")

total_files_transferred = 0
for i in range(args.days):
    date = start_date + datetime.timedelta(days=i)
    date_str = date.strftime("%Y-%m-%d")
    src_dir = f"{BASE_DIR}{date_str}"

    if not args.start:
        sunrise = calculate_sunrise(date)
        sunrise_time = datetime.datetime.strptime(sunrise, "%H:%M")
        args.start = (sunrise_time - datetime.timedelta(hours=1)).strftime("%H:%M")
    if not args.end:
        sunset = calculate_sunset(date)
        sunset_time = datetime.datetime.strptime(sunset, "%H:%M")
        args.end = (sunset_time + datetime.timedelta(hours=1)).strftime("%H:%M")

    if not args.no_copy:
        print(f"Syncing photos for {date_str} between {args.start} and {args.end}")

        include_patterns = [f"01_{date_str}_{t.hour:02d}-{t.minute:02d}-??.jpg" for t in datetime_range(datetime.datetime.strptime(args.start, "%H:%M"), datetime.datetime.strptime(args.end, "%H:%M"), datetime.timedelta(minutes=1))]
        include_args = [f"--include={pattern}" for pattern in include_patterns]

        rsync_cmd = ["rsync", "-av", "--no-relative", *include_args, "--exclude=*", f"{src_dir}/", stills_dir]
        print(f"Running rsync: {' '.join(rsync_cmd)}")
        result = subprocess.run(rsync_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error: {result.stderr}", file=sys.stderr)
            sys.exit(1)

        # Parse the output to get the number of transferred files
        transferred_files = len(re.findall(r"01_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}.jpg", result.stdout))
        total_files_transferred += transferred_files
        print(f"Transferred {transferred_files} files for {date_str}")

print(f"Total files transferred: {total_files_transferred}")

if not args.no_video:
    # Read and sort the filenames
    input_files = sorted(os.listdir(stills_dir))

    # Create a temporary file with the sorted filenames
    with tempfile.NamedTemporaryFile("w", delete=False) as temp_file:
        for file in input_files:
            temp_file.write(f"file '{os.path.join(stills_dir, file)}'\n")

    # Create timelapse using ffmpeg
    video_filename = f"timelapse_{os.path.basename(dest_dir)}.mov"
    video_path = os.path.join(dest_dir, video_filename)

    ffmpeg_cmd = [
        "ffmpeg", "-y", "-r", "60", "-f", "image2", "-s", "1920x1080", "-i", f"{stills_dir}/%*.jpg",
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", video_path
    ]

    print(f"Running ffmpeg: {' '.join(ffmpeg_cmd)}")
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    print(f"Timelapse video created: {video_path}")

    # Open the video using the system's 'open' command
    open_cmd = ["open", video_path]
    subprocess.run(open_cmd)

if not args.no_upload:
    if confirm("Do you want to upload the video to YouTube? [Y/n]: "):
        # Find thumbnail for the first day's midpoint
        first_day_midpoint = (datetime.datetime.combine(datetime.date.today(), datetime.datetime.strptime(args.start, "%H:%M").time()) + (datetime.datetime.strptime(args.end, "%H:%M") - datetime.datetime.strptime(args.start, "%H:%M")) // 2).time()
        thumbnail_filename = f"01_{start_date.strftime('%Y-%m-%d')}_{first_day_midpoint.hour:02d}-{first_day_midpoint.minute:02d}-00.jpg"
        thumbnail_path = os.path.join(stills_dir, thumbnail_filename)
        print(f"Using thumbnail: {thumbnail_path}")

        # Upload the video to YouTube
        video_title = VIDEO_TITLE_FORMAT.format(start_date=start_date.strftime("%Y.%m.%d"), end_date=end_date.strftime("%Y.%m.%d"))
        print(f"Uploading video to YouTube with title: {video_title}")
        video_id = upload_to_youtube(video_path, video_title, thumbnail_path, PLAYLIST_ID)

        if video_id:
            print(f"Video uploaded successfully. Video ID: {video_id}")
        else:
            print("Failed to upload video.", file=sys.stderr)
            sys.exit(1)
```
