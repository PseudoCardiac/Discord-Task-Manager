import discord, datetime
from zoneinfo import ZoneInfo
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import Faust
from .chart import genChart
from .string_to_date import stringToDate


weekdays = [ '월', '화', '수', '목', '금', '토', '일' ]


def generateTimeline( targetDate: datetime.date | None = None ):
    """
    전달된 날짜 혹은 호출 시각을 기준으로 타임라인 임베드와 어태치먼트용 파일을 생성해 반환한다.
    """
    if targetDate is None:
        targetDate = datetime.datetime.now( tz = ZoneInfo( "Asia/Seoul" ) )

    embed = discord.Embed(
        title = f"{ targetDate.year }년 { targetDate.month }월 { targetDate.day }일 { weekdays[ targetDate.weekday() ] }요일 타임라인",
        color = 16757172
    )

    genChart( targetDate )

    with open( "tt.png", 'rb' ) as f:
        chart = discord.File( f )

    embed.set_image( url = "attachment://tt.png" )

    return chart, embed


async def getLatestTimelineMessage( faust: "Faust" ):
    with open( "data/latest_timeline_msg_id.txt", 'r' ) as f:
        msgID = f.readline()

    try:
        return await faust.info.channel_timeline.fetch_message( int( msgID ) )
    except discord.NotFound:
        return False
    except ValueError:
        return False


async def updateTimeline( faust: "Faust", yesterday = False ):
    """
    최신 타임라인 메시지를 업데이트한다.
    """
    # ===== 최신 타임라인 메시지 페치 =====
    latestTimelineMsg = await getLatestTimelineMessage( faust )

    # 인식된 최신 타임라인 메시지가 존재하지 않음
    if latestTimelineMsg is False:
        latestTimelineMsg = await createTimeline( faust )

    latestTimelineMsgEmbeds = latestTimelineMsg.embeds
    if latestTimelineMsgEmbeds == []:
        raise Exception( "잘못된 타임라인 메시지 형식" )
    
    latestTimeline = latestTimelineMsg.embeds[ 0 ]
    # =====================================

    if not latestTimeline.title:
        raise Exception( "임베드에 제목이 없음" )
    latestTimelineDate = stringToDate( latestTimeline.title )
    if not latestTimelineDate:
        raise Exception( "임베드 제목이 올바르지 않은 형식임" )

    # ===== 기존 임베드와 날짜 비교 =====
    tz = ZoneInfo( "Asia/Seoul" )
    
    if yesterday:
        targetDate = ( datetime.datetime.now( tz = tz ) - datetime.timedelta( days = 1 ) ).date()
    else:
        targetDate = datetime.datetime.now( tz = tz ).date()

    if latestTimelineDate == targetDate:
        # 타임라인 수정
        await editTimeline( latestTimelineMsg, targetDate )
    else:
        # 타임라인 생성
        await deleteTimelineView( latestTimelineMsg )
        await createTimeline( faust, targetDate )
    # ===================================


async def editTimeline( latestTimelineMsg: discord.Message, targetDate: datetime.date | None = None ):
    """
    타임라인 채널의 최신 메시지를 수정한다.
    """
    chart, embed = generateTimeline( targetDate )

    await latestTimelineMsg.edit( attachments = [ chart ], embed = embed, view = TimelineView() )


async def createTimeline( faust: "Faust", targetDate: datetime.date | None = None ):
    """
    타임라인 채널에 새로운 메시지를 전송한다.
    """
    chart, embed = generateTimeline( targetDate )

    msg = await faust.info.channel_timeline.send( file = chart, embed = embed, view = TimelineView() )

    with open( "data/latest_timeline_msg_id.txt", 'w+' ) as f:
        f.write( str( msg.id ) )

    return msg


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
        # await interaction.response.send_message( "대시보드를 성공적으로 새로고침했습니다." )
        await interaction.response.defer()