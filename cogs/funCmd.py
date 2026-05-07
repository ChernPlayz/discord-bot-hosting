import discord, random
from discord.ext import commands
from discord import app_commands

class Fun(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  # Prefix commands
  @commands.command()
  async def hello(self, ctx):
    await ctx.send("Hello World! :D")

  # Slash commands
  @app_commands.command(name="hello", description="Sends a 'Hi! :D' to the user")
  async def hello(self, interaction: discord.Interaction, hooman: discord.Member):
    await interaction.response.send_message(f"Hi! {hooman.mention} :D")

  @app_commands.command(name="print", description="Print any message")
  async def printSth(self, interaction: discord.Interaction, msg: str):
    await interaction.response.send_message(msg)

  @app_commands.command(name="rng", description="Random generate a number")
  async def rng(self, interaction: discord.Interaction, lowest_num: int, highest_num: int):
    if lowest_num > highest_num:
      await interaction.response.send_message("Lowest number cannot be greater than highest number")
      return
    
    result = random.randint(lowest_num, highest_num)
    await interaction.response.send_message(f"The number is {result}")

async def setup(bot):
  await bot.add_cog(Fun(bot))