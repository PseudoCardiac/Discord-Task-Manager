import discord, datetime, json
from zoneinfo import ZoneInfo
from discord.ext import tasks
from discord.ext.commands import Cog
from utils import updateTimeline, deleteTimelineView
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
        self.reportChannel = faust.info.channel_timeline

        self.dailyReport.start()


    @tasks.loop( time = MIDNIGHT )
    async def dailyReport( self ):
        cutCurrentTasks()
        await updateTimeline( self.faust, True )
        await deleteTimelineView( self.faust )

        # 어제자 작업 초기화
        with open( "data/today.json", 'w+' ) as f:
            json.dump( {}, f )