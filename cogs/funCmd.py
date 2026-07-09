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

  @commands.command()
  async def choose(self, ctx, *choices: str):
    if len(choices) < 2:
      await ctx.send("Input at least 2 options")
      return

    randChoice = random.choice(choices)
    await ctx.send(randChoice)

  # Slash commands
  @app_commands.command(name="hello", description="Sends a 'Hi! :D' to the user")
  async def hello(self, interaction: discord.Interaction, hooman: discord.Member):
    await interaction.response.send_message(f"Hi! {hooman.mention} :D")

  @app_commands.command(name="print", description="Print any message")
  async def printSth(self, interaction: discord.Interaction, msg: str):
    await interaction.response.send_message(msg)

  @app_commands.command(name="choose", description="Randomly choose 1 of the option")
  @app_commands.describe(options="Enter your options separated by commas (e.g. pizza, burgers, sushi)")
  async def choose(self, interaction: discord.Interaction, options: str):
    options_list = [option.strip() for option in options.split(",") if option.strip()]
    if len(options_list) < 2:
      await interaction.response.send_message("Please input at least 2 options separated by commas", ephemeral=True)
      return
    
    randChoice = random.choice(options_list)
    await interaction.response.send_message(randChoice)

  @app_commands.command(name="kill", description="Kill anyone you hate >:)")
  async def kill(self, interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(f"{interaction.user.mention} killed {user.mention} 🔪")

  @app_commands.command(name="kik", description="Kik people")
  async def kik(self, interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(f"{user.mention} has been kiked from the server")

  @app_commands.command(name="bon", description="Bon ppl")
  async def bon(self, interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(f"{user.mention} has been bonned from the server")
  
  @app_commands.command(name="gay", description="Rate how gay is a person")
  async def gay(self, interaction: discord.Interaction, user: discord.Member):
    randNum = random.randint(0,100)
    await interaction.response.send_message(f"{user.mention} is {randNum}% gay")

  @app_commands.command(name="ship", description="Ship 2 person together")
  async def ship(self, interaction: discord.Interaction, user1: discord.Member, user2: discord.Member):
    randNum = random.randint(0,100)

    if randNum < 20:
      result = "Absolute disaster. Stay away from each other."
    elif randNum < 50:
      result = "Friendzone territory. Roommates at best."
    elif randNum < 75:
      result = "There's a spark here! Keep talking."
    elif randNum < 90:
      result = "A match made in heaven. Go get 'em!"
    else:
      result = "Soulmates. Wedding bells are ringing!"
    
    await interaction.response.send_message(
      f"Compatibility: {randNum}%\n"
      f"{user1.mention} X {user2.mention}\n"
      f"{result}"
    )

  @app_commands.command(name="rng", description="Random generate a number")
  async def rng(self, interaction: discord.Interaction, lowest_num: int, highest_num: int):
    if lowest_num > highest_num:
      await interaction.response.send_message("Lowest number cannot be greater than highest number")
      return
    
    result = random.randint(lowest_num, highest_num)
    await interaction.response.send_message(f"The number is {result}")

async def setup(bot):
  await bot.add_cog(Fun(bot))