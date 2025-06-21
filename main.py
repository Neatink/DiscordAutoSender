from datetime import datetime
from colorama import Fore,init
from discord.ext import tasks
import discord
import os

minutes = 0
seconds = 3

init(autoreset=True)
client = discord.Client()

def get_datetime():
    return f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
    
def close_app(message):
    print(get_datetime() + Fore.RED + message + Fore.RESET)
    os.system('pause')
    exit(1),Fore.RESET
    
@client.event
async def on_ready():
    os.system('cls')
    print(f'{get_datetime()} {Fore.MAGENTA}Username: {Fore.CYAN}{client.user.name}')
    print(f'{get_datetime()} {Fore.MAGENTA}User ID: {Fore.CYAN}{client.user.id}')
    if not collects_commands.is_running():
        collects_commands.start()
        
@tasks.loop(minutes=minutes,seconds=seconds)
async def collects_commands():
    channel = client.get_channel(target_channel_id[0])
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
        target_channel_id = int(input(f"{get_datetime()} {Fore.YELLOW}Channel ID: ")),Fore.RESET
    except ValueError:
        close_app("Enter only numbers!")
    
    
    client.run('your-discord-token')
