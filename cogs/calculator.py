import discord, math, re
from discord.ext import commands
from discord import app_commands

class Calculator(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.ans_memory = {}

  def evaluate(self, user_id: int, expression: str):
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

    ans = self.ans_memory.get(user_id, 0)

    expression = expression.replace("^","**")
    expression = expression.replace("Ans", str(ans))

    if not re.match(r"^[0-9+\-*/().,\sA-Za-z_**]*$", expression):
      return "Invalid characters"

    try:
      result = eval(expression, {"__builtins__": {}}, allowed_names)
      self.ans_memory[user_id] = result
      return result
    
    except Exception as err:
      return f"Error: {err}"

  @app_commands.command(name="calc", description="Type in any calculation")
  async def calculator(self, interaction: discord.Interaction, expression: str):
    result = self.evaluate(interaction.user.id, expression)
    await interaction.response.send_message(result)

async def setup(bot):
  await bot.add_cog(Calculator(bot))