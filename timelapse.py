#!/usr/bin/env python3
import argparse
import os
from datetime import datetime, timedelta
import subprocess
import re

# Define command line arguments
parser = argparse.ArgumentParser(description="Create timelapse from webcam photos.")
parser.add_argument("--date", type=str, help="First date to copy photos from in YYYY-MM-DD format. Default: most recent Monday.")
parser.add_argument("--days", type=int, default=5, help="Number of days from the --date to copy photos from, inclusive. Default: 5")
parser.add_argument("--start", type=str, required=True, help="Time of the first photo to copy for each day in HH:MM (24hr time), inclusive.")
parser.add_argument("--end", type=str, required=True, help="Time of the last photo to copy for each day in HH:MM (24hr time), inclusive.")

args = parser.parse_args()

# Determine start date
if args.date:
    start_date = datetime.strptime(args.date, "%Y-%m-%d")
else:
    today = datetime.now()
    start_date = today - timedelta(days=today.weekday())  # Most recent Monday

# Create destination directory
dest_dir = os.path.join(os.getcwd(), f"{start_date.strftime('%Y_%m_%d')}-{(start_date + timedelta(days=args.days - 1)).strftime('%Y_%m_%d')}")
os.makedirs(dest_dir, exist_ok=True)

print(f"Destination directory: {dest_dir}")

total_files_transferred = 0

# Iterate through days and sync photos
for i in range(args.days):
    date = start_date + timedelta(days=i)
    date_str = date.strftime("%Y-%m-%d")
    src_dir = f"/Volumes/DrewHA/Webcam/{date_str}"

    start_time = datetime.strptime(args.start, "%H:%M")
    end_time = datetime.strptime(args.end, "%H:%M")

    # Generate list of include patterns for each minute within the desired time range
    current_time = start_time
    include_patterns = []
    while current_time <= end_time:
        include_pattern = f"01_{date_str}_{current_time.strftime('%H-%M')}-??.jpg"
        include_patterns.extend(["--include", include_pattern])
        current_time += timedelta(minutes=1)

    rsync_cmd = [
        "rsync",
        "-avm",
        *include_patterns,
        "--exclude", "*",
        src_dir + "/",  # Add trailing slash to sync files within directory
        dest_dir
    ]

    print(f"Source directory: {src_dir}")
    print(f"Rsync command: {' '.join(rsync_cmd)}")
    print(f"Syncing photos for {date_str} between {args.start} and {args.end}")
    result = subprocess.run(rsync_cmd, capture_output=True, text=True)
    print(result.stdout)

    # Parse the output to get the number of transferred files
    transferred_files = len(re.findall(r"01_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}.jpg", result.stdout))
    total_files_transferred += transferred_files
    print(f"Transferred {transferred_files} files for {date_str}")

print(f"Total files transferred: {total_files_transferred}")

