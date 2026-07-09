import discord, requests, datetime
from discord.ext import commands
from discord import app_commands

class Weather(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  def get_weather_emoji(self, status):
    status_lower = status.lower()
    if "thunderstorm" in status_lower:
      return "⛈️"
    elif "heavy thunderstorm" in status_lower:
      return "🌩️"
    elif "rain" in status_lower or "drizzle" in status_lower:
      return "🌧️"
    elif "cloud" in status_lower or "overcast" in status_lower:
      return "☁️"
    elif "clear" in status_lower or "sun" in status_lower:
      return "☀️"
    elif "partly cloudy" in status_lower:
      return "⛅"
    else:
      return ""
  
  @app_commands.command(name="currentweather", description="Check current weather for a city")
  async def currentWeather(self, interaction: discord.Interaction, city: str):
    await interaction.response.defer(ephemeral=False)
    try:
      currentWeatherAPI = f"https://discord-bot-hosting-vft8.onrender.com/api/currentweather/{city}"

      response = requests.get(currentWeatherAPI)
      data = response.json()

      if response.status_code != 200:
        error_data = data
        error_msg = error_data.get("error", "Could not fetch weather data.")
        await interaction.followup.send(f"{error_msg}")
        return
      
      unix_time = data.get("unix_time")
      if isinstance(unix_time, int):
        formattedTime = f"<t:{unix_time}:F>"
      else:
        formattedTime = "N/A"
      
      temp_C = f"{data.get('temp', ''):.1f}"
      feelsLikeTemp_C = f"{data.get('feelsLikeTemp', ''):.1f}"
        
      emoji = self.get_weather_emoji(data.get("type", ""))
      description = data.get("description", "No description").title()

      current_string = (
        f"**{formattedTime}**\n"
        f"{emoji} {description} | "
        f"**{temp_C}°C**\n"
        f"Feels like: **{feelsLikeTemp_C}°C**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      )

      embed = discord.Embed(
        title = f"Current Weather Forecast",
        description = f"📍 {data['location']}\n\n{current_string}",
        color = discord.Color.blurple()
      )

      await interaction.followup.send(embed=embed)
    
    except requests.exceptions.HTTPError as httpErr:
      status = httpErr.response.status_code
      match status:
        case 400: await interaction.followup.send("Error 400 - Bad request: Please check your input")
        case 401: await interaction.followup.send("Error 401 - Unauthorised: Invalid API key")
        case 403: await interaction.followup.send("Error 403 - Forbidden: Access is denied")
        case 404: await interaction.followup.send("Error 404 - Not found: City not found")
        case 500: await interaction.followup.send("Error 500 - Intenal server error: Please try again later")
        case 502: await interaction.followup.send("Error 502 - Bad gateway: Invalid response from the server")
        case 503: await interaction.followup.send("Error 503 - Service unavailable: Server is down")
        case 504: await interaction.followup.send("Error 504 - Gateway timeout: No response from the server")
        case _:await interaction.followup.send(f"HTTP error occured: {httpErr}")

    except requests.exceptions.ConnectionError:
      await interaction.followup.send("Connection Error: Check your internet connection")

    except requests.exceptions.Timeout:
      await interaction.followup.send("Timeout Error: The request timed out")

    except requests.exceptions.TooManyRedirects:
      await interaction.followup.send("Too Many Redirects Error: Check the URL")

    except requests.exceptions.RequestException as reqErr:
      await interaction.followup.send(f"Request Error: {reqErr}")

  @app_commands.command(name="hourlyweather", description="Check hourly weather for a city (Max 25 hours)")
  async def hourlyWeather(self, interaction: discord.Interaction, city: str, hrs: int):
    if hrs < 1:
      await interaction.response.send_message("Must be at least 1 hour", ephemeral=True)
      return
    elif hrs > 25:
      await interaction.response.send_message("Maximum is 25 hrs(1 day), sry :<", ephemeral=True)
      return
    
    await interaction.response.defer(ephemeral=False)
    try:
      hourlyWeatherAPI = f"https://discord-bot-hosting-vft8.onrender.com/api/hourlyweather/{city}?hrs={hrs}"

      response = requests.get(hourlyWeatherAPI)
      data = response.json()

      if response.status_code != 200:
        error_data = data
        error_msg = error_data.get("error", "Could not fetch weather data.")
        await interaction.followup.send(f"{error_msg}")
        return
      
      forecast_lines = []

      for hourData in data.get("forecast", []):
        hrs_24 = hourData.get("hours", "N/A")
        
        if isinstance(hrs_24, int):
          meridiem = "PM" if hrs_24 >= 12 else "AM"
          hrs_12 = hrs_24 % 12
          if hrs_12 == 0:
            hrs_12 = 12
          formattedTime = f"{hrs_12}{meridiem}"
        else:
          formattedTime = "N/A"
        
        temp_C = f"{hourData.get('temp', ''):.1f}"
        feelsLikeTemp_C = f"{hourData.get('feelsLikeTemp', ''):.1f}"
        
        emoji = self.get_weather_emoji(hourData.get("type", ""))
        description = hourData.get("description", "No description").title()

        hour_string = (
          f"**{formattedTime}**\n"
          f"{emoji} {description} | "
          f"**{temp_C}°C**\n"
          f"Feels like: **{feelsLikeTemp_C}°C**\n"
          f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        forecast_lines.append(hour_string)
      
      full_forecast_text = "\n".join(forecast_lines)

      embed = discord.Embed(
        title = f"{hrs} Hour(s) Weather Forecast",
        description = f"📍 {data['location']}\n\n{full_forecast_text}",
        color = discord.Color.blurple()
      )

      await interaction.followup.send(embed=embed)

    except requests.exceptions.HTTPError as httpErr:
      status = httpErr.response.status_code
      match status:
        case 400: await interaction.followup.send("Error 400 - Bad request: Please check your input")
        case 401: await interaction.followup.send("Error 401 - Unauthorised: Invalid API key")
        case 403: await interaction.followup.send("Error 403 - Forbidden: Access is denied")
        case 404: await interaction.followup.send("Error 404 - Not found: City not found")
        case 500: await interaction.followup.send("Error 500 - Intenal server error: Please try again later")
        case 502: await interaction.followup.send("Error 502 - Bad gateway: Invalid response from the server")
        case 503: await interaction.followup.send("Error 503 - Service unavailable: Server is down")
        case 504: await interaction.followup.send("Error 504 - Gateway timeout: No response from the server")
        case _:await interaction.followup.send(f"HTTP error occured: {httpErr}")

    except requests.exceptions.ConnectionError:
      await interaction.followup.send("Connection Error: Check your internet connection")

    except requests.exceptions.Timeout:
      await interaction.followup.send("Timeout Error: The request timed out")

    except requests.exceptions.TooManyRedirects:
      await interaction.followup.send("Too Many Redirects Error: Check the URL")

    except requests.exceptions.RequestException as reqErr:
      await interaction.followup.send(f"Request Error: {reqErr}")

  @app_commands.command(name="dailyweather", description="Check weather for a city (Max 10 days)")
  async def dailyWeather(self, interaction: discord.Interaction, city: str, days: int):
    if days < 1:
      await interaction.response.send_message("Must be at least 1 day", ephemeral=True)
      return
    elif days > 10:
      await interaction.response.send_message("Maximum is 10 days, sry :<", ephemeral=True)
      return
    
    await interaction.response.defer(ephemeral=False)
    try:
      dailyWeatherAPI = f"https://discord-bot-hosting-vft8.onrender.com/api/dailyweather/{city}?days={days}"
      
      response = requests.get(dailyWeatherAPI)
      data = response.json()

      if response.status_code != 200:
        error_data = data
        error_msg = error_data.get("error", "Could not fetch weather data.")
        await interaction.followup.send(f"{error_msg}")
        return
      
      forecast_lines = []

      for dayData in data.get("forecast", []):
        raw_date_str = dayData.get("date", "")
        clean_date_str = " ".join(raw_date_str.split()[:4])
        try:
          raw_date = datetime.datetime.strptime(clean_date_str, "%a, %d %b %Y")
          formattedDate = raw_date.strftime("%a, %b %d")
        except Exception:
          formattedDate = clean_date_str
        
        maxTemp_C = f"{dayData.get('maxTemp', ''):.1f}"
        minTemp_C = f"{dayData.get('minTemp' ''):.1f}"

        feelsLikeMaxTemp_C = f"{dayData.get('feelsLikeMaxTemp' ''):.1f}"
        feelsLikeMinTemp_C = f"{dayData.get('feelsLikeMinTemp', ''):.1f}"
        
        daytimeEmoji = self.get_weather_emoji(dayData.get("type", ""))
        description = dayData.get("description", "No description").title()

        day_string = (
          f"**{formattedDate}**\n"
          f"{daytimeEmoji} {description} | "
          f"🔺 **{maxTemp_C}°C** / 🔻 **{minTemp_C}°C**\n"
          f"Feels like: 🔺 **{feelsLikeMaxTemp_C}°C** / 🔻 **{feelsLikeMinTemp_C}°C**\n"
          f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        forecast_lines.append(day_string)
      
      full_forecast_text = "\n".join(forecast_lines)

      embed = discord.Embed(
        title = f"{days} Day(s) Weather Forecast",
        description = f"📍 {data['location']}\n\n{full_forecast_text}",
        color = discord.Color.blurple()
      )

      await interaction.followup.send(embed=embed)

    except requests.exceptions.HTTPError as httpErr:
      status = httpErr.response.status_code
      match status:
        case 400: await interaction.followup.send("Error 400 - Bad request: Please check your input")
        case 401: await interaction.followup.send("Error 401 - Unauthorised: Invalid API key")
        case 403: await interaction.followup.send("Error 403 - Forbidden: Access is denied")
        case 404: await interaction.followup.send("Error 404 - Not found: City not found")
        case 500: await interaction.followup.send("Error 500 - Intenal server error: Please try again later")
        case 502: await interaction.followup.send("Error 502 - Bad gateway: Invalid response from the server")
        case 503: await interaction.followup.send("Error 503 - Service unavailable: Server is down")
        case 504: await interaction.followup.send("Error 504 - Gateway timeout: No response from the server")
        case _:await interaction.followup.send(f"HTTP error occured: {httpErr}")

    except requests.exceptions.ConnectionError:
      await interaction.followup.send("Connection Error: Check your internet connection")

    except requests.exceptions.Timeout:
      await interaction.followup.send("Timeout Error: The request timed out")

    except requests.exceptions.TooManyRedirects:
      await interaction.followup.send("Too Many Redirects Error: Check the URL")

    except requests.exceptions.RequestException as reqErr:
      await interaction.followup.send(f"Request Error: {reqErr}")

async def setup(bot):
  await bot.add_cog(Weather(bot))