Error:

```
(venv) drew@drew Timelapse % python3 timelapse.py --days 2 --date 2023-02-10 --start 10:20 --end 10:50
Destination directory: /Users/drew/Projects/Timelapse/2023_02_10-2023_02_11
Syncing photos for 2023-02-10 between 10:20 and 10:50
Running rsync: rsync -av --no-relative --include=01_2023-02-10_10-20-??.jpg --include=01_2023-02-10_10-21-??.jpg --include=01_2023-02-10_10-22-??.jpg --include=01_2023-02-10_10-23-??.jpg --include=01_2023-02-10_10-24-??.jpg --include=01_2023-02-10_10-25-??.jpg --include=01_2023-02-10_10-26-??.jpg --include=01_2023-02-10_10-27-??.jpg --include=01_2023-02-10_10-28-??.jpg --include=01_2023-02-10_10-29-??.jpg --include=01_2023-02-10_10-30-??.jpg --include=01_2023-02-10_10-31-??.jpg --include=01_2023-02-10_10-32-??.jpg --include=01_2023-02-10_10-33-??.jpg --include=01_2023-02-10_10-34-??.jpg --include=01_2023-02-10_10-35-??.jpg --include=01_2023-02-10_10-36-??.jpg --include=01_2023-02-10_10-37-??.jpg --include=01_2023-02-10_10-38-??.jpg --include=01_2023-02-10_10-39-??.jpg --include=01_2023-02-10_10-40-??.jpg --include=01_2023-02-10_10-41-??.jpg --include=01_2023-02-10_10-42-??.jpg --include=01_2023-02-10_10-43-??.jpg --include=01_2023-02-10_10-44-??.jpg --include=01_2023-02-10_10-45-??.jpg --include=01_2023-02-10_10-46-??.jpg --include=01_2023-02-10_10-47-??.jpg --include=01_2023-02-10_10-48-??.jpg --include=01_2023-02-10_10-49-??.jpg --include=01_2023-02-10_10-50-??.jpg --exclude=* /Volumes/DrewHA/Webcam/2023-02-10/ /Users/drew/Projects/Timelapse/2023_02_10-2023_02_11/stills
Transferred 31 files for 2023-02-10
Syncing photos for 2023-02-11 between 10:20 and 10:50
Running rsync: rsync -av --no-relative --include=01_2023-02-11_10-20-??.jpg --include=01_2023-02-11_10-21-??.jpg --include=01_2023-02-11_10-22-??.jpg --include=01_2023-02-11_10-23-??.jpg --include=01_2023-02-11_10-24-??.jpg --include=01_2023-02-11_10-25-??.jpg --include=01_2023-02-11_10-26-??.jpg --include=01_2023-02-11_10-27-??.jpg --include=01_2023-02-11_10-28-??.jpg --include=01_2023-02-11_10-29-??.jpg --include=01_2023-02-11_10-30-??.jpg --include=01_2023-02-11_10-31-??.jpg --include=01_2023-02-11_10-32-??.jpg --include=01_2023-02-11_10-33-??.jpg --include=01_2023-02-11_10-34-??.jpg --include=01_2023-02-11_10-35-??.jpg --include=01_2023-02-11_10-36-??.jpg --include=01_2023-02-11_10-37-??.jpg --include=01_2023-02-11_10-38-??.jpg --include=01_2023-02-11_10-39-??.jpg --include=01_2023-02-11_10-40-??.jpg --include=01_2023-02-11_10-41-??.jpg --include=01_2023-02-11_10-42-??.jpg --include=01_2023-02-11_10-43-??.jpg --include=01_2023-02-11_10-44-??.jpg --include=01_2023-02-11_10-45-??.jpg --include=01_2023-02-11_10-46-??.jpg --include=01_2023-02-11_10-47-??.jpg --include=01_2023-02-11_10-48-??.jpg --include=01_2023-02-11_10-49-??.jpg --include=01_2023-02-11_10-50-??.jpg --exclude=* /Volumes/DrewHA/Webcam/2023-02-11/ /Users/drew/Projects/Timelapse/2023_02_10-2023_02_11/stills
Transferred 31 files for 2023-02-11
Total files transferred: 62
Running ffmpeg: ffmpeg -y -r 60 -f image2 -s 1920x1080 -i /Users/drew/Projects/Timelapse/2023_02_10-2023_02_11/stills/%*.jpg -c:v libx264 -crf 18 -pix_fmt yuv420p /Users/drew/Projects/Timelapse/2023_02_10-2023_02_11/timelapse_2023_02_10-2023_02_11.mov
Timelapse video created: /Users/drew/Projects/Timelapse/2023_02_10-2023_02_11/timelapse_2023_02_10-2023_02_11.mov
Do you want to upload the video to YouTube? [Y/n]:
Traceback (most recent call last):
  File "/Users/drew/Projects/Timelapse/timelapse.py", line 126, in <module>
    first_day_midpoint = (datetime.datetime.strptime(args.start, "%H:%M") + datetime.datetime.strptime(args.end, "%H:%M")) // 2
                          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TypeError: unsupported operand type(s) for +: 'datetime.datetime' and 'datetime.datetime'
```

How do we fix it? Also outdent everything after `if not args.no_upload:` so that we can still upload even with `--no-video`.

