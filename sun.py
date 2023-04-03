import argparse
import datetime
from suntime import Sun, SunTimeException
import pytz

latitude = 47.6062
longitude = -122.3321

def calculate_sunrise(date):
    sun = Sun(latitude, longitude)
    local_timezone = pytz.timezone("America/Los_Angeles")
    sunrise = sun.get_local_sunrise_time(date).astimezone(local_timezone)
    return sunrise.strftime("%H:%M")


def calculate_sunset(date):
    sun = Sun(latitude, longitude)
    local_timezone = pytz.timezone("America/Los_Angeles")
    sunset = sun.get_local_sunset_time(date).astimezone(local_timezone)
    return sunset.strftime("%H:%M")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate sunrise and sunset times for Seattle")
    parser.add_argument("date", type=str, help="Date in format YYYY-MM-DD")

    args = parser.parse_args()
    date = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()

    sunrise = calculate_sunrise(date)
    sunset = calculate_sunset(date)

    print(f"Sunrise: {sunrise}")
    print(f"Sunset: {sunset}")

