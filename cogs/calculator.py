import discord, math, re
from discord.ext import commands
from discord import app_commands

class Calculator(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.ans_memory = {}

  def evaluate(self, user_id: int, expression: str):
    builtins = {
      "int": int,
      "float": float,
      "abs": abs,
      "pow": pow,
      "round": round,
    }

    allowed_names = {
      "sin": math.sin,
      "cos": math.cos,
      "tan": math.tan,
      "sqrt": math.sqrt,
      "log": math.log10,
      "ln": math.log,
      "pi": math.pi,
      "e": math.e,
      **builtins
    }

    ans = self.ans_memory.get(user_id, 0)

    expression = expression.replace("ans", str(ans))
    expression = expression.replace("^", "**")
    expression = expression.replace(" ", "")

    if not re.match(r"^[0-9+\-*/().,\sA-Za-z_]*$", expression):
      return "Invalid characters"

    try:
      result = eval(expression, {"__builtins__": builtins}, allowed_names)
      self.ans_memory[user_id] = result
      return result

    except Exception as err:
      return f"Error: {err}"

  @app_commands.command(name="calc", description="Type in any calculation")
  async def calculator(self, interaction: discord.Interaction, expression: str):
    result = self.evaluate(interaction.user.id, expression.lower())
    await interaction.response.send_message(result)

async def setup(bot):
  await bot.add_cog(Calculator(bot))