import os
import asyncio
import alert
import discord

from yt_dlp import YoutubeDL
from discord.ext.commands import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = Bot(command_prefix="!")

alert_status = False
started = False

@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='play', help='To play')
async def play(ctx):
    await ctx.invoke(bot.get_command('join'))
    global alert_status
    if alert_status:
        audio_file = "alarm.mp3"
    else:
        audio_file = "alarm_cancel.mp3"
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        async with ctx.typing():
            audio_source = discord.FFmpegPCMAudio(audio_file)
            voice_channel.play(source=audio_source)
            await asyncio.sleep(7)
    except:
        await ctx.send("The bot is not connected to a voice channel.")
    await ctx.invoke(bot.get_command('leave'))


@bot.command()
async def start(ctx):
    global started
    global alert_status
    if not started:
        started = True
        print("Started!")
        i = 0
        while True:
            status = await alert.get_status()
            if status == "Alert" and not alert_status:
                alert_status = True
                await ctx.send("Тривога в Житомирська область!")
                # await ctx.send("Тривога в Житомирськiй Областi!")
                await ctx.invoke(bot.get_command('play'))
            elif status == "No_Alert" and alert_status:
                alert_status = False
                await ctx.send("Вiдбiй тривоги в Житомирська область!")
                # await ctx.send("Вiдбiй тривоги в Житомирськiй Областi!")
                await ctx.invoke(bot.get_command('play'))
            i += 1
            print(status + str(i))
            status = ""
            await asyncio.sleep(15)
    else:
        await ctx.send("I'm already started :)")


@bot.command()
async def stop(ctx):
    exit(0)


bot.run(TOKEN)
