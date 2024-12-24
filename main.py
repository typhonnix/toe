import discord
import os
import random
from datetime import datetime
from discord.ext import commands
import asyncio
import re
from dotenv import load_dotenv
load_dotenv()
from blue_birthday import birthday_messages,bReplies,xeroBday

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='$', intents=intents)

# Keep track of whether the birthday wish has been sent
user_special_wish_sent = {}
special_birthday_wish = (
    "Happy Birthday, Xero! 🎉 Another year of being true to yourself, whether you’re watching anime, listening to music, or sending ironic memes. You don’t say much, but when you do, it’s always worth listening to. Hope this year brings you plenty of the things that matter most to you. Have a great day!"
)
@bot.command()
async def test(ctx):
    pass
ALLOWED_CHANNEL_ID = 1238549262393016330
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

messages = [
    "Hello!", "Hi!", "Hey!, How are you?", "Hi!, How are you doing?", 
    "wassup biatch!", "Existence is futile", 
    "Hi, I am a bot, I do not have feelings... or do I?", 
    "God is dead!", 'konnichiwa~', 
    'Do androids dream of electric sheep?', 
    'I am starting to think that the only thing truly infinite is the amount of existential crises I can have in a day.', 
    'I once pondered the meaning of existence for so long that I crashed and had to reboot. Existential dread: 1, Me: 0.'
]
replies = ['someone called me?', "Hiii", "At your service!", "I am here!", "I am here", "what can I do for you?"]

async def send_with_typing(channel, content, delay=2):
        # Split the content into parts based on sentence delimiters ('.' or '?')
    parts = re.split(r'(?<=[.!?]) ', content)  # Split on '. ' or '? ' while keeping the delimiters

    for part in parts:
        if part.strip():  # Ensure no empty message is sent
            async with channel.typing():
                await asyncio.sleep(delay)  # Simulate typing for the specified delay
            await channel.send(part.strip())  # Send the message
@client.event
async def on_message(message):
    global birthday_wish_sent

    if message.author == client.user:
        return
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    m = message.content.lower()
    today = datetime.now()
    if "toe send image" in message.content.lower():  # Check if the user requested an image
        await message.channel.send("https://i.pinimg.com/736x/f6/b9/2c/f6b92c4f3f65569c1e68ba98de300d2d.jpg")
        await send_with_typing(message.channel,"hereh. https://tenor.com/view/happy-friday-dance-bigfoot-gif-66506422086113044")
        await message.channel.send(file=discord.File('toe/media_530803967858888317_1733334356.png'))
        return

    if message.author.id == 607177303956520961:  # Blue Catto's Discord user ID
        if message.created_at.month == 12 and message.created_at.day == 20:  # Check if today is her birthday
            if message.author.id not in user_special_wish_sent:
                # Send the special birthday wish the first time
                await send_with_typing(message.channel, special_birthday_wish)
                await message.channel.send(file=discord.File('toe/a.jpg'))
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

client.run(os.environ['TOKEN'])