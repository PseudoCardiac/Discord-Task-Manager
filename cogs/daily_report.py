import discord, datetime, json
from zoneinfo import ZoneInfo
from discord.ext import tasks
from discord.ext.commands import Cog
from utils import genChart, updateTimetable
from utils.cut_current_tasks import cutCurrentTasks
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import Faust


weekdays = [ '월', '화', '수', '목', '금', '토', '일' ]


MIDNIGHT = datetime.time(
    hour = 0, minute = 0, second = 0,
    tzinfo = ZoneInfo( "Asia/Seoul" )
)


class DailyReportCog( Cog ):
    def __init__( self, faust: "Faust" ):
        self.faust = faust
        self.reportChannel = faust.info.channel_log

        self.dailyReport.start()


    @tasks.loop( time = MIDNIGHT )
    async def dailyReport( self ):
        cutCurrentTasks()

        yesterday = datetime.datetime.now( tz = ZoneInfo( "Asia/Seoul" ) ) - datetime.timedelta( days = 1 )
        genChart( yesterday )

        with open( "tt.png", 'rb' ) as f:
            chart = discord.File( f )

        # 어제자 작업 초기화
        with open( "data/today.json", 'w' ) as f:
            json.dump( {}, f )

        embed = discord.Embed(
            title = f"{ yesterday.year }년 { yesterday.month }월 { yesterday.day }일 { weekdays[ yesterday.weekday() ] }요일",
            color = 16757172
        )

        embed.set_image( url = "attachment://tt.png" )

        await self.reportChannel.send( file = chart, embed = embed)
        await updateTimetable( self.faust )