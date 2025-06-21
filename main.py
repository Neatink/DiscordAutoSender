from datetime import datetime
from colorama import Fore,init,Style
from discord.ext import tasks
from pathlib import Path
import discord
import os

minutes = 0
seconds = 3

init(autoreset=True)
client = discord.Client()

config_folder_path = Path('configs')
config_path = f'{config_folder_path}/main.cfg'
config_folder_path.mkdir(parents=True, exist_ok=True)

with open(config_path, 'w', encoding='utf-8') as danger_text:
    danger_text.write('---DO NOT SHARE THIS FILE WITH ANYONE AS IT CONTAINS YOUR DISCORD TOKEN WHICH CAN BE USED TO LOG INTO YOUR ACCOUNT!---')

def config_save(text):
    with open(f'{config_folder_path}/main.cfg', 'r+', encoding='utf-8') as config:
        config.seek(0, 2)
        config.write(text)

def get_datetime():
    return f"{Fore.BLACK}{Style.BRIGHT}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]{Style.RESET_ALL}"
    
def close_app(message):
    print(Style.RESET_ALL + get_datetime() + Fore.RED + message)
    os.system('pause')
    exit(1)
    
@client.event
async def on_ready():
    os.system('cls')
    print(f'{get_datetime()} {Fore.MAGENTA}{Style.BRIGHT}Username: {Style.RESET_ALL}{Fore.CYAN}{client.user.name}')
    print(f'{get_datetime()} {Fore.MAGENTA}{Style.BRIGHT}User ID: {Style.RESET_ALL}{Fore.CYAN}{client.user.id}')
    if not collects_commands.is_running():
        collects_commands.start()
        
@tasks.loop(minutes=minutes,seconds=seconds)
async def collects_commands():
    channel = client.get_channel(int(target_channel_id))
    if channel:
        try:
            await channel.send('+collect')
            print(f"{get_datetime()} {Fore.CYAN}'+collect' {Fore.GREEN}send")
            
            await channel.send('+work')
            print(f"{get_datetime()} {Fore.CYAN}'+work' {Fore.GREEN}send")

            async for msg in channel.history(limit=1):
                if msg.author.name != client.user.name:
                    channel_last_message = msg
                else:
                    return
            
            if channel_last_message.embeds:
                channel_last_message = channel_last_message.embeds[0].description
            else:
                channel_last_message = channel_last_message.content 
            
            changeInterval(channel_last_message)

            await channel.send('+dep all')
            print(f"{get_datetime()} {Fore.CYAN}'+dep all' {Fore.GREEN}send")
        except:
            close_app(" Сan't send a message!") 
    else:
        close_app(" Incorrect channel id!")

def changeInterval(last_message):
    seconds_minutes = []
    for number in last_message.split():
        if number.isdigit():
            seconds_minutes.append(number)
    try:
        print(f'{get_datetime()} {Fore.MAGENTA}Next message in {Fore.CYAN}{seconds_minutes[0]}{Fore.MAGENTA} minutes and {Fore.CYAN}{seconds_minutes[1]}{Fore.MAGENTA} seconds')
        collects_commands.change_interval(minutes=int(seconds_minutes[0]),seconds=int(seconds_minutes[1]))
    except:
        print(f'{get_datetime()} {Fore.RED}Failed to check interval')
    

if __name__ == "__main__":
    try:
        discord_token = str(input(f"{get_datetime()} {Fore.BLUE}{Style.BRIGHT}Discord token: "))
        config_save(f"Discord_token : {discord_token}\n")
    except discord.errors.LoginFailure as error:
        close_app(" Enter correct discord token!")
    try:
        target_channel_id = int(input(f"{get_datetime()} {Fore.BLUE}{Style.BRIGHT}Channel ID: "))
        config_save(f"Target_channel_id : {target_channel_id}\n")
    except ValueError:
        close_app(" Enter only numbers!")

    client.run(discord_token)