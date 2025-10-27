import discord
import os
import random
import asyncio
from discord.ext import tasks, commands
from dotenv import load_dotenv
import time
 
# Load the .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))
 
#  ID of the user to tag
USER_ID = 235097921740079104 # <-- Replace with your user ID
 
# Set the folder where your images are stored
IMAGE_FOLDER = os.getenv("IMAGE_FOLDER", "/app/images")
 
# Initialize image lists
used_images = []
images_list = []
 
# Set up bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
 
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    wait_until_top_of_hour.start()
 
@tasks.loop(count=1)
async def wait_until_top_of_hour():
    now = time.localtime()
    seconds_until_next_hour = (60 - now.tm_min) * 60 - now.tm_sec
    print(f"Waiting {seconds_until_next_hour} seconds to sync with the hour...")
    await asyncio.sleep(seconds_until_next_hour)
    send_random_image.start()
 
@tasks.loop(hours=1)
async def send_random_image():
    global used_images, images_list
 
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("Channel not found.")
        return
 
    # Reload images list every time
    images_list = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))]
 
    if not images_list:
        print("No images available to send.")
        return
 
    # If all images have been used, reset
    if len(used_images) == len(images_list):
        print("All images have been sent. Resetting used image list...")
        used_images = []
 
    # Choose from unused images
    available_images = list(set(images_list) - set(used_images))
    selected_image = random.choice(available_images)
    used_images.append(selected_image)
 
    image_path = os.path.join(IMAGE_FOLDER, selected_image)
    mention = f"<@{USER_ID}>"
 
    try:
        await channel.send(content=f"{mention}", file=discord.File(image_path))
        print(f"Sent image: {selected_image} to {mention}")
    except Exception as e:
        print(f"Failed to send image: {e}")
 
# Run the bot
bot.run(TOKEN)
