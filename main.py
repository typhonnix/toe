import discord
import os
import random
import json
from datetime import datetime
from discord import app_commands
from discord.ext import commands,tasks
import asyncio
import re
from blue_birthday import birthday_messages, bReplies, xeroBday,messages,replies,special_birthday_wish
intents = discord.Intents.default()
intents.message_content = True

# client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)
BIRTHDAYS_FILE = "birthdays.json"

def load_birthdays():
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

@bot.command()
async def test(ctx):
    pass
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
    await bot.process_commands(message)
    if message.author == bot.user:
        return
    # if message.channel.id != ALLOWED_CHANNEL_ID:
    #     return
    # await bot.process_commands(message)
    m = message.content.lower()
    today = datetime.now()
    if "toe send image" in message.content.lower():  # Check if the user requested an image
        await message.channel.send("Happy Birthday, Xero! Hope you’re stepping into the next year with all the good vibes and, of course, plenty of toes! 🎉🦶")
        await message.channel.send(file=discord.File('media_530803967858888317_1733334356.png'))
        await send_with_typing(message.channel,"hereh. https://tenor.com/view/happy-friday-dance-bigfoot-gif-66506422086113044")
        return

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

# Example of a slash command with arguments
@bot.tree.command(name="add", description="Add two numbers")
@app_commands.describe(a="The first number", b="The second number")
async def add(interaction: discord.Interaction, a: int, b: int):
    result = a + b
    await interaction.response.send_message(f"The sum of {a} and {b} is {result}.")

@bot.command()
async def setbirthday(ctx, date: str):
    """Set your birthday (format: MM-DD)"""
    try:
        datetime.strptime(date, "%m-%d")  # Validate the date format
        user_id = str(ctx.author.id)
        birthdays = load_birthdays()
        birthdays[user_id] = date
        save_birthdays(birthdays)
        await ctx.send(f"Got it! Your birthday has been set to {date}. 🎉")
    except ValueError:
        await ctx.send("Invalid date format! Please use MM-DD.")

# Command to check someone's birthday
@bot.command()
async def birthday(ctx, user: discord.User = None):
    """Check someone's birthday"""
    user_id = str(user.id if user else ctx.author.id)
    birthdays = load_birthdays()

    if user_id in birthdays:
        if user:
            await ctx.send(f"{user.name}'s birthday is on {birthdays[user_id]}! 🎂")
        else:
            await ctx.send(f"Your birthday is set to {birthdays[user_id]}. 🎉")
    else:
        if user:
            await ctx.send(f"Sorry, I don't have {user.name}'s birthday saved.")
        else:
            await ctx.send("You haven't set your birthday yet! Use `!setbirthday MM-DD` to set it.")

# Periodic birthday check to announce today's birthdays
@tasks.loop(hours=24)
async def daily_birthday_check():
    birthdays = load_birthdays()
    today = datetime.now().strftime("%m-%d")
    channel = bot.get_channel(1247280155228115074)  # Replace with the channel ID for announcements

    for user_id, date in birthdays.items():
        if date == today:
            await channel.send(f"🎂 Happy Birthday, <@{user_id}>! 🎉 Have an amazing day!")



bot.run(os.environ['TOKEN'])
