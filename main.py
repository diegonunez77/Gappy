import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup

bot = commands.Bot(command_prefix='!')

def get_win_rate(role):
    url = f'https://www.op.gg/role/statistics/{role}/winrate'

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        win_rate = soup.select_one('.win-rate-selector').text
        return win_rate
    except Exception as e:
        return 'Error retrieving data.'

@bot.command()
async def adcwr(ctx):
    win_rate = get_win_rate('adc')
    await ctx.send(f'ADC Win Rate: {win_rate}')

@bot.command()
async def suppwr(ctx):
    win_rate = get_win_rate('support')
    await ctx.send(f'Support Win Rate: {win_rate}')

@bot.command()
async def midwr(ctx):
    win_rate = get_win_rate('mid')
    await ctx.send(f'Mid Win Rate: {win_rate}')

@bot.command()
async def jgwr(ctx):
    win_rate = get_win_rate('jungle')
    await ctx.send(f'Jungle Win Rate: {win_rate}')

@bot.command()
async def topwr(ctx):
    win_rate = get_win_rate('top')
    await ctx.send(f'Top Win Rate: {win_rate}')

bot.run('MTE3OTIyOTU4MTMxMjUzMjU4MQ.GdRjfH.uz1QjKreEblaPvdcFZ2FYxp6ZP7NtuNGYZ7L9Q')
