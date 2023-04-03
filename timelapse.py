import argparse
import datetime
import os
import re
import subprocess
import sys
import tempfile
from sun import calculate_sunrise, calculate_sunset
from youtube import upload_to_youtube
from googleapiclient.errors import ResumableUploadError

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
parser.add_argument("--interval", type=int, default=1, help="Interval, in minutes, between frames to copy over (default: 1)")
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

    interval_minutes = args.interval
    include_patterns = [f"01_{date_str}_{t.hour:02d}-{t.minute:02d}-??.jpg" for t in datetime_range(datetime.datetime.strptime(args.start, "%H:%M"), datetime.datetime.strptime(args.end, "%H:%M"), datetime.timedelta(minutes=interval_minutes))]
    include_args = [f"--include={pattern}" for pattern in include_patterns]

    rsync_cmd = ["rsync", "-av", "--no-relative", *include_args, "--exclude=*", f"{src_dir}/", stills_dir]
    #print(f"Running rsync: {' '.join(rsync_cmd)}")
    result = subprocess.run(rsync_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    # Parse the output to get the number of transferred files
    transferred_files = len(re.findall(r"01_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}.jpg", result.stdout))
    total_files_transferred += transferred_files
    print(f"Transferred {transferred_files} files for {date_str}")

print(f"Total files transferred: {total_files_transferred}")

# Create timelapse using ffmpeg
video_filename = f"timelapse_{os.path.basename(dest_dir)}.mov"
video_path = os.path.join(dest_dir, video_filename)

if not args.no_video:
    # Read and sort the filenames
    input_files = sorted(os.listdir(stills_dir))

    # Create a temporary file with the sorted filenames
    with tempfile.NamedTemporaryFile("w", delete=False) as temp_file:
        for file in input_files:
            temp_file.write(f"file '{os.path.join(stills_dir, file)}'\n")

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
        first_day_midpoint_aligned = datetime.datetime.combine(datetime.date.today(), datetime.time(first_day_midpoint.hour // args.interval * args.interval))
        thumbnail_pattern = f"01_{date_list[0].strftime('%Y-%m-%d')}_{first_day_midpoint_aligned.hour:02d}-{first_day_midpoint_aligned.minute:02d}-??.jpg"
        thumbnail_file = glob.glob(os.path.join(stills_dir, thumbnail_pattern))[0]

        # Upload the video to YouTube
        youtube_upload_cmd = [
            "youtube-upload",
            "--title", f"Timelapse {os.path.basename(dest_dir)}",
            "--description", f"Timelapse of {os.path.basename(dest_dir)} from {date_list[0].strftime('%Y-%m-%d')} to {date_list[-1].strftime('%Y-%m-%d')}",
            "--category", "28",
            "--tags", "timelapse, weather",
            "--privacy", "private",
            "--thumbnail", thumbnail_file,
            video_path
        ]

        print(f"Uploading video to YouTube: {' '.join(youtube_upload_cmd)}")
        result = subprocess.run(youtube_upload_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error: {result.stderr}", file=sys.stderr)
            sys.exit(1)

        print("Video uploaded to YouTube")

sys.exit(0)

