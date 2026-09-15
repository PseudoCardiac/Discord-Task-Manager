import discord
from discord.ext import commands


class Info:
    async def init( self, bot: commands.Bot ):
        self.guild: discord.Guild = await bot.fetch_guild( 1530543614868979743 )                # type: ignore
        self.scy: discord.Member = await self.guild.fetch_member( 513676568745213953 )          # type: ignore

        self.tag_university: discord.Role = await self.guild.fetch_role( 1530556011415605350 )  # type: ignore
        self.tag_living: discord.Role = await self.guild.fetch_role( 1530556062275469504 )      # type: ignore
        self.tag_workout: discord.Role = await self.guild.fetch_role( 1530556344753590462 )     # type: ignore
        self.tag_rest: discord.Role = await self.guild.fetch_role( 1530556077559648468 )        # type: ignore
        self.tag_study: discord.Role = await self.guild.fetch_role( 1530556094806753300 )       # type: ignore
        self.tag_hobby: discord.Role = await self.guild.fetch_role( 1530556106336764004 )       # type: ignore
        self.tag_game: discord.Role = await self.guild.fetch_role( 1530556325325574184 )        # type: ignore
        self.tag_sleep: discord.Role = await self.guild.fetch_role( 1530556359433785425 )       # type: ignore
        self.tag_etc: discord.Role = await self.guild.fetch_role( 1530556370200559788 )         # type: ignore

        self.tag = [ self.tag_university, self.tag_living, self.tag_workout, self.tag_rest, self.tag_study, self.tag_hobby, self.tag_game, self.tag_sleep, self.tag_etc ]
        self.tagColor = [ 13050659, 16747818, 16772150, 9882670, 9105407, 14792447, 16734625, 7640229, 9013641 ]

        self.channel_log: discord.TextChannel = await self.guild.fetch_channel( 1530566962785026060 )       # type: ignore
        self.channel_timeline: discord.TextChannel = await self.guild.fetch_channel( 1542049334189752371 )  # type: ignore