# Construction Timelapse Generator

Construction Timelapse Generator is a Python script that creates timelapse videos from a series of webcam photos taken at specified intervals. The script handles copying photos from a source directory, processing them, and creating a high-quality timelapse video using the powerful ffmpeg library.

## Features

- Automatically calculates sunrise and sunset times for each day based on the date
- Allows custom start and end times for each day
- Supports multiple days of photos
- Generates a 1080p, 60fps H.264 video

## Requirements

- Python 3
- ffmpeg
- rsync

## Installation

1. Clone the repository or download the script to your local machine.

```
git clone https://github.com/dag10/construction-timelapse-generator.git
```


2. Make sure you have Python 3, ffmpeg, and rsync installed on your system.

3. Create a virtual environment and activate it:

```
python3 -m venv venv
source venv/bin/activate
```

4. Install the required dependencies:

```
pip3 install -r requirements.txt
```

## Usage

1. Edit the script to set the source directory where your webcam photos are stored.

2. Run the script with the desired options:

```
python3 timelapse.py --date 2023-03-27 --days 1 --start 07:30 --end 19:30
```

### Command-line arguments

| Argument   | Description | Default | Format |
|------------|-------------|---------|--------|
| `--date`   | The first date to copy photos from | most recent Monday | `YYYY-MM-DD` |
| `--days`   | The number of days from the `--date` to copy photos from, inclusive | 5 | integer |
| `--start`  | The time of the first photo to copy for each day, inclusive | one hour before sunrise | 24hr format |
| `--end`    | The time of the last photo to copy for each day, inclusive | one hour after sunset | 24hr format |
| `--no-video` | If set, the script will only transfer files and not create a timelapse video | N/A | flag |
| `--no-copy`  | If set, the script will not transfer files, assuming they're already transferred | N/A | flag |

