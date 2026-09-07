import json, datetime, discord
from zoneinfo import ZoneInfo
from objects import Task, TaskEmbed, TaskEmbedView
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import Faust


async def cutCurrentTasks( faust: "Faust" ):
    """
    진행 중인 태스크를 현재 시점 기준으로 끊는다.
    (자정에 실행되는 것을 상정한 함수)
    """
    with open( "data/current_tasks.json", 'r', encoding = "UTF-8" ) as f:
        currentTasks: list[ dict[ str, str ] ] = json.load( f )

    now = datetime.datetime.now( tz = ZoneInfo( "Asia/Seoul" ) )
    yesterday235959 = ( now - datetime.timedelta( hours = 1 ) ).replace( hour = 23, minute = 59, second = 59 )

    leftTasks: list[ Task ] = []
    rightTasks: list[ Task ] = []

    for currentTask in currentTasks:
        taskLeft = Task.toTaskObj( currentTask )
        taskRight = taskLeft.pop()  # 태스크 목록에서 제거 + 복사본 생성
        taskLeft.record( yesterday235959 )
        leftTasks.append( taskLeft )

        if taskRight is False:   # 일어나서는 안되는 일
            continue
        rightTasks.append( taskRight )

    for leftTask in leftTasks:
        if leftTask.msgID is None:
            continue

        try:
            msg = await faust.info.channel_log.fetch_message( leftTask.msgID )
            embed = TaskEmbed( leftTask, faust.info )
            await msg.edit( embed = embed, view = None )
        except discord.errors.NotFound:
            continue

    for rightTask in rightTasks:
        rightTask.start = now
        rightTask.ID = now.strftime( "%H%M%S" ) + str( ord( rightTask.name[0] ) )

        embed = TaskEmbed( rightTask, faust.info )
        msg = await faust.info.channel_log.send( embed = embed, view = TaskEmbedView() )

        rightTask.msgID = msg.id
        rightTask.push()