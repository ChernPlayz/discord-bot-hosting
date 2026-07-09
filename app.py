import discord
import os
from flask import Flask, request, render_template, url_for, redirect, jsonify, session
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
@app.route('/api/userinfo', methods=['GET'])
def userInfo():
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


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000, debug=True)