import argparse
import datetime
import os
import re
import subprocess
import sys
import tempfile
import atexit
import urllib
from sun import calculate_sunrise, calculate_sunset
from youtube import upload_to_youtube
from googleapiclient.errors import ResumableUploadError

# Constants
DEST_STILLS_CONTAINER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stills")
DEST_VIDEO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos")
PLAYLIST_ID = "PLnZFyIYD4hEnHwQw7_4GVGhtO-Qk8iXtt"
VIDEO_TITLE_FORMAT = "{start_date} - {end_date} Construction Timelapse"
SMB_MOUNT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mount")
SMB_HOSTS = {
    'homeassistant': {'user': 'drewbox', 'address': 'homeassistant.local', 'path': 'Share/motioneye/kaye/'},
    'drewbox': {'user': '', 'address': 'drewbox', 'path': 'Home Assistant/Clone/DrewHA/Webcam/'},
}
SMB_HOST = SMB_HOSTS['drewbox']

def unmount():
    if os.path.isdir(SMB_MOUNT_DIR):
        try:
            umount_result = subprocess.run(['diskutil', 'unmount', 'force', SMB_MOUNT_DIR], capture_output=True)
        except Exception as e:
            pass
        try:
            os.rmdir(SMB_MOUNT_DIR)
        except Exception as e:
            msg = ""
            msg += (
                "Failed to rmdir the mount dir. Did it fail to unmount?\n"
                "The output from {} was:".format(umount_result.args) )
            if umount_result.stdout:
                msg += "\n" + umount_result.stdout.decode()
            if umount_result.stderr:
                msg += "\n" + umount_result.stderr.decode()
            raise Exception(msg)
    get_webcam_dir._mounted_webcam_dir = None
unmount.registered = False

def get_webcam_dir():
    """Mounts (if needed) and returns the dir to the NAS Webcam photos."""
    if get_webcam_dir._mounted_webcam_dir:
        return get_webcam_dir._mounted_webcam_dir

    if not unmount.registered:
        atexit.register(unmount)
        unmount.registered = True

    if os.path.isdir(SMB_MOUNT_DIR):
        unmount()
    
    os.mkdir(SMB_MOUNT_DIR)

    smb_path_parts = os.path.normpath(SMB_HOST['path']).split('/')
    smb_user = SMB_HOST['user']
    smb_url = f"//{smb_user + '@' if smb_user else ''}{SMB_HOST['address']}/{urllib.parse.quote(smb_path_parts[0])}"
    subprocess.run(['mount_smbfs', smb_url, SMB_MOUNT_DIR], check=True, timeout=10)

    webcam_dir = os.path.join(SMB_MOUNT_DIR, *smb_path_parts[1:])
    if not os.path.isdir(webcam_dir):
        raise Exception(f"Mounted NAS, but directory could not be found at \"{SMB_HOST['path']}\"")

    get_webcam_dir._mounted_webcam_dir = webcam_dir
    return get_webcam_dir._mounted_webcam_dir
get_webcam_dir._mounted_webcam_dir = None

# dir = get_webcam_dir()
# print('dir:', dir)
# print('list:', os.listdir(dir)[:10])
# input('...')
# sys.exit(0)

def datetime_range(start, end, delta):
    current = start
    while current <= end:
        yield current
        current += delta

def get_recent_monday():
    today = datetime.date.today()
    weekday = today.weekday()
    if weekday >= 4:  # It's Friday, Saturday or Sunday
        return today - datetime.timedelta(days=weekday)
    else:
        return today - datetime.timedelta(days=weekday + 7)

def confirm(prompt):
    while True:
        response = input(prompt).lower()
        if response in ["y", "yes", ""]:
            return True
        elif response in ["n", "no"]:
            return False

parser = argparse.ArgumentParser(description="Create timelapse from webcam photos")
parser.add_argument("--date", type=str, default=get_recent_monday().strftime("%Y-%m-%d"), help="First date to copy photos from (default: most recent Monday)")
parser.add_argument("--days", type=int, default=min((datetime.date.today() - get_recent_monday()).days + 1, 7), help="Number of days from the --date to copy photos from, inclusive (default: full days between the --date and today, with a maximum of 7)")
parser.add_argument("--start", type=str, help="Time of the first photo to copy for each day, inclusive (24hr format)")
parser.add_argument("--end", type=str, help="Time of the last photo to copy for each day, inclusive (24hr format)")
parser.add_argument("--no-video", action="store_true", help="Don't create timelapse video")
parser.add_argument("--no-copy", action="store_true", help="Don't transfer files, assume they're already transferred")
parser.add_argument("--no-upload", action="store_true", help="Don't upload the video to YouTube")
parser.add_argument("--interval", type=int, default=1, help="Interval between photos in minutes (default: 1)")
parser.add_argument("--darkness-minutes", type=int, default=60, help="Amount of minutes we should start each day's timelapse before sunrise and after sunset (default: 60)")
args = parser.parse_args()

start_date = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()
end_date = start_date + datetime.timedelta(days=args.days - 1)
date_range = f"{start_date.strftime('%Y_%m_%d')}-{end_date.strftime('%Y_%m_%d')}"

print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

dst_stills_dir = os.path.join(DEST_STILLS_CONTAINER_DIR, date_range)

if __name__ == "__main__":

    if not os.path.exists(DEST_VIDEO_DIR):
        os.makedirs(DEST_VIDEO_DIR)
    if not os.path.exists(dst_stills_dir):
        os.makedirs(dst_stills_dir)

    print(f"Destination directory: {DEST_VIDEO_DIR}")

    time_first_day_start = args.start
    time_first_day_end = args.end

    total_files_transferred = 0
    for i in range(args.days):
        date = start_date + datetime.timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        src_dir = f"{get_webcam_dir()}/{date_str}"

        time_start = args.start
        time_end = args.end

        if not time_start:
            sunrise = calculate_sunrise(date)
            sunrise_time = datetime.datetime.strptime(sunrise, "%H:%M")
            time_start = (sunrise_time - datetime.timedelta(minutes=args.darkness_minutes)).strftime("%H:%M")
        if not time_end:
            sunset = calculate_sunset(date)
            sunset_time = datetime.datetime.strptime(sunset, "%H:%M")
            time_end = (sunset_time + datetime.timedelta(minutes=args.darkness_minutes)).strftime("%H:%M")

        if not time_first_day_start:
            time_first_day_start = time_start
        if not time_first_day_end:
            time_first_day_end = time_end

        if not args.no_copy:
            print(f"Syncing photos for {date_str} between {time_start} and {time_end}")

            include_patterns = [f"01_{date_str}_{t.hour:02d}-{t.minute:02d}-??.jpg" for t in datetime_range(datetime.datetime.strptime(time_start, "%H:%M"), datetime.datetime.strptime(time_end, "%H:%M"), datetime.timedelta(minutes=args.interval))]
            include_args = [f"--include={pattern}" for pattern in include_patterns]

            rsync_cmd = ["rsync", "-av", "--no-relative", *include_args, "--exclude=*", f"{src_dir}/", dst_stills_dir]
            # print(f"Running rsync: {' '.join(rsync_cmd)}")
            # print(f"A few files in the dir:", os.listdir(src_dir)[:10])
            # sys.exit(0)
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
    video_filename = f"timelapse_{date_range}.mov"
    video_path = os.path.join(DEST_VIDEO_DIR, video_filename)

    if not args.no_video:
        # Read and sort the filenames
        input_files = sorted(os.listdir(dst_stills_dir))

        # Create a temporary file with the sorted filenames
        with tempfile.NamedTemporaryFile("w", delete=False) as temp_file:
            for file in input_files:
                temp_file.write(f"file '{os.path.join(dst_stills_dir, file)}'\n")

        ffmpeg_cmd = [
            "ffmpeg", "-y", "-r", "60", "-f", "image2", "-s", "1920x1080", "-i", f"{dst_stills_dir}/%*.jpg",
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
            first_day_midpoint = (datetime.datetime.combine(datetime.date.today(), datetime.datetime.strptime(time_first_day_start, "%H:%M").time()) + (datetime.datetime.strptime(time_first_day_end, "%H:%M") - datetime.datetime.strptime(time_first_day_start, "%H:%M")) // 2).time()
            thumbnail_filename = f"01_{start_date.strftime('%Y-%m-%d')}_{first_day_midpoint.hour:02d}-{first_day_midpoint.minute:02d}-00.jpg"
            thumbnail_path = os.path.join(dst_stills_dir, thumbnail_filename)

            # Check if the chosen thumbnail file exists, and if not, choose the earliest photo in the stills directory
            if not os.path.exists(thumbnail_path):
                earliest_photo = sorted(os.listdir(dst_stills_dir))[0]
                thumbnail_path = os.path.join(dst_stills_dir, earliest_photo)

            print(f"Using thumbnail: {thumbnail_path}")

            # Upload the video to YouTube
            video_title = VIDEO_TITLE_FORMAT.format(start_date=start_date.strftime("%Y.%m.%d"), end_date=end_date.strftime("%Y.%m.%d"))
            print(f"Uploading video to YouTube with title: {video_title}")
            try:
                video_id = upload_to_youtube(video_path, video_title, thumbnail_path, PLAYLIST_ID)
            except ResumableUploadError as e:
                print(f"Failed to upload video due to error: {e}")
                sys.exit(1)

            if video_id:
                print(f"Video uploaded successfully. Video ID: {video_id}")
            else:
                print("Failed to upload video.", file=sys.stderr)
                sys.exit(1)

