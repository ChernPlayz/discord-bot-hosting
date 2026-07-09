import discord
import os
import logging
import threading
from discord.ext import commands
from dotenv import load_dotenv
from database import Database
from app import app

load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.guilds = True

guilds = [
  discord.Object(id=1156550837993222295), #???
  discord.Object(id=1506576753123135578), # Bot Testing
  discord.Object(id=1074174521235480596) #blacknight
]

class MyBot(commands.Bot):  
  async def setup_hook(self):
    db_success = await Database.initDB()

    if not db_success:
      print("Bot shutting down due to database connection failure")
      await self.close()
      return

    for fileName in os.listdir("cogs"):
      if fileName.endswith(".py"):
        try:
          await self.load_extension(f"cogs.{fileName[:-3]}")
          print(f"Loaded cog: {fileName}")
        except Exception as err:
          print(f"Failed to load {fileName}: {err}")

bot = MyBot(command_prefix="!", intents=intents)

# Bot logging in
@bot.event
async def on_ready():
  print(f"{bot.user.name} has logged in!")
  
  try:
    for guild in guilds:
      bot.tree.copy_global_to(guild=guild)
      syncedCmds = await bot.tree.sync(guild=guild)
      print(f"Synced {len(syncedCmds)} commands to guild {guild.id}")
  except Exception as err:
    print(f"Error syncing commands: {err}")
    
# Member joined
@bot.event
async def on_member_join(member):
  await member.send(f"Welcome to {member.guild.name}, {member.mention}!")

def run_flask():
  app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
  app.config["DISCORD_BOT"] = bot
  
  flask_thread = threading.Thread(target=run_flask)
  flask_thread.daemon = True
  flask_thread.start()
  print("Flask server started!")

  bot.run(token=discord_token, log_handler=handler, log_level=logging.DEBUG)