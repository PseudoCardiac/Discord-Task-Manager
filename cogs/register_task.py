import discord, json
from discord.ext.commands import Cog
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import Faust
from objects import Task, Category, TaskEmbed, TaskEmbedView
from utils import updateTimetable
from .timer import newTimer


class RegisterTaskCog( Cog ):
    def __init__( self, bot: "Faust" ):
        self.bot = bot

    @discord.app_commands.command( name = "태스크_등록", description = "새로운 태스크를 등록합니다." )
    @discord.app_commands.rename( name = "제목" )
    @discord.app_commands.rename( desc = "세부사항" )
    @discord.app_commands.rename( category = "카테고리" )
    @discord.app_commands.rename( min = "예상_소요_시간_분" )
    async def registerTask( self, i: discord.Interaction, name: str, category: discord.Role, desc: str = "", min: int = 0 ):
        try:
            categoryObj = Category( self.bot.info.tag.index( category ) )
        except ValueError:
            await i.response.send_message( "잘못된 카테고리입니다.", ephemeral = True, delete_after = 10 )
        else:
            task = Task(
                name = name,
                category = categoryObj,
                desc = desc
            )

            result = task.push()
            if result is False:
                await i.response.send_message( "태스크가 등록되지 않았습니다.", ephemeral = True, delete_after = 10 )
                return

            embed = TaskEmbed( task, self.bot.info )
            await self.bot.info.channel_log.send( embed = embed, view = TaskEmbedView( embed ) )
            await i.response.send_message( "태스크가 등록되었습니다.", ephemeral = True, delete_after = 10 )
            if min:
                t = newTimer( min, task, i.client )   # type: ignore
                t.start()


    @discord.app_commands.command( name = "태스크_완료", description = "진행 중인 태스크를 전부 완료합니다." )
    async def finishTask( self, i: discord.Interaction ):
        with open( "data/current_tasks.json", 'r', encoding = "UTF-8" ) as f:
            currentTasks: list[ dict[ str, str ] ] = json.load( f )

        for currentTask in currentTasks:
            task = Task.toTaskObj( currentTask )
            task.record()

        with open( "data/current_tasks.json", 'w', encoding = "UTF-8" ) as f:
            json.dump( [], f )

        await updateTimetable( i.client ) # type: ignore
        await i.response.send_message( "태스크 완료됨", ephemeral = True, delete_after = 10 )


    @discord.app_commands.command( name = "태스크_중단", description = "진행 중인 태스크를 전부 중단합니다." )
    async def abortTask( self, i: discord.Interaction ):
        with open( "data/current_tasks.json", 'w', encoding = "UTF-8" ) as f:
            json.dump( [], f )

        await i.response.send_message( "태스크 중단됨", ephemeral = True, delete_after = 10 )