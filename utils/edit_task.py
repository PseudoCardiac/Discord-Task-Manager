import json, discord
from datetime import datetime
from zoneinfo import ZoneInfo
from objects.task import Task


def getTodaysTasks():
    with open( "data/today.json", 'r', encoding = "UTF-8" ) as f:
        today: dict[ str, list[ dict[ str, str ] ] ] = json.load( f )

    todayStr = datetime.now( tz = ZoneInfo( "Asia/Seoul" ) ).strftime( "%Y%m%d" )
    todayTasks = today.get( todayStr )
    
    if todayTasks is None:
        return []

    return list( map( lambda x: Task.toTaskObj( x ), todayTasks ) )


def editTodaysTasks( tasks: list[ Task ] ):
    with open( "data/today.json", 'r', encoding = "UTF-8" ) as f:
        today: dict[ str, list[ dict[ str, str ] ] ] = json.load( f )

    todayStr = datetime.now( tz = ZoneInfo( "Asia/Seoul" ) ).strftime( "%Y%m%d" )

    if today.get( todayStr ) is None:
        today[ todayStr ] = []

    today[ todayStr ] = list( map( lambda x: x.toJsonObj(), tasks ) )

    with open( "data/today.json", 'w', encoding = "UTF-8" ) as f:
        json.dump( today, f, indent = 4 )


def editFinishedTask( taskID, name, desc, category, start, end ):
    todaysTasks = getTodaysTasks()

    for task in todaysTasks:
        if task.ID == taskID:
            task.editFull( name, category, desc, start, end )
            return task
    else:
        assert Exception( "주어진 ID와 일치하는 태스크를 찾을 수 없었음" )
        return


# async def editFinishedTaskEmbed( faust: "Faust", task: Task ):
#     msgID = task.msgID
#     if msgID is None:
#         assert Exception( "수정할 태스크 임베드의 메시지 ID 정보가 없음" )
#         return

#     msg = await faust.info.channel_log.fetch_message( msgID )
#     await msg.edit( embed = TaskEmbed( task, faust.info ) )