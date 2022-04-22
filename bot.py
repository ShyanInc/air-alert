import os
import asyncio
import configparser
import ChannelMessages
import discord
 
from datetime import datetime
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import (
    PeerChannel
)
from discord.ext.commands import Bot
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']
alert_data_channel = config['Telegram']['link']
command_prefix = config['Telegram']['command_prefix']
# Create the client and connect
client = TelegramClient(username, int(api_id), api_hash)

# Create the discord bot
bot = Bot(command_prefix=command_prefix)

started = False
alert_status = False


@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    channels = bot.get_all_channels()
    connected = False
    for channel in channels:
        if str(channel.type) == "voice":
            if channel.voice_states.keys():
                await channel.connect()
                connected = True
    if not connected:
        await ctx.send("No one is connected to the voice channel!", delete_after=5)
        return None


@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    try:
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
        else:
            pass
    except AttributeError:
        await ctx.send("I'm not connected!", delete_after=5)


@bot.command(name='play', help='To play')
async def play(ctx):
    try:
        await ctx.invoke(bot.get_command('join'))
        global alert_status
        if alert_status:
            audio_file = "alarm.mp3"
        else:
            audio_file = "alarm_cancel.mp3"

        server = ctx.message.guild
        voice_channel = server.voice_client
        async with ctx.typing():
            audio_source = discord.FFmpegPCMAudio(audio_file)
            voice_channel.play(source=audio_source)
            await asyncio.sleep(10)

        await ctx.invoke(bot.get_command('leave'))
    except AttributeError:
        pass


@bot.command()
async def start(ctx):
    global alert_data_channel
    await client.start()
    print("Client Created")
    # Ensure you're authorized
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    me = await client.get_me()

    if alert_data_channel.isdigit():
        entity = PeerChannel(int(alert_data_channel))
    else:
        entity = alert_data_channel

    my_channel = await client.get_entity(entity)

    global started
    global alert_status
    if not started:
        started = True
        print("Started!")
        i = 0
        new_client = False
        while True:
            status = await ChannelMessages.run(client, my_channel)
            if (datetime.now().hour == 2 and datetime.now().minute == 1 and not new_client) or (datetime.now().hour == 14 and datetime.now().minute == 1 and not new_client):
                await client.start()
                status = await ChannelMessages.run(client, my_channel)
                print("New client created!")
                new_client = True
                await ctx.send("New client created!", delete_after=30)
            if (datetime.now().hour == 2 and datetime.now().minute == 2) or (datetime.now().hour == 14 and datetime.now().minute == 2):
                new_client = False
            if status == "Alert" and not alert_status:
                alert_status = True
                await ctx.send("Повітряна тривога в Житомирськiй Областi!")
                await ctx.invoke(bot.get_command('play'))
            elif status == "Alert_Stop" and alert_status:
                alert_status = False
                await ctx.send("Вiдбiй тривоги в Житомирськiй Областi!")
                await ctx.invoke(bot.get_command('play'))
            i += 1
            print(status + ": " + str(i))
            status = ""
            await asyncio.sleep(15)
    else:
        await ctx.send("I'm already started :)")


@bot.command()
async def force_stop(ctx):
    if str(ctx.message.author) == "Shyan#6983":
        exit(0)


bot.run(TOKEN)

