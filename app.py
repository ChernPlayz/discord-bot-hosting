import discord
import os
import asyncio
from flask import Flask, request, render_template, url_for, redirect, jsonify, session, current_app
from flask_cors import CORS
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session

app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path='/')
CORS(app)

# Env
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
app.secret_key = os.getenv("FLASK_SECRET_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# URI & URL
REDIRECT_URI = "https://discord-bot-hosting-vft8.onrender.com/auth/discord"
API_BASE_URL = "https://discord.com/api/v10"
AUTHORIZATION_BASE_URL = f"{API_BASE_URL}/oauth2/authorize"
TOKEN_URL = f"{API_BASE_URL}/oauth2/token"

# Index, Login, Logout
@app.route('/')
def index():
  if "oauth_token" in session:
    return redirect(url_for('embeds'))
  return render_template("index.html")

@app.route('/login')
def login():
  return redirect(
    f"https://discord.com/oauth2/authorize"
    f"?client_id={CLIENT_ID}"
    f"&response_type=code"
    f"&redirect_uri={REDIRECT_URI}"
    f"&scope=identify%20guilds"
  )

@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('index'))

# Discord Auth
def get_discord_session(token=None, state=None):
  return OAuth2Session(
    client_id=CLIENT_ID, 
    token=token, 
    state=state, 
    scope=["identify", "guilds"], 
    redirect_uri=REDIRECT_URI
  )

@app.route('/auth/discord')
def discordAuth():
  code = request.args.get("code")
  if not code:
    return "Error: Missing authorization code from Discord", 400

  try:
    discord_session = get_discord_session()
    token = discord_session.fetch_token(
      token_url=TOKEN_URL,
      client_secret=CLIENT_SECRET, 
      code=code
    )
    session["oauth_token"] = token
    return redirect(url_for('index'))
  
  except Exception as err:
    return f"Error exchanging code for credentials: {err}", 500

# User Data
@app.route('/api/user_data', methods=['GET'])
def get_user_data():
  if "oauth_token" not in session:
    return jsonify({"error": "Unauthorized: Please log in first!"}), 401
  
  try:
    discord_session = get_discord_session(token=session["oauth_token"])
    user_data = discord_session.get(f"{API_BASE_URL}/users/@me").json()
    
    username = user_data.get("username")
    user_id = user_data.get("id")
    avatar_hash = user_data.get("avatar")

    if avatar_hash:
      avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png?size=128"
    else:
      avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
    
    return jsonify({
      "username": username,
      "avatar_url": avatar_url
    }), 200
  
  except Exception as err:
    return jsonify({"error": f"Failed to fetch user data: {err}"}), 500

# HTML Pages
@app.route('/embeds')
def embeds():
  return render_template("embeds.html")

@app.route('/currentWeather')
def currentWeather():
  return render_template("currentWeather.html")

@app.route('/hourlyWeather')
def hourlyWeather():
  return render_template("hourlyWeather.html")

@app.route('/dailyWeather')
def dailyWeather():
  return render_template("dailyWeather.html")

@app.route('/polls')
def polls():
  return render_template("polls.html")

@app.route('/reactionRoles')
def reactionRoles():
  return render_template("reactionRoles.html")

@app.route('/moderation')
def moderation():
  return render_template("moderation.html")

@app.route('/logs')
def logs():
  return render_template("logs.html")

# Embeds
@app.route('/api/guilds', methods=['GET'])
def get_guilds():
  if "oauth_token" not in session:
    return jsonify({"error": "Unauthorized: Please log in first!"}), 401
  
  bot = current_app.config.get("DISCORD_BOT")
  if bot is None or not bot.is_ready():
    return jsonify({"error": "Discord bot is not ready yet!"}), 503

  try:
    discord_session = get_discord_session(token=session["oauth_token"])
    guilds_data = discord_session.get(f"{API_BASE_URL}/users/@me/guilds").json()

    admin_guild_ids = []
    for guild in guilds_data:
      is_owner = guild.get("owner", False)
      user_perms = int(guild.get("permissions", 0))
      is_admin = (user_perms & 0x8) == 0x8 # bitwise operator &, admin at 0000 1000 or 0x8
      
      if is_owner or is_admin:
        admin_guild_ids.append(guild["id"])

    guilds_list = []
    for guild in bot.guilds:
      if str(guild.id) in admin_guild_ids:
        has_channels = any(
          isinstance(channel, discord.TextChannel) and channel.permissions_for(guild.me).send_messages 
          for channel in guild.channels
        )
        if has_channels:
          guilds_list.append({
            "id": str(guild.id),
            "name": guild.name
          })

    return jsonify(guilds_list)

  except Exception as err:
    return jsonify({"error": f"Failed to fetch guilds: {err}"}), 500

@app.route('/api/channels/<int:guild_id>', methods=['GET'])
def get_channels(guild_id):
  if "oauth_token" not in session:
    return jsonify({"error": "Unauthorized: Please log in first!"}), 401

  bot = current_app.config.get("DISCORD_BOT")
  if bot is None or not bot.is_ready():
    return jsonify({"error": "Discord bot is not ready yet!"}), 503
  
  try:
    guild = bot.get_guild(guild_id)
    if not guild:
      return jsonify({"error": "Guild not found"}), 500

    channels_list = []
    for channel in guild.channels:
      if isinstance(channel, discord.TextChannel):
        permissions = channel.permissions_for(guild.me)
        if permissions.view_channel and permissions.send_messages:
          channels_list.append({
            "id": str(channel.id),
            "name": channel.name
          })
                
    return jsonify(channels_list)

  except Exception as err:
    return jsonify({"error": f"Failed to fetch channels: {err}"}), 500

@app.route('/api/send_embed', methods=['POST'])
def send_embed():
  if "oauth_token" not in session:
    return jsonify({"error": "Unauthorized: Please log in first!"}), 401

  bot = current_app.config.get("DISCORD_BOT")
  if bot is None or not bot.is_ready():
    return jsonify({"error": "Discord bot is not ready yet!"}), 503
  
  data = request.json
  channel_id = data["channel_id"]

  if not channel_id:
    return jsonify({"error": "Missing Channel ID"}), 400
  
  # Parse hex color string to RGB
  hex_color = data.get("color", "#000000").lstrip('#')
  rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
  embed_color = discord.Color.from_rgb(*rgb)

  # Build the Embed object
  embed = discord.Embed(
    title=data["title"] or None,
    url=data["title_url"] or None,
    description=data["description"] or None,
    color=embed_color
  )

  author = data.get("author", {})
  if author["icon_name"]:
    embed.set_author(
      name=author["icon_name"], 
      url=author["icon_url"] or None, 
      icon_url=author["icon_name_url"] or None
    )
  
  for field in data.get("fields", []):
    field_title = field["title"]
    field_desc = field["desc"]
    isInline = field["inline"]
    
    embed.add_field(
      name=field_title, 
      value=field_desc, 
      inline=isInline
    )

  if data["image_url"]:
    embed.set_image(url=data["image_url"])

  if data["thumbnail_url"]:
    embed.set_thumbnail(url=data["thumbnail_url"])

  if data["footer"]:
    embed.set_footer(text=data["footer"], icon_url=data["footer_icon_url"] or None)
  
  try:
    channel = bot.get_channel(int(channel_id))

    future = asyncio.run_coroutine_threadsafe(
      channel.send(content=data["embed_text_send"] or None, embed=embed),
      bot.loop
    )
    future.result(timeout=10)
    return jsonify({"status": "success"}), 200
  
  except Exception as err:
    return jsonify({"error": f"Failed to send embed: {err}"}), 500

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000, debug=True)