import discord, json, datetime, re
from zoneinfo import ZoneInfo
from discord.ext.commands import Cog
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import Faust
from objects import Task, Category, TaskEmbed, TaskEmbedView
from .timer import setTimer
from utils import minutesToHours, updateTimetable


class RegisterTaskCog( Cog ):
    def __init__( self, bot: "Faust" ):
        self.bot = bot

    @discord.app_commands.command( name = "태스크_등록", description = "새로운 태스크를 등록합니다." )
    @discord.app_commands.rename( name = "제목" )
    @discord.app_commands.rename( desc = "세부사항" )
    @discord.app_commands.rename( category = "카테고리" )
    @discord.app_commands.rename( min = "다시_알림_시간_분" )
    async def registerTask( self, i: discord.Interaction, name: str, category: discord.Role, desc: str = "", min: int = 0 ):
        try:
            categoryObj = Category( self.bot.info.tag.index( category ) )
        except ValueError:
            await i.response.send_message( "…파우스트는 카테고리가 아닙니다.", ephemeral = True, delete_after = 10 )
            return
        
        task = Task(
            name = name,
            category = categoryObj,
            desc = desc
        )

        result = task.push()
        if result is False:
            await i.response.send_message( "태스크가 등록되지 않았습니다. 무언가 잘못되었군요.", ephemeral = True, delete_after = 10 )
            return

        embed = TaskEmbed( task, self.bot.info )
        await self.bot.info.channel_log.send( embed = embed, view = TaskEmbedView( embed ) )
        await i.response.send_message( "태스크가 등록되었습니다.", ephemeral = True, delete_after = 10 )
        if min:
            await setTimer( min, task, i.client )   # type: ignore


    @discord.app_commands.command( name = "태스크_완료", description = "진행 중인 태스크를 전부 완료 처리합니다." )
    async def finishTask( self, i: discord.Interaction ):
        with open( "data/current_tasks.json", 'r', encoding = "UTF-8" ) as f:
            currentTasks: list[ dict[ str, str ] ] = json.load( f )

        for currentTask in currentTasks:
            task = Task.toTaskObj( currentTask )
            task.record()

        with open( "data/current_tasks.json", 'w', encoding = "UTF-8" ) as f:
            json.dump( [], f )

        await updateTimetable( i.client ) # type: ignore
        await i.response.send_message( "진행 중인 태스크가 전부 완료 처리되었습니다.", ephemeral = True, delete_after = 10 )


    @discord.app_commands.command( name = "태스크_중단", description = "진행 중인 태스크를 전부 중단 처리합니다." )
    async def abortTask( self, i: discord.Interaction ):
        with open( "data/current_tasks.json", 'w', encoding = "UTF-8" ) as f:
            json.dump( [], f )

        await i.response.send_message( "진행 중인 태스크가 전부 중단 처리되었습니다.", ephemeral = True, delete_after = 10 )


    @discord.app_commands.rename( name = "제목" )
    @discord.app_commands.rename( desc = "세부사항" )
    @discord.app_commands.rename( category = "카테고리" )
    @discord.app_commands.rename( start = "시작_시간_6자리" )
    @discord.app_commands.rename( end = "종료_시간_6자리" )
    @discord.app_commands.command( name = "태스크_기록", description = "완료된 태스크를 등록합니다." )
    async def recordTask( self, i: discord.Interaction, name: str, category: discord.Role, start: str, end: str | None = None, desc: str = "" ):
        try:
            categoryObj = Category( self.bot.info.tag.index( category ) )
        except ValueError:
            await i.response.send_message( "…파우스트는 카테고리가 아닙니다.", ephemeral = True, delete_after = 10 )
            return

        try:
            tz = ZoneInfo( "Asia/Seoul" )
            today = datetime.datetime.now( tz = tz ).date()
            startTime = datetime.datetime.strptime( start, "%H%M%S" ).time()
            startDateTime = datetime.datetime.combine( today, startTime, tz )
            if end is None:
                endTime = datetime.datetime.now( tz = tz ).time()
            else:
                endTime = datetime.datetime.strptime( end, "%H%M%S" ).time()
            endDateTime = datetime.datetime.combine( today, endTime, tz )
        except ValueError:
            await i.response.send_message( "시간 형식이 잘못되었습니다.", ephemeral = True, delete_after = 10 )
            return

        task = Task(
            name = name,
            category = categoryObj,
            desc = desc,
            start = startDateTime,
            end = endDateTime
        )

        task.record( False )
        minutes = round( ( endDateTime - startDateTime ).total_seconds() ) // 60
        durationString = minutesToHours( minutes )


        embed = TaskEmbed( task, self.bot.info )
        embed.description = re.sub( r"<t:\d+:R> 시작", f"{ durationString }동안 진행", str( embed.description ) )
        view = TaskEmbedView( embed )
        for item in view.children:
            item.disabled = True    # type: ignore

        await updateTimetable( i.client )   # type: ignore

        await self.bot.info.channel_log.send( embed = embed, view = view )
        await i.response.send_message( "태스크가 기록되었습니다.", ephemeral = True, delete_after = 10 )