This logic is wrong, can you fix it?

```
def get_recent_monday():
    today = datetime.date.today()
    weekday = today.weekday()
    if weekday >= 4:  # It's Friday, Saturday or Sunday
        return today - datetime.timedelta(days=(weekday - 4))
    else:  # It's Monday through Thursday
        return today - datetime.timedelta(days=(weekday + 3 + 7))
```
