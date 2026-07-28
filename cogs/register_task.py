import discord
from discord.ext.commands import Cog
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.faust import Faust
from objects.task import Task
from objects.category import Category
from objects.task_embed import TaskEmbed, TaskEmbedView


class RegisterTaskCog( Cog ):
    def __init__( self, bot: "Faust" ):
        self.bot = bot

    @discord.app_commands.command( name = "태스크_등록", description = "새로운 태스크를 등록합니다." )
    @discord.app_commands.rename( name = "제목" )
    @discord.app_commands.rename( desc = "세부사항" )
    @discord.app_commands.rename( category = "카테고리" )
    async def registerTask( self, i: discord.Interaction, name: str, category: discord.Role, desc: str = "" ):
        try:
            categoryObj = Category( self.bot.info.tag.index( category ) )
        except ValueError:
            await i.response.send_message( "잘못된 카테고리입니다." )
        else:
            task = Task(
                name = name,
                category = categoryObj,
                desc = desc
            )

            result = task.push()
            if result is False:
                await i.response.send_message( "태스크가 등록되지 않았습니다." )
                return

            embed = TaskEmbed( task, self.bot.info )
            await self.bot.info.channel_log.send( embed = embed, view = TaskEmbedView( embed ) )
            await i.response.send_message( "태스크가 등록되었습니다." )