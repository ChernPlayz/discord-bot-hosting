import discord, math, re
from discord.ext import commands
from discord import app_commands

class Calculator(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  def evaluate(self, expression: str):
    allowed_names = {
      "sin": math.sin,
      "cos": math.cos,
      "tan": math.tan,
      "sqrt": math.sqrt,
      "log": math.log10,
      "ln": math.log,
      "pi": math.pi,
      "e": math.e,
      "abs": abs,
      "pow": pow
    }

    expression = expression.replace("^","**")

    if not re.match(r"^[0-9+\-*/().,\sA-Za-z_**]*$", expression):
      return "Invalid characters"

    try:
      return eval(expression, {"__builtins__": {}}, allowed_names)
    except Exception as err:
      return f"Error: {err}"

  @app_commands.command(name="calc", description="Type in any calculation")
  async def calculator(self, interaction: discord.Interaction, expression: str):
    result = self.evaluate(expression)
    await interaction.response.send_message(result)

async def setup(bot):
  await bot.add_cog(Calculator(bot))