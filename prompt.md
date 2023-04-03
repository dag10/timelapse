Let's create a new file called youtube.py. I'd like it to have at least one top level function:
```
def upload_to_youtube( path, title ):
```

Also, if the script is executed directly, it should call that function passing in the launch arg as the `path` parameter.

This function should upload the video at the `path` to youtube.
- It should be Unlisted by default
- It should have the title passed in to the function as `title`
- Be fairly verbose with the upload, and any tools it calls out to should be fairly verbose if possible.

Any credentials needed to perform this upload should be read out of a file called `config.json`. Give me an example config.json too.
