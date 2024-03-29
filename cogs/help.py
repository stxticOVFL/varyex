import discord
from discord.ext import commands

from imports.menus import Paginator
from typing import Union, List, Optional, TYPE_CHECKING
from copy import copy


from imports.main import Main

class Help(commands.Cog):
    def __init__(self, bot: Main):
        self.bot = bot

    def parse(self, cog, command, prefix="v!") -> Union[List[discord.Embed], discord.Embed]:
        if (not cog) and (not command): #v!help
            ret = []
            for x in list(self.bot.cogs):
                if x == 'Help': continue #don't get us
                ret.append(self.parse(x, None))
            return ret
        if command:
            command = self.bot.get_command(command)
            if not command: return None
            cog = command.cog.qualified_name
            return discord.Embed(title=f"{cog} - {command.name}", color=self.bot.data['color'], description=command.help)
        #cog
        embed = discord.Embed(title=cog, color=self.bot.data['color'], description="")
        for cmd in self.bot.get_cog(cog).walk_commands():
            if cmd.hidden or (not cmd.enabled) or (not cmd.help) or cmd.parent: continue
            summary = cmd.help.splitlines()[0]
            aliasstr = ""
            if (cmd.aliases):
                aliasstr = f" - `{'`, `'.join(cmd.aliases)}`"
            embed.description += f"__**`{cmd.name}`**__ - {summary}{aliasstr}\n"
        embed.set_footer(text = f"Use {prefix}help [command] for more info on a command.")            
        return embed
        
    @commands.command()
    async def help(self, ctx, command: Optional[str] = None):
        """Get help for all commands or a specific command."""
        if not command:
            embed = discord.Embed(title="Help", color=self.bot.data['color']) 
            embeds = [copy(embed)]
            for e in sorted(self.parse(None, None), key=lambda x: len(x.description)):
                if e.description:
                    embeds[-1].add_field(name=e.title, value=e.description, inline=False)
                if len(embeds[-1]) > 400:
                    embeds.append(copy(embed))
            if not embeds[-1].description: del embeds[-1]
            return await Paginator(embeds, footer=f"Use {ctx.prefix}help [command] for more info on a command.", title="Help", loop=True).start(ctx, ephemeral=True)
        embed = self.parse(None, command.lower())
        if not embed:
            for x in list(self.bot.cogs):
                if x.lower() == command.lower():
                    return await ctx.send(embed=self.parse(x, None, prefix=ctx.prefix), ephemeral=True)
            await ctx.send("That command doesn't exist!", ephemeral=True)
            return await ctx.invoke(self.help)
        return await ctx.send(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Help(bot))
