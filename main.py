from datetime import datetime,timedelta
from configparser import ConfigParser
from colorama import Fore,init,Style
from random import shuffle, randint
from discord.ext import tasks
from pathlib import Path
import discord
import asyncio
import json
import os

letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

getDatetime = lambda: f"{Fore.BLACK}{Style.BRIGHT}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]{Style.RESET_ALL}"

init(autoreset=True)
client = discord.Client()
config_parser = ConfigParser()

config_folder_path = Path('configs')
config_path = f'{config_folder_path}/main.cfg'

collect_timer = datetime.now().timestamp()
work_timer = datetime.now().timestamp()

def standartConfigSettings():
    with open(config_path, 'w', encoding='utf-8') as danger_text:
        danger_text.write('# DO NOT SHARE THIS FILE WITH ANYONE AS IT CONTAINS YOUR DISCORD TOKEN WHICH CAN BE USED TO LOG INTO YOUR ACCOUNT! #\n')
        danger_text.write('[Discord]\n')

if not config_folder_path.exists():
    config_folder_path.mkdir(parents=True)
    standartConfigSettings()

def getValueConfig(section, value):
    config_parser.read(config_path, encoding='utf-8')
    try:
        return json.loads(config_parser.get(section, value))
    except:
        return config_parser.get(section, value)

def config_save(text):
    with open(config_path, 'r+', encoding='utf-8') as config:
        config.seek(0, 2)
        config.write(text)
    
def close_app(message):
    print(Style.RESET_ALL + getDatetime() + Fore.RED + message)
    exit(1)
   
async def getCurrentBalance():
    channel = client.get_channel(int(getValueConfig('Discord','Target_channel_id')))
    await channel.send('+bal')
    
    channel_history = await getHistoryChannel()
    
    if not channel_history:
        return
    
    if channel_history.embeds:
        print(f"{getDatetime()} {Fore.LIGHTBLUE_EX}Balance:")
        for field in channel_history.embeds[0].fields:
            print(f"{getDatetime()} {Fore.LIGHTYELLOW_EX} {field.name} {Fore.LIGHTGREEN_EX} {field.value[27:]}")

async def antiSpamWithLetter(channel):
    shuffle(letters)
    random_letter = letters[randint(0,25)]
    temp_letter = await channel.send(random_letter)
    print(f"{getDatetime()} {Fore.CYAN}random letter('{random_letter}'){Style.RESET_ALL} {Fore.GREEN}send")
    await asyncio.sleep(1)
    await temp_letter.delete()
    print(f"{getDatetime()} {Fore.CYAN}random letter('{random_letter}'){Fore.RED} was deleted")

@client.event
async def on_ready():
    textbal = f'{getDatetime()}{Fore.GREEN} -----------------------------------'
    print(f'{getDatetime()} {Fore.MAGENTA}{Style.BRIGHT}Username: {Style.RESET_ALL}{Fore.CYAN}{client.user.name}')
    print(f'{getDatetime()} {Fore.MAGENTA}{Style.BRIGHT}User ID: {Style.RESET_ALL}{Fore.CYAN}{client.user.id}')
    print(textbal)
    await getCurrentBalance()
    print(textbal)
    if not collects_commands.is_running():
        collects_commands.start()        
        
@tasks.loop(hours=0, minutes=0, seconds=5)
async def collects_commands():
    collects_commands.change_interval(hours=0, minutes=0, seconds=5)
    target_channel_id = getValueConfig('Discord','Target_channel_id')
    try:
        channel = client.get_channel(int(target_channel_id))
    except:
        print(f'{getDatetime()} {Fore.RED}Failed to get channel ID')
        enterChannelID()
    if channel:
        try:
            global collect_timer, work_timer
            current_date = datetime.now().timestamp()
            
            await asyncio.sleep(2)

            while collect_timer is None or collect_timer < current_date:
                await antiSpamWithLetter(channel)
                
                await channel.send('+collect')
                print(f"{getDatetime()} {Fore.CYAN}'+collect' {Fore.GREEN}send")
                
                await asyncio.sleep(3)
                
                collect_timer = await getCollectTime(await getLastMessage())
                
                if collect_timer is not None and collect_timer >= current_date:
                    break
                
            await asyncio.sleep(3)

            while work_timer is None or work_timer < current_date:
                await antiSpamWithLetter(channel)

                await channel.send('+work')
                print(f"{getDatetime()} {Fore.CYAN}'+work' {Fore.GREEN}send")
                
                await asyncio.sleep(3)
                
                work_timer = await getWorkTime(await getLastMessage())
                
                if work_timer is not None and work_timer >= current_date:
                    break
        
        except EOFError as error:
            print(f"{getDatetime()}{Fore.RED} Сant send a message!{Fore.LIGHTYELLOW_EX}(Try again in 10 seconds...){Fore.RED}(Error:{error})")
            collects_commands.change_interval(hours=0, minutes=0, seconds=10)
            return
    else:
        enterChannelID()

async def getLastMessage():
    channel_history = await getHistoryChannel()
    
    if not channel_history:
        return
            
    if channel_history.embeds:
        channel_last_message = channel_history.embeds[0].description
    else:
        channel_last_message = channel_history.content
        
    return channel_last_message

async def getCollectTime(last_message):
    text1 = float(last_message.split("<t:")[1].split(":")[0])
    current_time = datetime.now()
    total_seconds = text1 - current_time.timestamp() + 3
    try:
        totals = datetime(1, 1, 1) + timedelta(seconds=(total_seconds))
    except:
        return None
    timepredict = current_time + timedelta(seconds=(total_seconds))
    print(f'{getDatetime()} {Fore.MAGENTA}Collect message in {Fore.CYAN}{totals.hour}{Fore.MAGENTA} hours {Fore.CYAN}{totals.minute}{Fore.MAGENTA} minutes and {Fore.CYAN}{totals.second}{Fore.MAGENTA} seconds{Fore.LIGHTBLACK_EX} ({timepredict.strftime('%H:%M:%S')})')
    return text1 + 3

async def getWorkTime(last_message):
    current_time = datetime.now()
    seconds_minutes = []
    for number in last_message.split():
        if number.isdigit():
            seconds_minutes.append(int(number))
    try:
        time_predict = current_time + timedelta(minutes=seconds_minutes[0],seconds=seconds_minutes[1])
        print(f'{getDatetime()} {Fore.MAGENTA}Work message in {Fore.CYAN}0{Fore.MAGENTA} hours {Fore.CYAN}{seconds_minutes[0]}{Fore.MAGENTA} minutes and {Fore.CYAN}{seconds_minutes[1]}{Fore.MAGENTA} seconds{Fore.LIGHTBLACK_EX} ({time_predict.strftime('%H:%M:%S')})')
        return (current_time + timedelta(seconds = (0 * 3600 + seconds_minutes[0] * 60 + seconds_minutes[1]))).timestamp()
    except EOFError as error:
        print(f'{getDatetime()} {Fore.RED}Failed to check interval(Error:{error})')
        return None

async def getHistoryChannel():
    async for msg in client.get_channel(int(getValueConfig('Discord','Target_channel_id'))).history(limit=1):
        if msg:
            if msg.author.name != client.user.name:
                return msg
            else:
                return

def enterChannelID():
    try:
        target_channel_id = int(input(f"{getDatetime()} {Fore.BLUE}{Style.BRIGHT}Channel ID: "))
        config_save(f"Target_channel_id : {target_channel_id}\n")
        close_app(f" Restart the app!")
    except ValueError:
        close_app(" Enter only numbers!")
     
if __name__ == "__main__":
    try:
        client.run(getValueConfig('Discord','Discord_token'))
    except:
        standartConfigSettings()
        try:
            discord_token = str(input(f"{getDatetime()} {Fore.BLUE}{Style.BRIGHT}Discord token: "))
            config_save(f"Discord_token : {discord_token}\n")
            enterChannelID()
        except discord.errors.LoginFailure:
            close_app(" Enter correct discord token!")