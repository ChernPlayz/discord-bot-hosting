import discord
import os
from flask import Flask, request, render_template, url_for, redirect, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session
from bot import bot

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
    return render_template("embeds.html")
  return render_template("index.html")

@app.route('/login')
def login():
  return redirect(
    f"https://discord.com/oauth2/authorize"
    f"?client_id={CLIENT_ID}"
    f"&response_type=code"
    f"&redirect_uri=https%3A%2F%2Fdiscord-bot-hosting-vft8.onrender.com%2Fauth%2Fdiscord"
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

    return jsonify({
      "username": user_data.get("username"),
      "avatar": user_data.get("avatar")
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

# Embeds
@app.route('/api/guilds', methods=['GET'])
def get_guilds():
  if "oauth_token" not in session:
    return jsonify({"error": "Unauthorized: Please log in first!"}), 401
  
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

  if bot is None or not bot.is_ready():
    return jsonify({"error": "Discord bot is not ready yet!"}), 503
  
  data = request.json
  channel_id = data.get("channel_id")

  if not channel_id:
    return jsonify({"detail": "Missing channel_id parameter"}), 400
  

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000, debug=True)