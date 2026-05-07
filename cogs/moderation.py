import discord, json, os, datetime
from discord.ext import commands
from discord import app_commands

class Moderation(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.banned_words = ["nigger"]
    self.allowed_roles_id = [
      1459100339578994701, #Admin
      1501594372104261692, #Moderator
      ]
    self.warn_data = {}
    self.warning_file = "warnings.json"
    self.warn_data = self.load_warnings()

  def load_warnings(self):
    try:
      if os.path.exists(self.warning_file):
        with open(self.warning_file, "r") as file:
          content = file.read().strip()

          if not content:
            return {}
          
          return json.loads(content)

    except json.JSONDecodeError:
      print("This json file is corrupted, resetting file...")
      return {}
    except FileNotFoundError:
      print("That file was not found")
    except PermissionError:
      print("You do not have permission to read the file")

    return {}
  
  def save_warnings(self):
    try:
      with open(self.warning_file, "w") as file:
        json.dump(self.warn_data, file, indent=2)
    except FileExistsError:
      print("That file already exists")

  # censor words
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

  def has_mod_role(self, member: discord.Member):
    return any(role.id in self.allowed_roles_id for role in member.roles)
  
  def is_mod(self, interaction: discord.Interaction):
    return(
      interaction.user.guild_permissions.kick_members or
      interaction.user.guild_permissions.ban_members
    ) and self.has_mod_role(interaction.user)

  # kick
  @app_commands.command(name="kick", description="Kick a member from this server")
  @app_commands.checks.has_permissions(kick_members=True)
  async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str="No reason provided"):
    if not self.is_mod(interaction):
      await interaction.response.send_message("You are not a mod/admin", ephemeral=True)
      return
    
    if member == interaction.user:
      await interaction.response.send_message("You cannot kick yourself", ephemeral=True)
      return
    
    if member.top_role >= interaction.user.top_role:
      await interaction.response.send_message("You cannot kick someone with equal/higher role", ephemeral=True)
      return
    
    if member.top_role > interaction.guild.me.top_role:
      await interaction.response.send_message("My role is too low to kick this user", ephemeral=True)
      return
    
    if member.bot:
      if member.id == self.bot.user.id:
        await interaction.response.send_message("How dare you want to kick me after everything I've done for this server >:<", ephemeral=True)
        return
      
      await interaction.response.send_message("You cannot kick bots", ephemeral=True)
      return
        
    try:
      await member.kick(reason=reason)
      await interaction.response.send_message(f"{member.mention} has been kicked from the server\nReason: {reason}")
    
    except discord.Forbidden:
      await interaction.response.send_message("Missing permissions", ephemeral=True)

    except discord.HTTPException:
      await interaction.response.send_message("Discord API Error", ephemeral=True)
 
    except Exception as err:
      await interaction.response.send_message(f"Error: {err}", ephemeral=True)

  # ban
  @app_commands.command(name="ban", description="Ban a member from this server")
  @app_commands.checks.has_permissions(ban_members=True)
  async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str="No reason provided"):
    if not self.is_mod(interaction):
      await interaction.response.send_message("You are not a mod/admin", ephemeral=True)
      return
    
    if member == interaction.user:
      await interaction.response.send_message("You cannot ban yourself", ephemeral=True)
      return
    
    if member.top_role >= interaction.user.top_role:
      await interaction.response.send_message("You cannot ban someone with equal/higher role", ephemeral=True)
      return
    
    if member.top_role > interaction.guild.me.top_role:
      await interaction.response.send_message("My role is too low to ban this user", ephemeral=True)
      return
    
    if member.bot:
      if member.id == self.bot.user.id:
        await interaction.response.send_message("SERIOUSLY!? Why do you wanna ban me after everything I've done for this server 🤬", ephemeral=True)
        return
      await interaction.response.send_message("You cannot ban bots", ephemeral=True)
      return
            
    try:
      await member.ban(reason=reason)
      await interaction.response.send_message(f"{member.mention} has been banned from the server\nReason: {reason}")
    
    except discord.Forbidden:
      await interaction.response.send_message("Missing permissions", ephemeral=True)

    except discord.HTTPException:
      await interaction.response.send_message("Discord API Error", ephemeral=True)

    except Exception as err:
      await interaction.response.send_message(f"Error: {err}", ephemeral=True)

  # unban
  @app_commands.command(name="unban", description="Unban a member from this server")
  @app_commands.checks.has_permissions(ban_members=True)
  async def unban(self, interaction: discord.Interaction, user_id: str):
    if not self.is_mod(interaction):
      await interaction.response.send_message("You are not a mod/admin", ephemeral=True)
      return
    
    try:
      user = await self.bot.fetch_user(int(user_id))
      await interaction.guild.unban(user)
      await interaction.response.send_message(f"Unbanned {user.mention}")

    except ValueError:
      await interaction.response.send_message("Invalid user ID", ephemeral=True)

    except discord.NotFound:
      await interaction.response.send_message("User not found", ephemeral=True)

    except discord.Forbidden:
      await interaction.response.send_message("Missing permissions", ephemeral=True)

    except discord.HTTPException:
      await interaction.response.send_message("Discord API Error", ephemeral=True)

    except Exception as err:
      await interaction.response.send_message(f"Error: {err}", ephemeral=True)

  # warn
  @app_commands.command(name="warn", description="Warn a member from this server")
  @app_commands.checks.has_permissions(manage_messages=True)
  async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str="No reason provided"):
    if not self.is_mod(interaction):
      await interaction.response.send_message("You are not a mod/admin", ephemeral=True)
      return

    if member == interaction.user:
      await interaction.response.send_message("You cannot warn yourself", ephemeral=True)
      return
    
    if member.top_role >= interaction.user.top_role:
      await interaction.response.send_message("You cannot warn someone with equal/higher role", ephemeral=True)
      return
    
    if member.top_role > interaction.guild.me.top_role:
      await interaction.response.send_message("My role is too low to warn this user", ephemeral=True)
      return
    
    if member.bot:
      if member.id == self.bot.user.id:
        await interaction.response.send_message("What did I even do wrong? :<", ephemeral=True)
        return
      await interaction.response.send_message("You cannot warn bots", ephemeral=True)
      return
        
    user_id = str(member.id)

    if user_id not in self.warn_data:
      self.warn_data[user_id] = []

    warning_data = {
      "reason": reason,
      "moderator": str(interaction.user),
      "moderator_id": interaction.user.id,
      "time": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    self.warn_data[user_id].append(warning_data)
    self.save_warnings()

    warn_count = len(self.warn_data[user_id])

    if warn_count >= 3:
      try:
        if member.top_role >= interaction.guild.me.top_role:
          await interaction.response.send_message("I cannot ban this user because their role is higher than mine.", ephemeral=True)
          return
        
        await member.ban(reason="Reached 3 warnings")
        await interaction.response.send_message(f"{member.mention} has been banned from the server for reaching 3 warnings")

        # clear warnings after ban
        del self.warn_data[user_id]
        self.save_warnings()
        return
      
      except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to ban this user", ephemeral=True)
        return

    await interaction.response.send_message(f"{member.mention} has been warned\nReason: {reason}\nTotal warnings: {warn_count}")

  # warnings
  @app_commands.command(name="warnings", description="Check the number of warnings of a member")
  @app_commands.checks.has_permissions(manage_messages=True)
  async def warnlist(self, interaction: discord.Interaction, member: discord.Member):
    if not self.is_mod(interaction):
      await interaction.response.send_message("You are not a mod/admin", ephemeral=True)
      return
    
    user_id = str(member.id)
    warns = self.warn_data.get(user_id, [])

    if not warns:
      await interaction.response.send_message(f"{member.mention} has no warnings")
      return
    
    warning_list = "\n\n".join([
      f"{index+1}) "
      f"Reason: {warn['reason']}\n"
      f"Moderator: {warn['moderator']}\n"
      f"Time: {warn['time']}"
      for index, warn in enumerate(warns)
    ])

    await interaction.response.send_message(f"Warnings for {member.mention}:\n{warning_list}")

  # clear warns
  @app_commands.command(name="clearwarns", description="Clear all warnings from a member")
  @app_commands.checks.has_permissions(manage_messages=True)
  async def clearwarns(self, interaction: discord.Interaction, member: discord.Member):
    if not self.is_mod(interaction):
      await interaction.response.send_message("You are not a mod/admin", ephemeral=True)
      return
    
    user_id = str(member.id)

    if user_id in self.warn_data:
      del self.warn_data[user_id]
      self.save_warnings()
      await interaction.response.send_message(f"Cleared all warnings for {member.mention}")
    else:
      await interaction.response.send_message(f"{member.mention} has no warnings")

  # remove warn
  @app_commands.command(name="removewarn", description="Remove a specific warning from a member")
  @app_commands.checks.has_permissions(manage_messages=True)
  async def removewarn(self, interaction: discord.Interaction, member: discord.Member, warning_number: int):
    if not self.is_mod(interaction):
      await interaction.response.send_message("You are not a mod/admin", ephemeral=True)
      return
    
    user_id = str(member.id) 

    if user_id not in self.warn_data or not self.warn_data[user_id]:
      await interaction.response.send_message(f"{member.mention} has no warnings", ephemeral=True)
      return
    
    warns = self.warn_data[user_id]

    if warning_number < 1 or warning_number > len(warns):
      await interaction.response.send_message(f"Invalid warning number\nThis user only have {len(warns)} warning(s)", ephemeral=True)
      return
    
    removed_warn = warns.pop(warning_number-1)

    if not warns:
      del self.warn_data[user_id]
    
    self.save_warnings()

    await interaction.response.send_message(f"Removed warning #{warning_number} from {member.mention}\nReason: {removed_warn['reason']}")

async def setup(bot):
  await bot.add_cog(Moderation(bot))