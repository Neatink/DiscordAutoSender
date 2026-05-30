from configparser import ConfigParser, NoOptionError, NoSectionError
from datetime import datetime,timedelta
from colorama import Fore,init,Style
from random import shuffle, randint
from logger import setup_logger
from discord.ext import tasks
from pathlib import Path
import platform
import logging
import discord
import asyncio
import time
import sys
import os

setup_logger(__name__)
logger = logging.getLogger(__name__)

letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

getDatetime = lambda: f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]{Style.RESET_ALL}"
getRandomCounter = lambda: randint(1, 3)
clearConsole = lambda command : os.system(command)

sections = ["# DO NOT SHARE THIS FILE WITH ANYONE AS IT CONTAINS YOUR DISCORD TOKEN WHICH CAN BE USED TO LOG INTO YOUR ACCOUNT! #", "Discord", "OS"]

init(autoreset=True)
client = discord.Client()
config_parser = ConfigParser()

config_folder_path = Path("configs")
config_folder_path.mkdir(parents=True, exist_ok=True)
config_path = config_folder_path / "main.cfg"

collect_timer = datetime.now().timestamp()
work_timer = datetime.now().timestamp()

def restartBot(timing = 0):
    if timing > 0: 
        logger.info(f"Restarting bot in {timing} seconds...")
    else:
        logger.info(f"Restarting bot...")
    time.sleep(timing)
    os.execv(sys.executable, [sys.executable] + sys.argv)

def checkSections(sections):
    added_new_sections = False
    for section in sections:
        if not config_parser.has_section(section):
            logger.info(f"Adding section '{section}' to config file({config_path})")
            config_parser.add_section(section)
            added_new_sections = True
            logger.info(f"Successfully added section '{section}' to config file({config_path})")
    if added_new_sections:
        with open(config_path, "w", encoding="utf-8") as config:
            config_parser.write(config)

def createConfigFile():
    logger.info(f"Creating config file ({config_path})...")
    try:
        open(config_path, "x")
        checkSections(sections)
        logger.info(f"Successfully created config file ({config_path})")
        getDiscordToken()
        getChannelID()
    except FileExistsError:
        config_parser.read(config_path, encoding="utf-8")
        logger.error(f"Config file exists. Loading({config_path})...")

def config_save(section, target, text):
    with open(config_path, "w", encoding="utf-8") as config:
        config_parser.set(section, target, text)
        config_parser.write(config)
    logger.info(f"Successfully saved '{target}' in '{section}' section")

async def getInfoUser():
    logger.info(f"Username: {client.user.name}")
    logger.info(f"User ID: {client.user.id}")

async def getCurrentBalance():
    textbal = '-' * 35
    try:
        logger.info("Getting Channel ID...")
        channel = client.get_channel(int(config_parser.get("Discord","target_channel_id")))
        logger.info("Successfully got Channel ID")
        clearConsole(getClearCommand())
        await getInfoUser()
        await channel.send("+bal")
        logger.debug("'+bal' send")
    except (ValueError, AttributeError):
        getChannelID("Your Channel ID is unavailable, please enter new Channel ID")
    except NoOptionError:
        getChannelID("Failed to get option 'Channel ID'")
    await asyncio.sleep(1)
    
    channel_history = await getHistoryChannel()
    
    if not channel_history:
        return
    
    if channel_history.embeds:
        logger.debug(textbal)
        logger.info("Balance:")
        for field in channel_history.embeds[0].fields:
            logger.info(f"{field.name} {field.value[27:]}")
        logger.debug(textbal)

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
    logger.info("Successfully started DiscordAutoSender")
    await getCurrentBalance()
    if not collects_commands.is_running():
        collects_commands.start()  

@tasks.loop(hours=0, minutes=0, seconds=5)
async def collects_commands():
    global collect_timer, work_timer
    collects_commands.change_interval(hours=0, minutes=0, seconds=5)
    target_channel_id = config_parser.get("Discord","target_channel_id")
    try:
        channel = client.get_channel(int(target_channel_id))
    except:
        logger.error(f"Failed to get channel ID!")
        getChannelID()
    if channel:
        try:
            current_date = datetime.now().timestamp()

            while not collect_timer or collect_timer < current_date:
                await asyncio.sleep(2.5)
                
                await antiSpamWithLetter(channel)
                
                await channel.send('+collect')
                logger.debug("'+collect' send")
                
                await asyncio.sleep(2.5)
                
                collect_timer = await getCollectTime(await getLastMessage())
                
                if collect_timer is not None and collect_timer >= current_date:
                    break
                
            await asyncio.sleep(2.5)

            while not work_timer or work_timer < current_date:
                await asyncio.sleep(2.5)
                
                await antiSpamWithLetter(channel)

                await channel.send('+work')
                logger.debug("'+work' send")
                
                await asyncio.sleep(2.5)
                
                work_timer = await getWorkTime(await getLastMessage())
                
                if work_timer is not None and work_timer >= current_date:
                    break
        
        except Exception as error:
            logger.error(f"Сant send a message!(Trying again in 10 seconds...)(Error:{error})", exc_info=True)
            collects_commands.change_interval(hours=0, minutes=0, seconds=10)
            return
    else:
        getChannelID()

async def getLastMessage():
    channel_history = await getHistoryChannel()
    
    if not channel_history:
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
        timepredict = current_time + timedelta(seconds=(total_seconds))
        logger.info(f"Collect message in {totals.hour} hours {totals.minute} minutes and {totals.second} seconds({timepredict.strftime('%H:%M:%S')})")
        return text1 + getRandomCounter()
    except:
        logger.error(f"Failed to check interval!")
        return None


async def getWorkTime(last_message):
    if not last_message:
        return None
    current_time = datetime.now()
    seconds_minutes = []
    for number in last_message.split():
        if number.isdigit():
            seconds_minutes.append(int(number))
    try:
        time_predict = current_time + timedelta(minutes=seconds_minutes[0],seconds=seconds_minutes[1])
        logger.info(f"Work message in 0 hours {seconds_minutes[0]} minutes and {seconds_minutes[1]} seconds({time_predict.strftime('%H:%M:%S')})")
        return time_predict.timestamp() + getRandomCounter()
    except IndexError:
        logger.error(f"Failed to check interval!")
        return None

async def getHistoryChannel():
    async for msg in client.get_channel(int(config_parser.get("Discord","target_channel_id"))).history(limit=1):
        if msg:
            if msg.author.name != client.user.name:
                return msg
            else:
                return None

def getChannelID(error = None):
    clearConsole(getClearCommand())
    if error : logger.error(error)
    while True:
        try:
            target_channel_id = int(input(f"{getDatetime()} {Fore.BLUE}{Style.BRIGHT}Enter Channel ID: "))
        except ValueError:
            logger.error("Enter only numbers!")
            continue
        except EOFError:
            logger.critical("Keyboard not found!")
            logger.info("Checking .env file to get Channel ID...")
            target_channel_id = os.getenv("TARGET_CHANNEL_ID")
            if not target_channel_id:
                logger.critical("Failed to get Channel ID from .env file!")
                sys.exit()
        if not str(target_channel_id).strip():
            logger.error("Channel ID is empty!")
        else:
            logger.info("Successfully got Channel ID")
            config_save("Discord", "target_channel_id", str(target_channel_id))
            restartBot()
        
def getDiscordToken(error = None):
    clearConsole(getClearCommand())
    if error : logger.error(error)
    while True:
        try:
            discord_token = input(f"{getDatetime()} {Fore.BLUE}{Style.BRIGHT}Enter Discord Token: ")
        except EOFError:
            logger.critical("Keyboard not found!")
            logger.info("Checking .env file to get Discord Token...")
            discord_token = os.getenv("DISCORD_TOKEN")
            if not discord_token:
                logger.critical("Failed to get Discord Token from .env file!(Empty)")
                sys.exit()
        if not discord_token.strip():
            logger.error("Discord Token is empty!")
        else:
            logger.info("Successfully got Discord Token")
            config_save("Discord", "discord_token", discord_token)
            restartBot()

def getClearCommand():
    def getOS():
        if platform.system() == "Windows":
            return "cls"
        else:
            return "clear"
    current_os = getOS()
    try:
        logger.info("Getting user OS...")
        old_clear_command = config_parser.get("OS", "clear_command")
        logger.info("Successfully got user OS")
        logger.info("Checking for OS changes...")
        if old_clear_command != current_os:
            os_base = platform.uname()
            logger.info(f"New OS detected: {os_base.system}({os_base.node})")
            config_save("OS", "clear_command", current_os)
        else:
            logger.info("Changes not detected")
    except NoOptionError:
        logger.error("Failed to get option 'OS'")
        config_save("OS", "clear_command", getOS())
    except NoSectionError:
        logger.error("Failed to get section 'OS'")
        checkSections([sections[2]])
    except PermissionError as error:
        logger.error(f"Permission to file was denied!(error: {error})")
        sys.exit()
    return current_os

def startBot():
    while True:
        createConfigFile()
        getClearCommand()
        try:
            logging.info("Starting DiscordAutoSender...")
            client.run(config_parser.get("Discord","discord_token"))
        except NoSectionError:
            logger.error("Failed to get section 'Discord'")
            checkSections([sections[1]])
        except NoOptionError:
            getDiscordToken("Failed to get option 'Discord Token'")
        except (discord.errors.LoginFailure,UnicodeEncodeError):
            getDiscordToken("Your Discord Token is unavailable, please enter new Discord Token")
        except Exception as error:
            logger.error(f"Unknown error: {error}", exc_info=True)
        logger.critical("Connection with bot was aborted")
        restartBot(15)


if __name__ == "__main__":
    startBot()
