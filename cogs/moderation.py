import discord
import datetime
from discord.ext import commands
from discord import app_commands
from database import Database

class Moderation(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.banned_words = ["nigger"]
  
  # Censor words on msg
  @commands.Cog.listener()
  async def on_message(self, msg):
    if msg.author.bot:
      return
    
    text = msg.content.lower()

    if any(word in text for word in self.banned_words):
      await msg.delete()

      if "nigger" in text:
        await msg.channel.send(f"{msg.author.mention}, hey u racist")
      if "fuck" in text:
        await msg.channel.send(f"No F word :)")

  # Log Infraction
  def log_infraction(self, guild_id: int, user_id: int, mod: discord.User, type: str, reason: str="", extra_data: dict=None) -> int:
    user_record = Database.modlogs_collection.find_one({"guild_id": guild_id, "user_id": user_id})
    case_id = 1 if not user_record or "infractions" not in user_record else len(user_record["infractions"]) + 1

    new_entry = {
      "case_id": case_id,
      "type": type,
      "reason": reason,
      "moderator": str(mod),
      "moderator_id": mod.id,
      "time": datetime.datetime.now(datetime.timezone.utc).timestamp()
    }

    if extra_data:
      new_entry.update(extra_data)

    Database.modlogs_collection.update_one(
      {"guild_id": guild_id, "user_id": user_id},
      {"$push": {"infractions": new_entry}},
      upsert=True
    )

    return case_id

  # Get mod logs channel
  async def get_modlogs_channel(self, interaction: discord.Interaction) -> discord.TextChannel:
    guild_id = interaction.guild_id

    try:
      settings_document = await Database.modlogschannel_collection.find_one({"guild_id": guild_id})
    except Exception as err:
      await interaction.followup.send("An error occured connecting to the database")
      return None

    if not settings_document or not settings_document["log_channel_id"]:
      await interaction.followup.send(
        "This server has not configured the mod logs channel yet\n"
        "Please ask an admin to use /setmodlogschannel",
        ephemeral=True
      )
      return None
    
    logChannelID = settings_document["log_channel_id"]
    logChannel = interaction.client.get_channel(logChannelID)

    if logChannel is None:
      await interaction.followup.send(
        "Mod logs channel could not be found. Check if they are deleted", 
        ephemeral=True
      )
      return None
    
    return logChannel
  
  # /setmodlogschannel
  @app_commands.command(name="setmodlogschannel", description="Set the private channel where mod logs are sent")
  @app_commands.checks.has_permissions(manage_channels=True)
  async def setmodlogschannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
    await interaction.response.defer(ephemeral=True)
    guild_id = interaction.guild_id
    
    await Database.modlogschannel_collection.update_one(
      {"guild_id": guild_id},
      {"$set": {"log_channel_id": channel.id}},
      upsert=True
    )
    
    await interaction.followup.send(f"Mod logs channel set to {channel.mention}")

  # Check Mod Hierarchy
  async def check_mod_hierarchy(self, interaction: discord.Interaction, member: discord.Member, action: str="", msg: str="") -> bool:
    if member == interaction.user:
      await interaction.followup.send(f"You cannot {action} yourself")
      return False
    
    if member.top_role >= interaction.user.top_role:
      await interaction.followup.send(f"You cannot {action} someone with an equal/higher role")
      return False
    
    if member.top_role >= interaction.guild.me.top_role:
      await interaction.followup.send(f"My role is too low to {action} this user")
      return False
    
    if member.bot:
      if member.id == self.bot.user.id:
        await interaction.followup.send(msg)
        return False
      
      await interaction.followup.send(f"You cannot {action} other bots")
      return False
    
    return True

  # /kick
  @app_commands.command(name="kick", description="Kick a member from this server")
  @app_commands.checks.has_permissions(kick_members=True)
  async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str="No reason provided"):
    await interaction.response.defer()
    
    hierarchyResult = await self.check_mod_hierarchy(interaction, member, action="kick", msg="How dare you want to kick me after everything I've done for this server >:<")
    if not hierarchyResult:
      return
    
    logChannel = await self.get_modlogs_channel(interaction)
    if not logChannel:
      return
    
    try:
      await member.kick(reason=reason)
      case_id = await self.log_infraction(
        guild_id=interaction.guild_id,
        user_id=member.id,
        mod=interaction.user,
        type="KICK",
        reason=reason
      )
      await logChannel.send(f"{member.mention} has been kicked from the server | Case #{case_id}\nReason: {reason}")
      await interaction.followup.send(f"Successfully kicked {member.mention}\nReason: {reason}")
    
    except Exception as err:
      await interaction.followup.send(f"Failed to kick {member.mention}: {err}")

  # /ban
  @app_commands.command(name="ban", description="Ban a member from this server")
  @app_commands.checks.has_permissions(ban_members=True)
  async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str="No reason provided"):
    await interaction.response.defer()

    hierarchyResult = await self.check_mod_hierarchy(interaction, member, action="ban", msg="SERIOUSLY!? Why do you wanna ban me after everything I've done for this server 🤬")
    if not hierarchyResult:
      return
    
    logChannel = await self.get_modlogs_channel(interaction)
    if not logChannel:
      return
    
    try:
      await member.ban(reason=reason)
      case_id = await self.log_infraction(
        guild_id=interaction.guild_id,
        user_id=member.id,
        mod=interaction.user,
        type="BAN",
        reason=reason
      )
      await logChannel.send(f"{member.mention} has been banned from the server | Case #{case_id}\nReason: {reason}")
      await interaction.followup.send(f"Successfully banned {member.mention}\nReason: {reason}")
    
    except Exception as err:
      await interaction.followup.send(f"Failed to ban {member.mention}: {err}")

  # /unban
  @app_commands.command(name="unban", description="Unban a member from this server")
  @app_commands.checks.has_permissions(ban_members=True)
  async def unban(self, interaction: discord.Interaction, user_id: int):
    await interaction.response.defer()

    logChannel = await self.get_modlogs_channel(interaction)
    if not logChannel:
      return
    
    try:
      user = await self.bot.fetch_user(user_id)
      await interaction.guild.unban(user)
      await logChannel.send(f"{user.mention} has been unbanned by {interaction.user.mention}")
      await interaction.followup.send(f"{user.mention} has been unbanned")
    
    except Exception as err:
      await interaction.followup.send(f"Failed to unban {user.mention}: {err}")

  # /mute
  @app_commands.command(name="mute", description="Mute a member from this server")
  @app_commands.checks.has_permissions(moderate_members=True)
  async def mute(self, interaction: discord.Interaction, member: discord.Member, duration_hrs: int, duration_mins: int, reason: str="No reason provided"):
    await interaction.response.defer()

    hierarchyResult = await self.check_mod_hierarchy(interaction, member, action="mute", msg="What did I even do wrong? Y would u wanna mute me?")
    if not hierarchyResult:
      return
    
    logChannel = await self.get_modlogs_channel(interaction)
    if not logChannel:
      return
    
    try:
      total_mins = duration_hrs*60 + duration_mins
      await member.timeout(datetime.timedelta(minutes=total_mins), reason=reason)
      case_id = await self.log_infraction(
        guild_id=interaction.guild_id,
        user_id=member.id,
        mod=interaction.user,
        type="MUTE",
        reason=reason,
        extra_data={"duration": total_mins}
      )
      await logChannel.send(f"{member.mention} has been muted from the server for {duration_hrs}hr(s) {duration_mins}min(s) | Case #{case_id}\nReason: {reason}")
      await interaction.followup.send(f"Successfully muted {member.mention} for {duration_hrs}hr(s) {duration_mins}min(s)\nReason: {reason}")
    
    except Exception as err:
      await interaction.followup.send(f"Failed to mute {member.mention}: {err}")

  # /unmute
  @app_commands.command(name="unmute", description="Unmute a member from this server")
  @app_commands.checks.has_permissions(moderate_members=True)
  async def unmute(self, interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer()
    
    hierarchyResult = await self.check_mod_hierarchy(interaction, member, action="unmute", msg="")
    if not hierarchyResult:
      return
    
    if not member.timed_out_until:
      await interaction.followup.send(f"{member.mention} is not currently muted")
      return
    
    logChannel = await self.get_modlogs_channel(interaction)
    if not logChannel:
      return
    
    try:
      await member.timeout(None)
      await logChannel.send(f"{member.mention} has been unmuted by {interaction.user.mention}")
      await interaction.followup.send(f"Successfully unmuted {member.mention}")
    except Exception as err:
      await interaction.followup.send(f"Failed to unmute {member.mention}: {err}")

  # /warn
  @app_commands.command(name="warn", description="Warn a member from this server")
  @app_commands.checks.has_permissions(manage_messages=True)
  async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str="No reason provided"):
    await interaction.response.defer()
    
    hierarchyResult = await self.check_mod_hierarchy(interaction, member, action="warn", msg="What did I even do wrong? Y u wanna warn me?")
    if not hierarchyResult:
      return
    
    logChannel = await self.get_modlogs_channel(interaction)
    if not logChannel:
      return
    
    user_id = member.id
    guild_id = interaction.guild_id

    case_id = await self.log_infraction(
      guild_id=interaction.guild_id,
      user_id=member.id,
      mod=interaction.user,
      type="WARN",
      reason=reason
    )

    user_record = await Database.modlogs_collection.find_one({"guild_id": guild_id, "user_id": user_id})
    warn_count = len([infraction for infraction in user_record["infractions"] if infraction["type"] == "WARN"])

    if warn_count >= 3:
      try:
        if member.top_role >= interaction.guild.me.top_role:
          await interaction.followup.send("I cannot ban this user because their role is higher than mine.")
          return
        
        await member.ban(reason="Reached 3 warnings")
        await logChannel.send(f"{member.mention} has been warned | Case #{case_id}\nReason: {reason}\nTotal warnings: {warn_count}\n{member.mention} has been banned from the server for reaching 3 warnings")
        await interaction.followup.send(f"Successfully warned & banned {member.mention}\nReason: {reason}")

      except discord.Forbidden:
        await interaction.followup.send("I don't have permission to ban this user")
        return
    else:
      await logChannel.send(f"{member.mention} has been warned | Case #{case_id}\nReason: {reason}\nTotal warnings: {warn_count}")
      await interaction.followup.send(f"Successfully warned {member.mention}\nReason: {reason}")

  # /clearwarns
  @app_commands.command(name="clearwarns", description="Clear all warnings from a member")
  @app_commands.checks.has_permissions(manage_messages=True)
  async def clearwarns(self, interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer()
    
    logChannel = await self.get_modlogs_channel(interaction)
    if not logChannel:
      return
    
    user_id = member.id
    guild_id = interaction.guild_id

    result = await Database.modlogs_collection.update_one(
      {"guild_id": guild_id, "user_id": user_id},
      {"$pull": {"infractions": {"type": "WARN"}}}
    )

    if result.modified_count > 0:
      user_record = await Database.modlogs_collection.find_one({"guild_id": guild_id, "user_id": user_id})
        
      if user_record and "infractions" in user_record:
        cases = user_record["infractions"]

      if len(cases) == 0:
        await Database.modlogs_collection.delete_one({"guild_id": guild_id, "user_id": user_id})
      else:
        for i, remaining_case in enumerate(cases):
          remaining_case["case_id"] = i+1
            
        await Database.modlogs_collection.update_one(
          {"guild_id": guild_id, "user_id": user_id},
          {"$set": {"infractions": cases}}
        )
      
      await logChannel.send(f"Cleared all warnings for {member.mention}")
      await interaction.followup.send(f"Successfully cleared all warnings for {member.mention}")
    else:
      await interaction.followup.send(f"{member.mention} has no warnings")
  
  # /removecase
  @app_commands.command(name="removecase", description="Remove a specific case from a member")
  @app_commands.checks.has_permissions(manage_messages=True)
  async def removecase(self, interaction: discord.Interaction, member: discord.Member, case_id: int):
    await interaction.response.defer()
    
    logChannel = await self.get_modlogs_channel(interaction)
    if not logChannel:
      return
    
    user_id = member.id
    guild_id = interaction.guild_id
    user_record = await Database.modlogs_collection.find_one({"guild_id": guild_id, "user_id": user_id})

    if not user_record or not user_record["infractions"]:
      await interaction.followup.send(f"{member.mention} has no warnings")
      return
    
    cases = user_record["infractions"]
    
    if case_id < 1 or case_id > len(cases):
      await interaction.followup.send(f"Invalid case id\nThis user only have {len(cases)} case(s)")
      return
    
    target_case = cases.pop(case_id-1)

    for i, remaining_case in enumerate(cases):
      remaining_case["case_id"] = i+1

    if len(cases) == 0:
      await Database.modlogs_collection.delete_one({"guild_id": guild_id, "user_id": user_id})
    else:
      await Database.modlogs_collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"infractions": cases}}
      )

    await logChannel.send(f"Removed Case #{case_id} `[{target_case["type"]}]` from {member.mention}\nReason: {target_case["reason"]}")
    await interaction.followup.send(f"Successfully removed Case #{case_id} `[{target_case["type"]}]` from {member.mention}\nReason: {target_case["reason"]}")
  
  # /modlogs
  @app_commands.command(name="modlogs", description="Check wat naughty thing a member did >:)")
  @app_commands.checks.has_permissions(manage_messages=True)
  async def modlogs(self, interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer()
    
    logChannel = await self.get_modlogs_channel(interaction)
    if not logChannel:
      return
    
    user_id = member.id
    guild_id = interaction.guild_id
    user_record = await Database.modlogs_collection.find_one({"guild_id": guild_id, "user_id": user_id})

    if not user_record or not user_record["infractions"] or len(user_record["infractions"]) == 0:
      await interaction.followup.send(f"{member.mention} didn't have any infractions, is a good hooman :)")
      return
    
    embed = discord.Embed(
      title = f"Modlogs for {member.name}", 
      description = f"User ID: `{member.id}`", 
      color = discord.Color.blurple()
    )
    embed.set_thumbnail(url=member.display_avatar.url)

    for infraction in user_record["infractions"]:
      case_id = infraction.get("case_id")
      type = infraction.get("type", "WARN")
      reason = infraction.get("reason")
      mod = infraction.get("moderator")
      raw_time = infraction.get("time")

      if type == "KICK":
        badge = f"**`[KICK]`** Case #{case_id}"
      elif type == "WARN":
        badge = f"**`[WARN]`** Case #{case_id}"
      elif type == "MUTE":
        duration = infraction.get("duration", 0)
        badge = f"**`[MUTE]`** `{duration//60}hr(s) {duration%60}min(s)` Case #{case_id}"
      elif type == "BAN":
        badge = f"**`[BAN]`** Case #{case_id}"
      else:
        badge = f"Case #{case_id}"

      try:
        time_display = f"<t:{int(float(raw_time))}:F>"
      except (ValueError, TypeError):
        time_display = f"{raw_time} GMT+8"
          
      value_details = f"Reason: {reason}\nModerator: {mod}\nTime: {time_display}"
      embed.add_field(name=badge, value=value_details, inline=False)

    await interaction.followup.send(embed=embed)

async def setup(bot):
  await bot.add_cog(Moderation(bot))