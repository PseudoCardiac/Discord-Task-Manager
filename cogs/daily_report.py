import discord, datetime, json
from zoneinfo import ZoneInfo
from discord.ext import tasks
from discord.ext.commands import Cog
from utils import genChart, updateTimetable
from utils.cut_current_tasks import cutCurrentTasks
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import Faust


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

        genChart()

        with open( "tt.png", 'rb' ) as f:
            chart = discord.File( f )

        # 오늘자 작업 초기화
        with open( "data/today.json", 'w' ) as f:
            json.dump( {}, f )

        await self.reportChannel.send( file = chart )
        await updateTimetable( self.faust )