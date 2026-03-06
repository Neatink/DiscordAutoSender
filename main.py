from configparser import ConfigParser, NoSectionError
from datetime import datetime,timedelta
from colorama import Fore,init,Style
from random import shuffle, randint
from logger import setup_logger
from discord.ext import tasks
from pathlib import Path
import logging
import discord
import asyncio

setup_logger(__name__)
logger = logging.getLogger(__name__)

letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

getDatetime = lambda: f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]{Style.RESET_ALL}"

init(autoreset=True)
client = discord.Client()
config_parser = ConfigParser()

config_folder_path = Path('configs')
config_path = f'{config_folder_path}/main.cfg'

collect_timer = datetime.now().timestamp()
work_timer = datetime.now().timestamp()

if not config_folder_path.exists():
    config_folder_path.mkdir(parents=True)

def createConfigFile():
    logger.info(f"Creating config file ({config_path})...")
    try:
        open(config_path, "x")
        logger.info("Successfully created config file!")
        with open(config_path, "w", encoding="utf-8") as section:
            logger.info("Writing warning text...")
            config_parser.add_section("# DO NOT SHARE THIS FILE WITH ANYONE AS IT CONTAINS YOUR DISCORD TOKEN WHICH CAN BE USED TO LOG INTO YOUR ACCOUNT! #")
            logger.info("Successfully wrote warning text!")
            logger.info("Adding section 'Discord' to config file...")
            config_parser.add_section("Discord")
            config_parser.write(section)
            logger.info("Successfully added section 'Discord' to config file")
        logger.info(f"Successfully created config file! ({config_path})")
        while not getDiscordToken():
            pass
        while not getChannelID():
            pass
    except FileExistsError:
        config_parser.read(config_path, encoding="utf-8")
        logger.info(f"Config file exists. Loading! ({config_path})")

def config_save(section, target, text):
    with open(config_path, "w", encoding="utf-8") as config:
        config_parser.set(section, target, text)
        config_parser.write(config)
    logger.info(f"Successfully saved '{target}' in '{section}' section")
   
async def getCurrentBalance():
    channel = client.get_channel(int(config_parser.get("Discord","target_channel_id")))
    try:
        await channel.send("+bal")
    except AttributeError as error:
        logger.error("Your Channel ID is incorrect, please enter new Channel ID")
        while not getChannelID():
            pass
        logger.info("Restart app")
        exit(1)
    
    channel_history = await getHistoryChannel()
    
    if not channel_history:
        return
    
    if channel_history.embeds:
        logger.info("Balance:")
        for field in channel_history.embeds[0].fields:
            logger.info(f"{field.name} {field.value[27:]}")

async def antiSpamWithLetter(channel):
    shuffle(letters)
    random_letter = letters[randint(0,25)]
    temp_letter = await channel.send(random_letter)
    logger.debug(f"random letter('{random_letter}') send")
    await asyncio.sleep(1)
    await temp_letter.delete()
    logger.debug(f"random letter('{random_letter}') was deleted")

@client.event
async def on_ready():
    textbal = "-----------------------------------"
    logger.info(f"Username: {client.user.name}")
    logger.info(f"User ID: {client.user.id}")
    logger.debug(textbal)
    await getCurrentBalance()
    logger.debug(textbal)
    if not collects_commands.is_running():
        collects_commands.start()        
        
@tasks.loop(hours=0, minutes=0, seconds=5)
async def collects_commands():
    collects_commands.change_interval(hours=0, minutes=0, seconds=5)
    target_channel_id = config_parser.get("Discord","target_channel_id")
    try:
        channel = client.get_channel(int(target_channel_id))
    except Exception as error:
        logger.error(f"Failed to get channel ID(Error:{error})", exc_info=True)
        enterChannelID()
    if channel:
        try:
            global collect_timer, work_timer
            current_date = datetime.now().timestamp()
            
            await asyncio.sleep(2)

            while collect_timer is None or collect_timer < current_date:
                await antiSpamWithLetter(channel)
                
                await channel.send('+collect')
                logger.debug("'+collect' send")
                
                await asyncio.sleep(3)
                
                collect_timer = await getCollectTime(await getLastMessage())
                
                if collect_timer is not None and collect_timer >= current_date:
                    break
                
            await asyncio.sleep(3)

            while work_timer is None or work_timer < current_date:
                await antiSpamWithLetter(channel)

                await channel.send('+work')
                logger.debug("'+work' send")
                
                await asyncio.sleep(3)
                
                work_timer = await getWorkTime(await getLastMessage())
                
                if work_timer is not None and work_timer >= current_date:
                    break
        
        except Exception as error:
            logger.error(f"Сant send a message!(Try again in 10 seconds...)(Error:{error})", exc_info=True)
            collects_commands.change_interval(hours=0, minutes=0, seconds=10)
            return
    else:
        enterChannelID()

async def getLastMessage():
    channel_history = await getHistoryChannel()
    
    if channel_history is None:
        return None
            
    if channel_history.embeds:
        channel_last_message = channel_history.embeds[0].description
    else:
        channel_last_message = channel_history.content
        
    return channel_last_message

async def getCollectTime(last_message):
    current_time = datetime.now()
    try:
        text1 = float(last_message.split("<t:")[1].split(":")[0])
        total_seconds = text1 - current_time.timestamp() + 3
        totals = datetime(1, 1, 1) + timedelta(seconds=(total_seconds))
    except:
        return None
    timepredict = current_time + timedelta(seconds=(total_seconds))
    logger.info(f"Collect message in {totals.hour} hours {totals.minute} minutes and {totals.second} seconds({timepredict.strftime('%H:%M:%S')})")
    return text1 + 3

async def getWorkTime(last_message):
    if last_message is None:
        return None
    
    current_time = datetime.now()
    seconds_minutes = []
    for number in last_message.split():
        if number.isdigit():
            seconds_minutes.append(int(number))
    try:
        time_predict = current_time + timedelta(minutes=seconds_minutes[0],seconds=seconds_minutes[1])
        logger.info(f"Work message in 0 hours {seconds_minutes[0]} minutes and {seconds_minutes[1]} seconds({time_predict.strftime('%H:%M:%S')})")
        return (current_time + timedelta(seconds = (0 * 3600 + seconds_minutes[0] * 60 + seconds_minutes[1]))).timestamp()
    except IndexError as error:
        logger.error(f"Failed to check interval(Error:{error})", exc_info=True)
        return None

async def getHistoryChannel():
    async for msg in client.get_channel(int(config_parser.get("Discord","target_channel_id"))).history(limit=1):
        if msg:
            if msg.author.name != client.user.name:
                return msg
            else:
                return None

def getChannelID():
    try:
        target_channel_id = int(input(f"{getDatetime()} {Fore.BLUE}{Style.BRIGHT}Enter Channel ID: "))
        config_save("Discord", "target_channel_id", str(target_channel_id))
        return True
    except ValueError:
        logger.error("Enter only numbers!")
        return False
        
def getDiscordToken():
    discord_token = input(f"{getDatetime()} {Fore.BLUE}{Style.BRIGHT}Enter Discord Token: ")
    if not discord_token.strip():
        logger.error("Discord Token is empty!")
        return False
    config_save("Discord", "discord_token", discord_token)
    return True

def startBot():
    createConfigFile()
    try:
        logging.info("Starting DiscordAutoSender...")
        client.run(config_parser.get("Discord","discord_token"))
    except discord.errors.LoginFailure:
        logger.error("Your Discord Token is unavailable, please enter new Discord Token")
        while not getDiscordToken():
            pass
    except Exception as error:
        logger.error(f"Error: {error}", exc_info=True)


if __name__ == "__main__":
    startBot()