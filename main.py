import asyncio
import json
import os
import random
import re
from datetime import datetime
from discord import app_commands
from discord.ext import commands, tasks
from blue_birthday import birthday_messages, bReplies, xeroBday, messages, replies, special_birthday_wish, error_messages
from tictactoe import TicTacToeGame, TicTacToeView
import discord
from uttt import UltimateTicTacToe,MiniBoardView
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True

# client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)
BIRTHDAYS_FILE = "birthdays.json"
        
@bot.command()
async def tictactoe(ctx, opponent: discord.Member):
    if opponent.bot:
        await ctx.send("You can't play against a bot!")
        return

    game = TicTacToeGame(ctx.author, opponent)
    view = TicTacToeView(game)
    await ctx.send(f"Tic Tac Toe game started between {ctx.author.mention} and {opponent.mention}!", view=view)

@bot.command()
async def utt(ctx,opponent:discord.Member):
    if opponent.bot:
        await ctx.send("You can't play against a bot!")
        return
    game = UltimateTicTacToe(ctx.author,opponent)
    view = MiniBoardView(game)
    await ctx.send(content="Game started! Choose a board to play on:", file=discord.File("board.png"), view=view)
def load_birthdays():
    if not os.path.exists(BIRTHDAYS_FILE) or os.stat(BIRTHDAYS_FILE).st_size == 0:
        # If the file doesn't exist or is empty, initialize it with an empty dictionary
        with open(BIRTHDAYS_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(BIRTHDAYS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Function to save birthdays
def save_birthdays(birthdays):
    with open(BIRTHDAYS_FILE, "w") as f:
        json.dump(birthdays, f)

# Keep track of whether the birthday wish has been sent
user_special_wish_sent = {}

ALLOWED_CHANNEL_ID = 1285525471353765952
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

async def send_with_typing(channel, content, delay=2):
        # Split the content into parts based on sentence delimiters ('.' or '?')
    parts = re.split(r'(?<=[.!?]) ', content)  # Split on '. ' or '? ' while keeping the delimiters

    for part in parts:
        if part.strip():  # Ensure no empty message is sent
            async with channel.typing():
                await asyncio.sleep(delay)  # Simulate typing for the specified delay
            await channel.send(part.strip())  # Send the message
@bot.event
async def on_message(message):
    global birthday_wish_sent
    if message.author == bot.user:
        return
    await bot.process_commands(message)
    # if message.channel.id != ALLOWED_CHANNEL_ID:
    #     return
    # await bot.process_commands(message)
    m = message.content.lower()
    today = datetime.now()

    if message.author.id == 607177303956520961:  # Blue Catto's Discord user ID
        if message.created_at.month == 12 and message.created_at.day == 20:  # Check if today is her birthday
            if message.author.id not in user_special_wish_sent:
                # Send the special birthday wish the first time
                await send_with_typing(message.channel, special_birthday_wish)
                user_special_wish_sent[message.author.id] = True
            else:
                for x in ['thank you','thanks', 'arigatou','arigato']:
                    if m.startswith(x):
                        reply = random.choice(bReplies)
                        await send_with_typing(message.channel, reply)
                        return
                # Send a random birthday message afterward
                reply = random.choice(xeroBday)
                await send_with_typing(message.channel, reply)
            return

    # Your regular responses
    if 'your mom' in m:
        await message.channel.send('no you')
        return
    if 'car ' in m:
        await message.channel.send('<@1226080566617575424>, <@811093597407281174> called you!')
        return
    if 'gandalf' in m:
        await message.channel.send('<@811093597407281174> someone called you!')
        return
    if 'fuck you' in m:
        await message.channel.send('nah fuck you bitch!')
        return
    for x in ['hello', 'hi', 'hey', 'hi hi hi', 'wsg', 'hai', 'sup', 'wsp', 'wassup', 'yo', 'hey', 'whats up', 
              'what up', 'what is up', 'what is going on', 'konnichiwa', 'hola', 'bonjour', 'salut', 'ciao', 
              'aloha', 'privet', 'hallo']:
        if m.startswith(x):
            await message.channel.send(random.choice(messages))
            return
    if 'toe' in m:
        await message.channel.send(random.choice(replies))

@bot.tree.command(name="hello", description="Say hello to the bot!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello, {interaction.user.mention}! 👋")

#birthday commands
@bot.tree.command(name="setbirthday", description="Set your birthday")
@app_commands.describe(day="Your birth day (1-31)",month="Your birth month (1-12)")
async def setbirthday(interaction: discord.Interaction, day: int, month: int):
    if month == 2 and day > 29:
        await interaction.response.send_message("February has a maximum of 29 days dumbass")
        return
    try:
        datetime.strptime(f"{day}-{month}", "%d-%m")
        # Validate the date
    except ValueError:
        await interaction.response.send_message(random.choice(error_messages))
        return
    user_id = str(interaction.user.id)
    birthdays = load_birthdays()
    birthdays[user_id] = f"{day:02d}-{month:02d}"
    save_birthdays(birthdays)
    await interaction.response.send_message(f"Fine! Your birthday has been set to {day:02d}-{month:02d}. You can forget it now.")
    

# Slash command to check someone's birthday
@bot.tree.command(name="birthday", description="Check someone's birthday")
@app_commands.describe(user="The user whose birthday you want to check")
async def birthday(interaction: discord.Interaction, user: discord.User | None = None):
    user_id = str(user.id if user else interaction.user.id)
    birthdays = load_birthdays()

    if user_id in birthdays:
        if user:
            print(user)
            await interaction.response.send_message(f"{user.name}'s birthday is on {birthdays[user_id]}! 🎂")
        else:
            await interaction.response.send_message(f"Your birthday is set to {birthdays[user_id]}. 🎉")
    else:
        if user:
            await interaction.response.send_message(f"I don't have {user.name}'s birthday saved.")
        else:
            await interaction.response.send_message("You haven't set your birthday yet! Use `/setbirthday` to set it.")

@bot.tree.command(name="uttt",description="Play Ultimate Tic Tac Toe")
@app_commands.describe(opponent="Who you wanna play with?")
async def uttt(interaction: discord.Interaction, opponent: discord.Member):
    if opponent.bot:
        await interaction.response.send_message("You can't play against a bot!", ephemeral=True)
        return

    game = UltimateTicTacToe(interaction.user, opponent)
    view = MiniBoardView(game)

    await interaction.response.send_message(
        content="Game started! Choose a board to play on:",
        file=discord.File("board.png"),
        view=view
    )

bot.run(os.environ['TOKEN'])
