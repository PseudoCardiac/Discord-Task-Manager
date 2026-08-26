import discord, datetime
from zoneinfo import ZoneInfo
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import Faust
from .chart import genChart
from .string_to_date import stringToDate


weekdays = [ '월', '화', '수', '목', '금', '토', '일' ]


def generateTimeline():
    """
    호출 시각을 기준으로 타임라인 임베드와 어태치먼트용 파일을 생성해 반환한다.
    """
    now = datetime.datetime.now( tz = ZoneInfo( "Asia/Seoul" ) )
    embed = discord.Embed( title = f"{ now.year }년 { now.month }월 { now.day }일 { weekdays[ now.weekday() ] }요일 타임라인" )

    genChart()

    with open( "tt.png", 'rb' ) as f:
        chart = discord.File( f )

    embed.set_image( url = "attachment://tt.png" )

    return chart, embed


async def updateTimeline( faust: "Faust" ):
    """
    최신 타임라인 메시지를 업데이트한다.
    """
    chart, embed = generateTimeline()

    latestTimelineMsg = [ msg async for msg in faust.info.channel_timeline.history( limit = 1 ) ][ 0 ]
    # latestTimeline = latestTimelineMsg.embeds[ 0 ]

    # if not latestTimeline.title:
    #     raise Exception( "임베드에 제목이 없음" )
    # latestTimelineDate = stringToDate( latestTimeline.title )
    # if not latestTimelineDate:
    #     raise Exception( "임베드 제목이 올바르지 않은 형식임" )

    await latestTimelineMsg.edit( attachments = [ chart ], embed = embed, view = TimelineView() )


async def createTimeline( faust: "Faust" ):
    """
    타임라인 채널에 새로운 메시지를 전송한다.
    """
    chart, embed = generateTimeline()

    await faust.info.channel_timeline.send( file = chart, embed = embed, view = TimelineView() )


async def deleteTimelineView( msg: discord.Message ):
    """
    메시지에서 뷰를 제거한다.
    """
    await msg.edit( view = None )


class TimelineView( discord.ui.View ):
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
        await updateTimeline( interaction.client ) # type: ignore
        # await interaction.response.send_message( "대시보드를 성공적으로 새로고침했습니다.", ephemeral = True, delete_after = 10 )
        await interaction.response.defer()