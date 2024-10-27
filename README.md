# waybar-weather2

A substantially modified version of [waybar-weather](https://git.tjdev.de/thetek/waybar-weather): a simple weather module for Waybar based on data from OpenWeatherMap.

## Usage

### Initial Steps

1. [Install `uv`](https://docs.astral.sh/uv/getting-started/installation/).
2. Obtain a valid API key from the OpenWeatherMap One Call API 3.0. You will be asked for a credit card, but with 1000 API calls per day for free and a reasonable interval set for the widget, being charged for use is highly unlikely.
3. Set an environment variable called `OPEN_WEATHER_API_KEY` to your API key.
4. Set environment variables `LATITUDE` and `LONGITUDE` to your desired values.

### Waybar Integration

To integrate the weather widget with Waybar, create a custom module:

```json
"custom/weather": {
  "exec": "~/.config/waybar/weather.py waybar",
  "restart-interval": 900,
  "return-type": "json",
},
```

Remember to change the path to the `weather.py` script specified within the `exec` field.

Then, include the `custom/weather` module in your desired module list.

By default, the module will display the current weather category and temperature in the bar. When hovering the mouse over the widget, a tooltip will pop up with detailed information about the current weather and a forecast for the next week.

The colors used within the widget and tooltip may be changed in the
`weather.py` script in order to match your colorscheme.

## Acknowledgment

Many thanks to [thetek](https://git.tjdev.de/thetek) for writing a clear and comprehensible script, which served as a fantastic starting point for this project. The colorization via pango markup and ANSI escape codes and the human-readable wind direction code, -- that is, the good looks of this project -- are all taken from the original script linked to above.
