import discord, datetime, json
from zoneinfo import ZoneInfo
from discord.ext import tasks
from discord.ext.commands import Cog
from chart import genChart


MIDNIGHT = datetime.time(
    hour = 0, minute = 0, second = 0,
    tzinfo = ZoneInfo( "Asia/Seoul" )
)


class DailyReportCog( Cog ):
    def __init__( self, reportChannel: discord.TextChannel ):
        self.reportChannel = reportChannel


    @tasks.loop( time = MIDNIGHT )
    async def dailyReport( self ):
        genChart()

        with open( "tt.png", 'rb' ) as f:
            chart = discord.File( f )

        # 오늘자 작업 초기화
        with open( "data/today.json", 'w' ) as f:
            json.dump( {}, f )

        await self.reportChannel.send( file = chart )