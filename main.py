import discord, logging, os, asyncio
from discord.ext import commands
from dotenv import load_dotenv
from webserver import keep_alive

load_dotenv()
token = os.getenv("TOKEN")

keep_alive()

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
guild = discord.Object(id=1156550837993222295)

async def loadCogs():
  for fileName in os.listdir("Discord Bot/cogs"):
    if fileName.endswith(".py"):
      try:
        await bot.load_extension(f"cogs.{fileName[:-3]}")
        print(f"Loaded cog: {fileName}")
      except Exception as err:
        print(f"Failed to load {fileName}: {err}")

# Bot logging in
@bot.event
async def on_ready():
  print(f"{bot.user.name} has logged in!")

  try:
    bot.tree.copy_global_to(guild=guild)
    synced = await bot.tree.sync(guild=guild)
    print(f"Synced {len(synced)} commands to guild {guild.id}")
  except Exception as errMsg:
    print(f"Error syncing commands: {errMsg}")
    
# Member joined
@bot.event
async def on_member_join(member):
  await member.send(f"Welcome to the server! {member.name}")

async def setup_hook():
  await loadCogs()

bot.setup_hook = setup_hook
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
"""
# Add reaction
@bot.event
async def on_reaction_add(reaction, user):
  if user.bot:
    return
  
  guild = reaction.message.guild
  if not guild:
    return
  
  if reaction.message.id != getattr(bot, "gender_role_message_id"):
    return
  
  emoji = str(reaction.emoji)
  reaction_role_map = {
    "♂️": "Male",
    "♀️": "Female",
    "🤔": "SUS"
  }

  if emoji in reaction_role_map:
    role_name = reaction_role_map[emoji]
    role = discord.utils.get(guild.roles, name=role_name)

    if role and user:
      await user.add_roles(role)

# Remove reaction
@bot.event
async def on_reaction_remove(reaction, user):
  if user.bot:
    return
  
  guild = reaction.message.guild
  if not guild:
    return
  
  if reaction.message.id != getattr(bot, "gender_role_message_id"):
    return
  
  emoji = str(reaction.emoji)
  reaction_role_map = {
    "♂️": "Male",
    "♀️": "Female",
    "🤔": "SUS"
  }

  if emoji in reaction_role_map:
    role_name = reaction_role_map[emoji]
    role = discord.utils.get(guild.roles, name=role_name)

    if role and user:
      await user.remove_roles(role)

# Prefix Commands

secret_role = "ded"
@bot.command()
async def assign(ctx):
  role = discord.utils.get(ctx.guild.roles, name=secret_role)
  if role:
    await ctx.author.add_roles(role)
    await ctx.send(f"{ctx.author.mention} is now assigned to {secret_role}")

# Slash Commands
@bot.tree.command(name="embed", description="Embed anything", guild=GUILD_ID)
async def embed(interaction: discord.Interaction):
  embed = discord.Embed(title="This is a title", 
                        url="https://google.com", 
                        description="This is a description",
                        color=discord.Color.from_rgb(255,0,0))
  embed.set_thumbnail(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT-p4iUe6m_eaREf2mxj-FdduAGGdtrzelOWA&s")
  embed.add_field(name="Field 1 Title", value="EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", inline=False)
  embed.add_field(name="Field 2 Title", value="EEEEEE", inline=True)
  embed.add_field(name="Field 3 Title", value="EEEEEE", inline=True)
  embed.set_footer(text="This is a footer")
  embed.set_author(name=f"By {interaction.user.name}", url="https://google.com", icon_url="https://png.pngtree.com/png-vector/20230912/ourmid/pngtree-line-circle-png-png-image_10023727.png")
  await interaction.response.send_message(embed=embed)

class View(discord.ui.View):
  @discord.ui.button(label="Click me!", style=discord.ButtonStyle.red, emoji="🔥")
  async def btn_callback1(self, interaction: discord.Interaction, btn: discord.ui.Button):
    await interaction.response.send_message(f"{interaction.user.name} have clicked the fire btn!")

  @discord.ui.button(label="Click me!", style=discord.ButtonStyle.green, emoji="🌲")
  async def btn_callback2(self, interaction: discord.Interaction, btn: discord.ui.Button):
    await interaction.response.send_message(f"{interaction.user.name} have clicked the tree btn!")

@bot.tree.command(name="btn", description="Button", guild=GUILD_ID)
async def btn(interaction: discord.Interaction):
    await interaction.response.send_message(view=View())

class Menu(discord.ui.Select):
  def __init__(self):
    options = [
      discord.SelectOption(
        label="Option 1",
        description="This is option 1",
        emoji="🍉"
      ),
      discord.SelectOption(
        label="Option 2",
        description="This is option 2",
        emoji="🍋"
      )
    ]

    super().__init__(placeholder="Please choose an option: ", min_values=1, max_values=1, options=options)

  async def callback(self, interaction:discord.Interaction):
    await interaction.response.send_message(f"You picked {self.values[0]}", ephemeral=True)

class MenuView(discord.ui.View):
  def __init__(self):
    super().__init__()
    self.add_item(Menu())

@bot.tree.command(name="menu", description="Displaying a drop down menu", guild=GUILD_ID)
async def myMenu(interaction: discord.Interaction):
    await interaction.response.send_message(view=MenuView())

@bot.tree.command(name="genderroles", description="Create a message that let users pick a gender role", guild=GUILD_ID)
async def gender_roles(interaction: discord.Interaction):
  # Check admin
  if not interaction.user.guild_permissions.administrator:
    await interaction.response.send_message("You must be an admin to run this command", ephemeral=True)
    return
  
  await interaction.response.defer(ephemeral=True)

  description = (
    "React to this message to get your gender role!\n\n"
    "♂️ Male\n"
    "♀️ Female\n"
    "🤔 SUS"
  )

  embed = discord.Embed(title="Pick your gender!", description=description, color=discord.Color.blurple())
  message = await interaction.channel.send(embed=embed)

  emojis = ['♂️','♀️','🤔']

  for emoji in emojis:
    await message.add_reaction(emoji)
  
  bot.gender_role_message_id = message.id
  await interaction.followup.send("Gender role message created!", ephemeral=True)
"""