import discord, datetime
from discord.ext import commands
from discord import app_commands
from typing import Optional

class Polls(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="poll", description="Create a poll, separate options by ,")
  async def poll(self, interaction: discord.Interaction, question: str, choices: Optional[str]=None, duration_days: Optional[int]=1, duration_hrs: Optional[int]=0, multiple_select: Optional[bool]=False):
    # No choices
    if choices is None:
      msg = await interaction.channel.send(question)
      await msg.add_reaction("👍")
      await msg.add_reaction("👎")
      await interaction.response.send_message("Your question has been posted!", ephemeral=True)
      return
    
    # Have choices
    choice_list = [choice.strip() for choice in choices.split(",") if choice.strip()]

    if len(choice_list) < 2:
      await interaction.response.send_message("You must provide at least 2 choices separated by a comma.", ephemeral=True)
      return
    
    if len(choice_list) > 10:
      await interaction.response.send_message("Discord native polls only support up to 10 choices.", ephemeral=True)
      return
    
    total_hrs = (duration_days*24) + duration_hrs
    hours = max(1, min(total_hrs, 168))
    poll = discord.Poll(question=question, duration=datetime.timedelta(hours=hours), multiple=multiple_select)
    
    for choice in choice_list:
      poll.add_answer(text=choice)

    await interaction.channel.send(poll=poll)
    await interaction.response.send_message("Your poll has been created!", ephemeral=True)

async def setup(bot):
  await bot.add_cog(Polls(bot))