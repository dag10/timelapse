#!/usr/bin/env python3
import argparse
import os
from datetime import datetime, timedelta
import subprocess

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

# Iterate through days and sync photos
for i in range(args.days):
    date = start_date + timedelta(days=i)
    date_str = date.strftime("%Y-%m-%d")
    src_dir = f"/Volumes/DrewHA/Webcam/{date_str}"

    start_time = datetime.strptime(args.start, "%H:%M").time()
    end_time = datetime.strptime(args.end, "%H:%M").time()

    include_pattern = f"01_{date_str}_{start_time.strftime('%H-%M')}-?-*..{end_time.strftime('%H-%M')}-?-*.jpg"
    exclude_pattern = "*"

    rsync_cmd = [
        "rsync",
        "-avm",
        "--include", include_pattern,
        "--exclude", exclude_pattern,
        src_dir + "/",  # Add trailing slash to sync files within directory
        dest_dir
    ]

    subprocess.run(rsync_cmd)

