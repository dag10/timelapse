Now let's make some more changes to youtube.py.

For uploading a youtube thumbnail, is that doable from the upload_to_youtube function? e.g.
```
def upload_to_youtube(video_path, title, thumbnail_path=None):
```

If so, add the `thumbnail_path` parameter (and support passing that as a launch arg) and have that work. The input file will be a 1080p jpeg, hopefully that's supported by the API.

Oh and one more change, when the script outputs "Video uploaded with ID: {video_id}", have it instead output "Video uploaded: https://youtu.be/{video_id}"
