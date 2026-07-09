import discord
import datetime
from discord.ext import commands
from discord import app_commands
from database import Database

class DarkHistory(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="sethistorychannel", description="Set the channel where anonymous histories are posted")
  @app_commands.checks.has_permissions(manage_channels=True)
  async def sethistorychannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
    await interaction.response.defer(ephemeral=True)
    guild_id = interaction.guild_id
    
    await Database.dark_history_collection.update_one(
      {"guild_id": guild_id},
      {"$set": {"post_channel_id": channel.id}},
      upsert=True
    )
    
    await interaction.followup.send(f"History post channel set to {channel.mention}", ephemeral=True)

  @app_commands.command(name="sethistorylogchannel", description="Set the private channel where user logs are sent")
  @app_commands.checks.has_permissions(manage_channels=True)
  async def sethistorylogchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
    await interaction.response.defer(ephemeral=True)
    guild_id = interaction.guild_id
    
    await Database.dark_history_collection.update_one(
      {"guild_id": guild_id},
      {"$set": {"log_channel_id": channel.id}},
      upsert=True
    )
    
    await interaction.followup.send(f"History log channel set to {channel.mention}", ephemeral=True)
    
  @app_commands.command(name="darkhistory", description="Post your darkest history 👀")
  async def darkhistory(self, interaction: discord.Interaction, msg: str):
    await interaction.response.defer(ephemeral=True)
    guild_id = interaction.guild_id

    try:
      guild_settings = await Database.dark_history_collection.find_one({"guild_id": guild_id})
    except Exception as err:
      await interaction.followup.send(f"An error occured connecting to the database: {err}", ephemeral=True)
      return

    postChannelID = guild_settings["post_channel_id"]
    logChannelID = guild_settings["log_channel_id"]

    if not guild_settings or not postChannelID or not logChannelID:
      await interaction.followup.send(
        "This server has not configured the history or log history channels yet.\n"
        "Please ask an admin to use /sethistorychannel and /sethistorylogchannel.",
        ephemeral=True
      )
      return
    
    postChannel = interaction.client.get_channel(postChannelID)
    logChannel = interaction.client.get_channel(logChannelID)

    if postChannel is None or logChannel is None:
      await interaction.followup.send(
        "History or log history channels could not be found. Check if they are deleted.", 
        ephemeral=True
      )
      return
    
    embed = discord.Embed(
      title = "Anonymous Person",
      description = msg,
      color = discord.Color.from_rgb(0,0,0),
      timestamp=datetime.datetime.now()
    )
    embed.set_author(name="Dark History")
    await postChannel.send(embed=embed)

    log_embed = discord.Embed(
      title="Dark History Log",
      description=f"User: {interaction.user.mention} (`{interaction.user.name}`)\n"
                  f"User ID: `{interaction.user.id}`\n"
                  f"Dark History Message:\n{msg}",
      color=discord.Color.from_rgb(255,0,0),
      timestamp=datetime.datetime.now()
    )
    await logChannel.send(embed=log_embed)
    await interaction.followup.send("Your history is sent", ephemeral=True)

async def setup(bot):
  await bot.add_cog(DarkHistory(bot))