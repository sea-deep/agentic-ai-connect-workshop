"""Tool definitions and schemas for the agent."""
import json
import urllib.request
import urllib.parse

# WMO weather codes mapping to short human descriptions
WMO_WEATHER_CODES = {
    0: "clear sky", 1: "mostly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "depositing rime fog",
    51: "light drizzle", 53: "drizzle", 55: "dense drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain",
    71: "light snow", 73: "snow", 75: "heavy snow",
    80: "light showers", 81: "showers", 82: "violent showers",
    95: "thunderstorm",
}

def get_weather(city: str, forecast_days: int = 1) -> str:
    """
    Geocodes the city, then fetches current conditions from Open-Meteo.
    
    Args:
        city (str): The name of the city to get weather for.
        forecast_days (int, optional): Number of days for the forecast. Defaults to 1.
        
    Returns:
        str: A summary of the weather conditions.
    """
    try:
        geocode_url = "https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode(
            {"name": city, "count": 1}
        )
        with urllib.request.urlopen(geocode_url, timeout=10) as r:
            geocode_result = json.loads(r.read())

        if not geocode_result.get("results"):
            return f"No weather data for {city}"
        place = geocode_result["results"][0]

        forecast_url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(
            {
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,weather_code",
                "daily": "temperature_2m_max,temperature_2m_min,weather_code",
                "forecast_days": forecast_days,
                "timezone": "auto",
            }
        )
        with urllib.request.urlopen(forecast_url, timeout=10) as r:
            forecast_result = json.loads(r.read())

        current = forecast_result["current"]
        condition = WMO_WEATHER_CODES.get(current["weather_code"], "unknown conditions")
        summary = f"Now: {current['temperature_2m']}C, {condition}."

        if forecast_days > 1:
            daily = forecast_result["daily"]
            day_lines = []
            for i, date in enumerate(daily["time"]):
                day_condition = WMO_WEATHER_CODES.get(daily["weather_code"][i], "unknown conditions")
                day_lines.append(
                    f"{date}: high {daily['temperature_2m_max'][i]}C / "
                    f"low {daily['temperature_2m_min'][i]}C, {day_condition}"
                )
            summary += " Forecast: " + "; ".join(day_lines) + "."

        return summary
    except Exception as e:
        return f"Could not fetch weather for {city}: {e}"

def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Converts an amount between currencies using Frankfurter's API.
    
    Args:
        amount (float): The amount to convert.
        from_currency (str): The 3-letter currency code to convert from.
        to_currency (str): The 3-letter currency code to convert to.
        
    Returns:
        str: A string showing the converted amount.
    """
    headers = {"User-Agent": "anatomy-of-ai-agent/1.0 (workshop demo)"}
    url = "https://api.frankfurter.dev/v1/latest?" + urllib.parse.urlencode(
        {"amount": amount, "from": from_currency.upper(), "to": to_currency.upper()}
    )
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        result = json.loads(r.read())
    converted = result["rates"][to_currency.upper()]
    return f"{amount} {from_currency.upper()} = {converted} {to_currency.upper()}"


# Dispatch table: maps the tool name to the actual Python function
AVAILABLE_TOOLS = {
    "get_weather": get_weather,
    "convert_currency": convert_currency,
}

# Tool schemas describing the functions to the model
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": (
                "Get current weather for a city. Pass forecast_days > 1 to also get "
                "that many days of daily forecast, e.g. forecast_days=3 for a 3-day trip."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name, e.g. 'Tokyo'"},
                    "forecast_days": {
                        "type": "integer",
                        "description": "How many days of daily forecast to include (default 1 = current only)",
                    },
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": "Convert an amount from one currency to another using live exchange rates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Amount to convert"},
                    "from_currency": {"type": "string", "description": "3-letter source currency code, e.g. 'USD'"},
                    "to_currency": {"type": "string", "description": "3-letter target currency code, e.g. 'JPY'"},
                },
                "required": ["amount", "from_currency", "to_currency"],
            },
        },
    },
]
