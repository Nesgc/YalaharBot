import os
import sys
import asyncio
import logging
import discord
from discord.ext import commands
import requests
import tibiapy
from tibiapy.parsers import CharacterParser
from dotenv import load_dotenv
from asgiref.sync import sync_to_async

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "YalaharBot2.settings")
import django
django.setup()
from bot.models import DiscordUser, Character, DiscordUserAndCharacters

# Load environment variables
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def get_character(name):
    url = tibiapy.urls.get_character_url(name)
    r = requests.get(url)
    content = r.text
    character = CharacterParser.from_content(content)
    return character

@sync_to_async
def update_or_create_character(name, level, vocation, world, other_characters):
    discord_user, _ = DiscordUser.objects.get_or_create(User=name)  # Assuming character name is the Discord user's name
    return Character.objects.update_or_create(
        name=name,
        defaults={
            'accountid': discord_user,
            'level': level,
            'vocation': str(vocation),
            'world': world,
            'other_characters': other_characters
        }
    )

@sync_to_async
def add_character_to_discord_user(discord_id, character_name):
    logging.info(f"Adding character {character_name} to Discord user with ID {discord_id}")
    discord_user, created = DiscordUser.objects.get_or_create(User=discord_id)  # Use 'User' to store Discord ID
    if created:
        logging.info(f"Created new Discord user with ID {discord_id}")
    else:
        logging.info(f"Found existing Discord user with ID {discord_id}")

    # Attempt to fetch character details from Tibia API or set defaults
    try:
        character_data = get_character(character_name)
        level = character_data.level or 1  # Default level if not found
        vocation = character_data.vocation or 'None'  # Default vocation if not found
        world = character_data.world or 'Unknown'  # Default world if not found
        other_characters = ', '.join([char.name for char in character_data.other_characters]) if character_data.other_characters else ''
    except Exception as e:
        logging.error(f"Error fetching character data: {e}", exc_info=True)
        level = 1  # Fallback to default values
        vocation = 'None'
        world = 'Unknown'
        other_characters = ''

    character, created = Character.objects.get_or_create(
        name=character_name,
        defaults={
            'accountid': discord_user,
            'level': level,
            'vocation': vocation,
            'world': world,
            'other_characters': other_characters
        }
    )

    # Add the relationship manually using the DiscordUserAndCharacters model
    DiscordUserAndCharacters.objects.get_or_create(discord_user=discord_user, character=character)

    logging.info(f"Added character {character_name} to Discord user with ID {discord_id}")
    return discord_user, character




class CharacterSelect(discord.ui.Select):
    def __init__(self, characters):
        options = [
            discord.SelectOption(label=char, value=char)
            for char in characters
        ]
        super().__init__(placeholder="Select characters to add", options=options, min_values=1, max_values=len(options))

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        added_chars = []

        try:
            for char_name in self.values:  # Directly using the selected values
                discord_user, character = await add_character_to_discord_user(user_id, char_name)
                added_chars.append(character.name)
            
            await interaction.response.send_message(f"Added characters to your account: {', '.join(added_chars)}", ephemeral=True)
            logging.info(f"Added characters {added_chars} to Discord user ID {user_id}")
        except Exception as e:
            logging.error(f"Error adding characters: {str(e)}", exc_info=True)
            await interaction.response.send_message(f"An error occurred while adding characters: {str(e)}", ephemeral=True)


class CharacterSelectView(discord.ui.View):
    def __init__(self, characters):
        super().__init__()
        self.add_item(CharacterSelect(characters))


@bot.tree.command()
async def add(interaction: discord.Interaction, character_name: str):
    """Add Tibia character(s) to your Discord account"""
    try:
        character = await sync_to_async(get_character)(character_name)
        if character:
            all_characters = [character.name] + [char.name for char in character.other_characters]
            unique_characters = list(dict.fromkeys(all_characters))
            view = CharacterSelectView(unique_characters)
            await interaction.response.send_message(
                f"Select which character(s) from the account of {character_name} you want to add:",
                view=view,
                ephemeral=True
            )
        else:
            await interaction.response.send_message(f"Character '{character_name}' not found.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
        logging.error(f"Error in add command: {str(e)}", exc_info=True)

@bot.hybrid_command()
async def lookup(ctx, character_name: str):
    """Look up a Tibia character"""
    try:
        character = await sync_to_async(get_character)(character_name)
        if character:
            other_characters = ', '.join([char.name for char in character.other_characters])
            await update_or_create_character(
                character.name, 
                character.level, 
                character.vocation, 
                character.world, 
                other_characters
            )

            embed = discord.Embed(title=f"Character: {character.name}", color=0x00ff00)
            embed.add_field(name="Level", value=character.level, inline=True)
            embed.add_field(name="Vocation", value=character.vocation, inline=True)
            embed.add_field(name="World", value=character.world, inline=True)

            if character.other_characters:
                embed.add_field(name="Other Characters", value=other_characters, inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Character '{character_name}' not found.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")
        logging.error(f"Error in lookup command: {str(e)}", exc_info=True)

@bot.command()
async def ping(ctx):
    await ctx.send('Pong! El bot está funcionando.')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        guild_id = int(os.getenv('TEST_GUILD_ID', '0'))  # Add TEST_GUILD_ID to your .env file
        if guild_id:
            guild = discord.Object(id=guild_id)
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"Synced {len(synced)} command(s) to the test guild.")
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s) globally")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
        logging.error(f"Failed to sync commands: {e}", exc_info=True)

async def run_bot():
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        raise ValueError("No token found. Set the DISCORD_BOT_TOKEN environment variable.")
    try:
        await bot.start(token)
    except discord.errors.LoginFailure:
        print("Invalid token. Please check your DISCORD_BOT_TOKEN.")
        logging.error("Invalid token. Please check your DISCORD_BOT_TOKEN.", exc_info=True)
    except Exception as e:
        print(f"An error occurred while starting the bot: {e}")
        logging.error(f"An error occurred while starting the bot: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(run_bot())
