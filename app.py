import discord
import os
import random
import asyncio
from discord.ext import tasks, commands
from dotenv import load_dotenv
import time
import ollama
 
# Load the .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))
PREFIX = os.getenv("PREFIX", "!")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant.")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
 
#  ID of the user to tag
USER_ID = 235097921740079104 # <-- Replace with your user ID
 
# Set the folder where your images are stored
IMAGE_FOLDER = os.getenv("IMAGE_FOLDER", "/app/images")
 
# Initialize image lists
used_images = []
images_list = []

# Store conversation context for each user
conversation_contexts = {}

# Set up bot
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent for reading messages
bot = commands.Bot(command_prefix="!", intents=intents)
 
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    wait_until_top_of_hour.start()

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Process commands first
    await bot.process_commands(message)
    
    # Check if message starts with the prefix
    if not message.content.startswith(PREFIX):
        return
    
    # Extract the prompt (everything after the prefix)
    prompt = message.content[len(PREFIX):].strip()
    
    if not prompt:
        await message.channel.send("Please provide a message after the prefix.")
        return
    
    # Get or initialize conversation context for this user
    user_id = message.author.id
    if user_id not in conversation_contexts:
        conversation_contexts[user_id] = []
    
    try:
        # Show typing indicator while processing
        async with message.channel.typing():
            # Make the call to Ollama with system prompt and context
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *conversation_contexts[user_id],
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the response content
            ai_response = response['message']['content']
            
            # Update conversation context
            conversation_contexts[user_id].append({"role": "user", "content": prompt})
            conversation_contexts[user_id].append({"role": "assistant", "content": ai_response})
            
            # Keep context limited to last 10 messages (5 exchanges)
            if len(conversation_contexts[user_id]) > 10:
                conversation_contexts[user_id] = conversation_contexts[user_id][-10:]
            
            # Send response (Discord has a 2000 character limit)
            if len(ai_response) > 2000:
                # Split into multiple messages if too long
                for i in range(0, len(ai_response), 2000):
                    await message.channel.send(ai_response[i:i+2000])
            else:
                await message.channel.send(ai_response)
                
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        await message.channel.send(f"Sorry, I encountered an error processing your request: {str(e)}")

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
