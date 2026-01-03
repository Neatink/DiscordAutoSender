from datetime import datetime,timedelta
from configparser import ConfigParser
from colorama import Fore,init,Style
from discord.ext import tasks
from pathlib import Path
import discord
import json
import os

systemCLS = lambda: os.system('clear')
getDatetime = lambda: f"{Fore.BLACK}{Style.BRIGHT}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]{Style.RESET_ALL}"

init(autoreset=True)
client = discord.Client()
config_parser = ConfigParser()

config_folder_path = Path('configs')
config_path = f'{config_folder_path}/main.cfg'

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
        print(getDatetime(),Fore.LIGHTBLUE_EX+'Balance:')
        for field in channel_history.embeds[0].fields:
            print(getDatetime(),Fore.LIGHTYELLOW_EX+field.name,Fore.LIGHTGREEN_EX+field.value[27:])
      
@client.event
async def on_ready():
    textbal = f'{getDatetime()}{Fore.GREEN} -----------------------------------'
    systemCLS()
    print(f'{getDatetime()} {Fore.MAGENTA}{Style.BRIGHT}Username: {Style.RESET_ALL}{Fore.CYAN}{client.user.name}')
    print(f'{getDatetime()} {Fore.MAGENTA}{Style.BRIGHT}User ID: {Style.RESET_ALL}{Fore.CYAN}{client.user.id}')
    print(textbal)
    await getCurrentBalance()
    print(textbal)
    if not collects_commands.is_running():
        collects_commands.start()        
        
@tasks.loop(minutes=0,seconds=5)
async def collects_commands():
    collects_commands.change_interval(minutes=0,seconds=5)
    target_channel_id = getValueConfig('Discord','Target_channel_id')
    try:
        channel = client.get_channel(int(target_channel_id))
    except:
        systemCLS()
        print(f'{getDatetime()} {Fore.RED}Failed to get channel ID')
        enterChannelID()
    if channel:
        try:
            await channel.send('+collect')
            print(f"{getDatetime()} {Fore.CYAN}'+collect' {Fore.GREEN}send")
            
            await channel.send('+work')
            print(f"{getDatetime()} {Fore.CYAN}'+work' {Fore.GREEN}send")
            
            channel_history = await getHistoryChannel()
            
            if not channel_history:
                return
            
            if channel_history.embeds:
                channel_last_message = channel_history.embeds[0].description
            else:
                channel_last_message = channel_history.content 
            
            changeInterval(channel_last_message)

            await channel.send('+dep all')
            print(f"{getDatetime()} {Fore.CYAN}'+dep all' {Fore.GREEN}send")
        except:
            print(f"{getDatetime()}{Fore.RED} Сan't send a message!{Fore.LIGHTYELLOW_EX}(Try again in 10 seconds...)")
            collects_commands.change_interval(minutes=0,seconds=10)
            return
    else:
        enterChannelID()

async def getHistoryChannel():
    async for msg in client.get_channel(int(getValueConfig('Discord','Target_channel_id'))).history(limit=1):
        if msg:
            if msg.author.name != client.user.name:
                return msg
            else:
                return

def changeInterval(last_message):
    seconds_minutes = []
    for number in last_message.split():
        if number.isdigit():
            seconds_minutes.append(number)
    try:
        time_predict = datetime.now()+timedelta(minutes=int(seconds_minutes[0]),seconds=int(seconds_minutes[1]))
        print(f'{getDatetime()} {Fore.MAGENTA}Next message in {Fore.CYAN}{seconds_minutes[0]}{Fore.MAGENTA} minutes and {Fore.CYAN}{seconds_minutes[1]}{Fore.MAGENTA} seconds{Fore.LIGHTBLACK_EX} ({time_predict.strftime('%H:%M:%S')})')
        collects_commands.change_interval(minutes=int(seconds_minutes[0]),seconds=int(seconds_minutes[1]))
    except:
        print(f'{getDatetime()} {Fore.RED}Failed to check interval')

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
        systemCLS()
        standartConfigSettings()
        try:
            discord_token = str(input(f"{getDatetime()} {Fore.BLUE}{Style.BRIGHT}Discord token: "))
            config_save(f"Discord_token : {discord_token}\n")
            enterChannelID()
        except discord.errors.LoginFailure:
            close_app(" Enter correct discord token!")