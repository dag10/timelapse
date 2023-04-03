On a recent run, the following happened:

```
(venv) drew@drew Timelapse % python3 timelapse.py --days 2 --date 2023-02-01 --start 9:20 --end 9:50 --no-copy
Destination directory: /Users/drew/Projects/Timelapse/2023_02_01-2023_02_02
Total files transferred: 0
Running ffmpeg: ffmpeg -y -r 60 -f image2 -s 1920x1080 -i /Users/drew/Projects/Timelapse/2023_02_01-2023_02_02/stills/%*.jpg -c:v libx264 -crf 18 -pix_fmt yuv420p /Users/drew/Projects/Timelapse/2023_02_01-2023_02_02/timelapse_2023_02_01-2023_02_02.mov
Timelapse video created: /Users/drew/Projects/Timelapse/2023_02_01-2023_02_02/timelapse_2023_02_01-2023_02_02.mov
Do you want to upload the video to YouTube? [Y/n]:
Using thumbnail: /Users/drew/Projects/Timelapse/2023_02_01-2023_02_02/stills/01_2023-02-01_09-35-00.jpg
Uploading video to YouTube with title: 2023.02.01 - 2023.02.02 Construction Timelapse
Traceback (most recent call last):
  File "/Users/drew/Projects/Timelapse/timelapse.py", line 134, in <module>
    video_id = upload_to_youtube(video_path, video_title, thumbnail_path, PLAYLIST_ID)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/drew/Projects/Timelapse/youtube.py", line 39, in upload_to_youtube
    status, response = request.next_chunk()
                       ^^^^^^^^^^^^^^^^^^^^
  File "/Users/drew/Projects/Timelapse/venv/lib/python3.11/site-packages/googleapiclient/_helpers.py", line 130, in positional_wrapper
    return wrapped(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/drew/Projects/Timelapse/venv/lib/python3.11/site-packages/googleapiclient/http.py", line 1022, in next_chunk
    raise ResumableUploadError(resp, content)
googleapiclient.errors.ResumableUploadError: <HttpError 403 when requesting None returned "The request cannot be completed because you have exceeded your <a href="/youtube/v3/getting-started#quota">quota</a>.". Details: "[{'message': 'The request cannot be completed because you have exceeded your <a href="/youtube/v3/getting-started#quota">quota</a>.', 'domain': 'youtube.quota', 'reason': 'quotaExceeded'}]">
```

As you can see, Google's servers are telling me that I've exceeded a quota. Fine, that's something that we can't fix with code; I can only use their API a certain amount per day and I've hit my limit. However, I'd like this error to be printed in a more readable way when running the command.

Notice that the message is is embedded in a `'message':` field in the error message. In the case we get an error of this format, print the `message` to stdout as a failure reason, instead of a whole stack trace.
