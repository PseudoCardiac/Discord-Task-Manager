import discord, datetime
from zoneinfo import ZoneInfo
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import Faust
from .chart import genChart


weekdays = [ '월', '화', '수', '목', '금', '토', '일' ]


async def updateTimetable( faust: "Faust" ):
    now = datetime.datetime.now( tz = ZoneInfo( "Asia/Seoul" ) )
    embed = discord.Embed( title = f"{ now.year }년 { now.month }월 { now.day }일 { weekdays[ now.weekday() ] }요일 대시보드" )

    genChart()

    with open( "tt.png", 'rb' ) as f:
        chart = discord.File( f )

    embed.set_image( url = "attachment://tt.png" )
    await faust.info.msg_timetable.edit( attachments = [ chart ], embed = embed, view = TimetableView() )


class TimetableView( discord.ui.View ):
    def __init__( self ):
        super().__init__( timeout = None )
        self.add_item( RefreshButton() )


class RefreshButton( discord.ui.Button ):
    def __init__( self ):
        super().__init__(
            label = "새로고침",
            style = discord.ButtonStyle.primary,
            custom_id = "RefreshButton"
        )


    async def callback( self, interaction: discord.Interaction ):
        await updateTimetable( interaction.client ) # type: ignore
        # await interaction.response.send_message( "대시보드를 성공적으로 새로고침했습니다.", ephemeral = True, delete_after = 10 )
        await interaction.response.defer()