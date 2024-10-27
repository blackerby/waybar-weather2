#!/usr/bin/env -S uv run -q
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
# ]
# ///

import datetime
import json
import os

import requests

# TODO
# - snowfall data
# - weather warnings

### CONSTANTS ###

# api key - get it at https://openweathermap.org/
API_KEY = os.getenv("OPEN_WEATHER_API_KEY")

# latitude and longitude of the city you want to query
LATITUDE = os.getenv("LATITUDE")
LONGITUDE = os.getenv("LONGITUDE")

BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"

# waybar colors
GRAY = "#859289"
DARK = "#5a6772"
GREEN = "#a7c080"
YELLOW = "#dbbc7f"
ORANGE = "#e69875"
RED = "#e67e80"
PURPLE = "#d699b6"
BLUE = "#7fbbb3"


class Weather:
    def __init__(self) -> None:
        self._get_data()
        self._process_current()
        self._process_forecast()

    def _get_data(self):
        url = f"{BASE_URL}?lat={LATITUDE}&lon={LONGITUDE}&appid={API_KEY}&units=imperial&exclude=minutely,hourly"
        try:
            response = requests.get(url)
            self.data = response.json()
        except Exception as e:
            print(f"Request did not succeed: {e}")
            exit(1)

    @property
    def _current_data(self):
        return self.data["current"]

    @property
    def _forecast_data(self):
        return self.data["daily"]

    def _process_current(self):
        data = self._current_data
        self.weather = data["weather"][0]["description"].lower()
        self.temperature = round(data["temp"], 1)
        self.temperature_felt = round(data["feels_like"], 1)
        self.humidity = data["humidity"]
        self.wind_speed = round(data["wind_speed"], 1)
        self.wind_direction = self._get_wind_direction(data["wind_deg"])
        self.rainfall = data.get("rain", 0)

    def _process_forecast(self):
        data = self._forecast_data

        output = dict()

        for entry in data:
            day = entry["dt"]

            # collect relevant from day for each day
            weather = entry["weather"][0]["description"].lower()
            humidity = entry["humidity"]
            rainfall = entry.get("rain", 0)
            precipitation_prob = entry["pop"]
            wind_speed = entry["wind_speed"]
            weekday = self._get_weekday(day)

            # min and max temperature for the day
            min_temperature = entry["temp"]["min"]
            max_temperature = entry["temp"]["max"]

            output[day] = {
                "min_temperature": min_temperature,
                "max_temperature": max_temperature,
                "weather": weather,
                "humidity": humidity,
                "rainfall": rainfall,
                "precipitation_prob": precipitation_prob,
                "wind_speed": wind_speed,
                "weekday": weekday,
            }

            self._forecast = output

    def _get_wind_direction(self, deg: int) -> str:
        """
        turn a wind direction specified by meteorological degrees into a
        human-readable form

        @param deg: degrees. expected to be in range [0..360]

        @return human-readable form (e.g. 'NE' for `deg == 45`)
        """
        if deg < 22.5:
            return "N"
        if deg < 67.5:
            return "NE"
        if deg < 112.5:
            return "E"
        if deg < 157.5:
            return "SE"
        if deg < 202.5:
            return "S"
        if deg < 247.5:
            return "SW"
        if deg < 292.5:
            return "W"
        if deg < 337.5:
            return "NW"
        else:
            return "N"

    def _get_weekday(self, date: int) -> str:
        """
        get weekday from date

        @param date: date as ISO-8601-formatted string (YYYY-mm-dd)

        @return weekday as lowercase string (e.g. 'monday')
        """
        return datetime.datetime.fromtimestamp(date).strftime("%A").lower()

    def _colorize(self, text: str, color: str) -> str:
        """
        wrap `text` with pango markup to colorize it for usage with waybar.

        @param text: the text to colorize
        @param color: the color as string ('#rrggbb')
        """
        return f'<span foreground="{color}">{text}</span>'

    ### WAYBAR ###

    def _waybar_entry(
        self, label: str, content: str, indent: int = 2, label_width: int = 9
    ):
        """
        create an 'entry' for a waybar tooltip that consists of a label (printed in
        gray) and some content. the labels are automatically filled with whitespace
        to align multiple lines properly.

        @param label:       the label of the line
        @param content:     content, printed after the label
        @param indent:      number of spaces to indent with
        @param label_width: width of label

        @return the entry for use within waybar
        """

        label_with_whitespace = label.ljust(label_width)
        return (
            f'{" " * indent}{self._colorize(label_with_whitespace, GRAY)}  {content}\n'
        )

    def _waybar_widget(self) -> str:
        """
        get the widget component of the waybar output. contains the current weather
        group and temperature.

        @param current weather data

        @return widget component
        """

        weather = self.weather
        temperature = self.temperature

        return f"{self._colorize(weather, DARK)} {temperature}°"

    def _waybar_current(self) -> str:
        """
        get the current weather overview for the tooltip of the waybar output.

        @param current weather data

        @return formatted current weather overview
        """

        # retrieve relevant data
        weather = self.weather
        temperature = self.temperature
        temperature_felt = self.temperature_felt
        humidity = self.humidity
        wind_speed = self.wind_speed
        wind_direction = self.wind_direction
        rainfall = self.rainfall

        # generate output
        output = ""
        output += self._waybar_entry("weather", self._colorize(weather, YELLOW))
        output += self._waybar_entry(
            "temp",
            f'{self._colorize(f"{temperature} °F", ORANGE)}{self._colorize(", feels like ", GRAY)}{self._colorize(f"{temperature_felt} °F", ORANGE)}',
        )
        output += self._waybar_entry(
            "humidity", self._colorize(f"{humidity} % RH", RED)
        )
        output += self._waybar_entry(
            "wind",
            f'{self._colorize(f"{wind_speed} mph", PURPLE)} {self._colorize(f"({wind_direction})", GRAY)}',
        )
        output += self._waybar_entry("rain", self._colorize(f"{rainfall} mm", BLUE))
        return output

    def _waybar_forecast(self) -> str:
        """
        get the daily forecast for the tooltip of the waybar output.

        @param forecast weather data

        @return formatted daily forecast
        """

        output = ""

        daily_data = self._forecast

        for day in sorted(daily_data):
            data = daily_data[day]
            line_content = (
                self._colorize(f'{data["max_temperature"]:2}°', ORANGE)
                + self._colorize(" / ", GRAY)
                + self._colorize(f'{data["min_temperature"]:2}°', ORANGE)
                + self._colorize(", ", GRAY)
                + self._colorize(data["weather"], YELLOW)
            )

            if data["rainfall"] > 0:
                line_content += (
                    self._colorize(": ", GRAY)
                    + self._colorize(f'{data["rainfall"]} mm ', BLUE)
                    + self._colorize(f'({data["precipitation_prob"]}%)', GRAY)
                )

            output += self._waybar_entry(data["weekday"], line_content)

        return output.rstrip()

    def waybar(self):
        """
        get current and forecast weather data and output it formatted in a way that
        allows it to be included as a widget in waybar. only shows weather category
        and temperature in the widget, but reveals detailed weather information and
        a one week forecast in the tooltip.
        """

        widget = self._waybar_widget()
        current = self._waybar_current()
        forecast = self._waybar_forecast()
        tooltip = (
            self._colorize("current weather", GREEN)
            + "\n"
            + current
            + "\n"
            + self._colorize("forecast", GREEN)
            + "\n"
            + forecast
        )

        print(
            json.dumps(
                {
                    "text": widget,
                    "tooltip": tooltip,
                }
            )
        )


### UTILITIES ###


def print_error(msg: str):
    """
    print an error message with appropriate prefix.

    @param str: the message to print
    """
    print("\x1b[90m[\x1b[31merr\x1b[90m]\x1b[0m", msg)


### MAIN ###


def main():
    """
    main function
    """

    # constants not set
    if API_KEY is None or LATITUDE is None or LONGITUDE is None:
        print_error(
            "please set required API key and latitude and longitude environment variables"
        )
    else:
        weather = Weather()
        weather.waybar()


if __name__ == "__main__":
    main()
