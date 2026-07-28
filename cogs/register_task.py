import discord
from discord.ext.commands import Cog
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import Faust
from objects import Task, Category, TaskEmbed, TaskEmbedView
from utils import updateTimetable


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


    # TODO 모든 태스크를 pop하도록 수정하기
    @discord.app_commands.command( name = "태스크_완료", description = "진행 중인 태스크를 완료합니다." )
    async def finishTask( self, i: discord.Interaction ):
        result = Task.pop()
        if result is False:
            await i.response.send_message( "태스크를 찾지 못함" )
            return
        
        result.record()

        await updateTimetable( i.client ) # type: ignore
        await i.response.send_message( "태스크 완료됨" )

    # TODO 모든 태스크를 pop하도록 수정하기
    @discord.app_commands.command( name = "태스크_중단", description = "진행 중인 태스크를 중단합니다." )
    async def abortTask( self, i: discord.Interaction ):
        result = Task.pop()
        if result is False:
            await i.response.send_message( "태스크를 찾지 못함" )
            return

        await i.response.send_message( "태스크 중단됨" )