import discord
from discord.ext import commands
from discord import app_commands
import asyncpg
from datetime import timedelta
from utils.messages import response

token = 'token'

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="$", intents=discord.Intents.all())

    async def setup_hook(self) -> None: #setup_hook is a coroutine to be called to setup the bot, by default this is blank.
        try:
            self.conn = await asyncpg.create_pool('postgresql://astra:root@localhost/test_db')
            print("Database connection successful!")
        except Exception as err:
            print(err)

    async def on_ready(self):
        await bot.load_extension("cogs.bot_commands")
        print("Bot commands cogs loaded!")
        await bot.tree.sync()
        print("Bot is ready...")
    
    async def on_member_join(self, member: discord.Member):
        channel_id = await self.conn.fetchval("SELECT welcome_channel from discord_servers WHERE server_id = $1", str(member.guild.id))
        channel = self.get_channel(int(channel_id))
        embed_info = discord.Embed(title=f"Welcome to {member.guild.name} {member.display_name}", description=f"We are very glad to have you here!", color=discord.Color.blue())
        embed_info.set_thumbnail(url=member.guild.icon)
        embed_info.set_image(url=member.avatar)
        embed_info.set_footer(text=f"From: {member.guild.name}")
        embed_info.add_field(name="", value="", inline=False)
        await channel.send(embed=embed_info)
    
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel): #If you want this to work in a group channel
            if message.author != self.user:
                print(f"{message.author}: {message.content}")
                reply = response(message.author.display_name, message.content)
                await message.channel.send(reply)
        if message.flags and discord.MessageFlags.ephemeral:
            return
        if isinstance(message.channel, discord.TextChannel): #added new line
            words = message.content.split(" ")
            for word in words:
                bad_word = await self.conn.fetchval("SELECT word FROM bad_words WHERE word = $1 AND server_id = $2", word.lower(), str(message.guild.id))
                if bad_word:
                    break

            if bad_word:
                delta = timedelta(minutes=10)
                await message.author.timeout(delta)
                await message.channel.send(f"{message.author} has been timed out for 10 minutes for using bad words.")
        
async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        perms = ""
        for p in error.missing_permissions: 
            perms += f"{p}, "
    await interaction.response.send_message(f"You need these permissions: {perms} to use this command", ephemeral=True)

    
bot = Bot()
bot.tree.on_error = on_tree_error

bot.run(token)
