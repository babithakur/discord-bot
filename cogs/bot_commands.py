import discord
from discord.ext import commands 
from discord import app_commands

class BotCommands(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    async def delete_message(self, ctx: discord.Interaction, amount: int):
        """deletes the specified amount of message""" 
        await ctx.response.defer(thinking=True, ephemeral=True) 
        await ctx.channel.purge(limit=amount) 
        await ctx.followup.send(f"Deleted {amount} messages!", ephemeral=True)
    
    @app_commands.command()
    async def print_id(self, ctx, name: str, position: str):
        """prints the id card information for the member"""
        embed_info = discord.Embed(title=name, description=position, color=discord.Color.orange())
        embed_info.set_thumbnail(url=ctx.guild.icon)
        embed_info.set_image(url=ctx.user.avatar)
        embed_info.set_footer(text=ctx.guild.name)
        embed_info.add_field(name="", value="", inline=False)
        await ctx.response.send_message(embed=embed_info)
    
    @app_commands.command()
    async def server_info(self, ctx): 
        """prints information about server"""
        info_embed = discord.Embed(title=f"Information about {ctx.guild.name}", color=discord.Color.green())
        info_embed.set_thumbnail(url=ctx.guild.icon)
        info_embed.add_field(name="Name:", value=ctx.guild.name, inline=False)
        info_embed.add_field(name="Server ID:", value=ctx.guild.id, inline=False)
        info_embed.add_field(name="Owner:", value=ctx.guild.owner, inline=False)
        info_embed.add_field(name="Member Count:", value=ctx.guild.member_count, inline=False)
        info_embed.add_field(name="Channel Count:", value=len(ctx.guild.channels), inline=False)
        info_embed.add_field(name="Role Count:", value=len(ctx.guild.roles), inline=False)
        info_embed.add_field(name="Rules Channel:", value=ctx.guild.rules_channel, inline=False)
        info_embed.add_field(name="Booster Count:", value=ctx.guild.premium_subscription_count, inline=False)
        info_embed.add_field(name="Booster Tier:", value=ctx.guild.premium_tier, inline=False)
        info_embed.add_field(name="Booster Role:", value=ctx.guild.premium_subscriber_role, inline=False)
        info_embed.add_field(name="Created At:", value=ctx.guild.created_at.__format__("%A, %d. %B %Y @ %H:%M:%S"), inline=False)
        info_embed.set_footer(text=f"Requested by {ctx.user.name}", icon_url=ctx.user.avatar)

        await ctx.response.send_message(embed=info_embed)
    
    @app_commands.command()
    async def dm_member(self, ctx, member: discord.Member, message: str):
        """sends dm to a member"""
        await member.send(message)
        await ctx.response.send_message(f"Sent {message} to {member}", ephemeral=True)
    
    @app_commands.command()
    async def kick_member(self, ctx, member: discord.Member, reason: str):
        """removes a member from the server"""
        await member.kick(reason=reason)
        await ctx.response.send_message(f"{member} has been kicked for {reason}")
    
    @app_commands.command()
    async def ban_member(self, ctx, member: discord.Member, reason: str):
        """bans a member on server"""
        await member.ban(reason=reason)
        await ctx.response.send_message(f"{member} has been banned for {reason}")
    
    @app_commands.command()
    async def set_welcome_channel(self, ctx: discord.Interaction):
        """sets welcome channel for your server"""
        server_id = await self.bot.conn.fetchval("SELECT server_id FROM discord_servers WHERE server_id = $1", str(ctx.guild.id))
        if server_id:
            await ctx.response.send_message("You have already set the welcome channel. You may use update_welcome_channel_command to update it.", ephemeral=True)
        else:
            await self.bot.conn.execute("INSERT INTO discord_servers (server_id, welcome_channel) VALUES ($1, $2)", str(ctx.guild.id), str(ctx.channel_id))
            await ctx.response.send_message(f"{ctx.channel.mention} is your welcome channel now!")

    @app_commands.command()
    async def update_welcome_channel(self, ctx: discord.Interaction):
        """updates welcome channel for your server"""
        await self.bot.conn.execute("UPDATE discord_servers SET welcome_channel = $1 WHERE server_id = $2", str(ctx.channel_id), str(ctx.guild.id))
        await ctx.response.send_message(f"Your welcome channel has been updated to {ctx.channel.mention}")
    
    @app_commands.checks.has_permissions(manage_guild=True)    
    @app_commands.command()
    async def add_bad_word(self, ctx: discord.Interaction, word: str):
        """adds a word in the list of bad words"""
        bad_word = await self.bot.conn.fetchval("SELECT word FROM bad_words WHERE word = $1 AND server_id = $2", word, str(ctx.guild.id))
        if bad_word:
            await ctx.response.send_message("This word is already set as a bad word!", ephemeral=True)
        else:
            await self.bot.conn.execute("INSERT INTO bad_words (word, server_id) VALUES ($1, $2)", word.lower(), str(ctx.guild.id))
            await ctx.response.send_message(f"The given word is added to bad words.")
    
    @app_commands.checks.has_permissions(manage_guild=True)        
    @app_commands.command()
    async def remove_bad_word(self, ctx: discord.Interaction, word: str):
        """removes a word from bad words"""
        bad_word = await self.bot.conn.fetchval("SELECT word FROM bad_words WHERE word = $1 AND server_id = $2", word.lower(), str(ctx.guild.id))
        if bad_word:
            await self.bot.conn.execute("DELETE FROM bad_words WHERE word = $1 and server_id = $2", word.lower(), str(ctx.guild.id))
            await ctx.response.send_message("The given word was removed from bad words.", ephemeral=True)
        else:
            await ctx.response.send_message("No such word was found in bad words.", ephemeral=True)
    
    @app_commands.command()
    async def give_shout_out(self, ctx: discord.Interaction, name: discord.Member):
        """gives a shout out to specified member"""
        embed_info = discord.Embed(title=f"Shout-out to {name.display_name}", color=discord.Color.random())
        embed_info.set_thumbnail(url=ctx.guild.icon)
        embed_info.set_image(url=name.avatar)
        embed_info.add_field(name="", value="", inline=False)
        embed_info.set_footer(text=f"From: {ctx.user.name}", icon_url=ctx.user.avatar)
        await ctx.response.send_message(embed=embed_info)

async def setup(bot: commands.Bot):
    await bot.add_cog(BotCommands(bot))
