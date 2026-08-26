import discord
from discord.ext import commands


class Info:
    async def init( self, bot: commands.Bot ):
        self.guild: discord.Guild = bot.get_guild( 1530543614868979743 )                        # type: ignore
        self.scy: discord.Member = self.guild.get_member( 513676568745213953 )                  # type: ignore

        self.tag_university: discord.Role = self.guild.get_role( 1530556011415605350 )          # type: ignore
        self.tag_living: discord.Role = self.guild.get_role( 1530556062275469504 )              # type: ignore
        self.tag_workout: discord.Role = self.guild.get_role( 1530556344753590462 )             # type: ignore
        self.tag_rest: discord.Role = self.guild.get_role( 1530556077559648468 )                # type: ignore
        self.tag_study: discord.Role = self.guild.get_role( 1530556094806753300 )               # type: ignore
        self.tag_hobby: discord.Role = self.guild.get_role( 1530556106336764004 )               # type: ignore
        self.tag_game: discord.Role = self.guild.get_role( 1530556325325574184 )                # type: ignore
        self.tag_sleep: discord.Role = self.guild.get_role( 1530556359433785425 )               # type: ignore
        self.tag_etc: discord.Role = self.guild.get_role( 1530556370200559788 )                 # type: ignore

        self.tag = [ self.tag_university, self.tag_living, self.tag_workout, self.tag_rest, self.tag_study, self.tag_hobby, self.tag_game, self.tag_sleep, self.tag_etc ]
        self.tagColor = [ 13050659, 16747818, 16772150, 9882670, 9105407, 14792447, 16734625, 7640229, 9013641 ]

        self.channel_home: discord.TextChannel = self.guild.get_channel( 1530546132382388234 )  # type: ignore
        self.channel_log: discord.TextChannel = self.guild.get_channel( 1530566962785026060 )   # type: ignore
        self.channel_timeline: discord.TextChannel = self.guild.get_channel( 1542049334189752371 )   # type: ignore

        self.msg_timetable: discord.Message = await self.channel_timeline.fetch_message( 1531453119240737025 )