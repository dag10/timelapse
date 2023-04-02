import argparse
import datetime
import os
import re
import subprocess
import sys

def get_recent_monday():
    today = datetime.date.today()
    return today - datetime.timedelta(days=today.weekday())

parser = argparse.ArgumentParser(description="Create timelapse from webcam photos")
parser.add_argument("--date", type=str, default=get_recent_monday().strftime("%Y-%m-%d"), help="First date to copy photos from (default: most recent Monday)")
parser.add_argument("--days", type=int, default=5, help="Number of days from the --date to copy photos from, inclusive (default: 5)")
parser.add_argument("--start", type=str, required=True, help="Time of the first photo to copy for each day, inclusive (24hr format)")
parser.add_argument("--end", type=str, required=True, help="Time of the last photo to copy for each day, inclusive (24hr format)")
parser.add_argument("--no-video", action="store_true", help="Don't create timelapse video")
parser.add_argument("--no-copy", action="store_true", help="Don't transfer files, assume they're already transferred")
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
    src_dir = f"/Volumes/DrewHA/Webcam/{date_str}"

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
    # Create timelapse using ffmpeg
    video_filename = f"timelapse_{os.path.basename(dest_dir)}.mov"
    video_path = os.path.join(dest_dir, video_filename)

    ffmpeg_cmd = [
        "ffmpeg", "-y", "-pattern_type", "glob", "-i", f"{stills_dir}/01_*.jpg",
        "-s", "1920x1080", "-r", "60", "-c:v", "libx264", "-preset", "slow",
        "-crf", "18", "-pix_fmt", "yuv420p", video_path
    ]

    print(f"Running ffmpeg: {' '.join(ffmpeg_cmd)}")
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    print(f"Timelapse video created: {video_path}")

