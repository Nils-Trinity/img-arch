from discord.ext import commands
import discord
import os
import datetime

#Get the bot's token
with open("token.txt", "r") as token_file:
    token = token_file.read()

#Set its prefix
bot = commands.Bot(command_prefix = ";")

#Get the paths to the image and dates folders
path_imgs = os.getcwd() + "\\images\\"
path_dates = os.getcwd() + "\\dates\\"

#Check if the folders exists, if they don't, create them
if not os.path.exists(path_imgs):
    print(f"Creating directory: {path_imgs}")
    os.mkdir(path_imgs)
if not os.path.exists(path_dates):
    print(f"Creating directory: {path_dates}")
    os.mkdir(path_dates)

#Upon startup:
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    #Go through every server
    for guild in bot.guilds:
        #Get the first part of the path (if u don't, the directory fucks itself with an invalid character and idk why)
        patha = os.getcwd() + f"\\dates\\{str(guild)}\\"

        #Go through every channel in the server
        for channel in guild.text_channels:
            print(f"Scanning {channel} in {guild}")

            #Visual representation that the bot is scanning the channel
            async with channel.typing():
                #Second part of the path appended to the first part
                path = patha + f"lastmsg-{str(channel)}.txt"
                
                #If the channel has been previously scanned before
                if os.path.isfile(path):
                    #Open a file with the date of the last detected message
                    with open(path, "r") as file:
                        #Get the date
                        date = datetime.datetime.strptime(file.read(), "%Y-%m-%d %H:%M:%S.%f")

                        #Get all messages after the date of the last detected message
                        msgs = await channel.history(limit=None, after=date, oldest_first=True).flatten()
                #If it hasn't been scanned before
                else:
                    #Get all messages in the channel
                    msgs = await channel.history(limit=None, oldest_first=True).flatten()
                    
                #Go through each one
                for msg in msgs:
                    #Save the image and update the file containing the date
                    print(f"Message in {msg.channel} from {msg.created_at}")
                    await save_message(msg, guild)
                    track_message(msg, guild)
    print("Finished getting images")
                
#Command just to test if the bot is working from discord
@bot.command(name="ping", help="Pings the bot")
async def ping(ctx):
    await ctx.send("pong")
    print("Pinged bot")

#When a message is sent:
@bot.event
async def on_message(message):
    print("Got message")
    #Save the image(if applicable) and update the last read date
    await save_message(message, message.guild)
    track_message(message, message.guild)
    
#Saving the message
async def save_message(message, guild):
    #Go through every image in the message
    for img in message.attachments:
        #Get the path to the server's image directory
        path = os.getcwd() + f"\\images\\{str(guild)}"

        #Check if the path already exists for both the guild and channel
        #If the path does not exist, it creates it
        if not os.path.exists(path):
            print(f"Creating directory: {path}")
            os.mkdir(path)
        if not os.path.exists(path + f"\\{message.channel}"):
            print(f"Creating directory: {path}")
            os.mkdir(path + f"\\{message.channel}")

        #Then it just saves the image with the path
        await img.save(f'{path}\\{message.channel}\\{img.filename}')

#Updating the date
def track_message(message, guild):
    #Get the message's date
    date = message.created_at
    #Get a path to the server's date directory
    path = os.getcwd() + f"\\dates\\{str(guild)}\\"
    #and the filename
    f = f"lastmsg-{str(message.channel)}.txt"

    #Check if the server directory exists and creates it if it doesn't
    if not os.path.exists(path):
        print(f"Creating directory: {path}")
        os.mkdir(path)

    #Saves the date of the message to the file
    with open(path + f, "w") as file:
        file.write(str(date))

#Run the bot using the given token
bot.run(token)
