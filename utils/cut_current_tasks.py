import json, datetime
from zoneinfo import ZoneInfo
from objects import Task


def cutCurrentTasks():
    with open( "data/current_tasks.json", 'r', encoding = "UTF-8" ) as f:
        currentTasks: list[ dict[ str, str ] ] = json.load( f )

    now = datetime.datetime.now( tz = ZoneInfo( "Asia/Seoul" ) )

    for currentTask in currentTasks:
        taskLeft = Task.toTaskObj( currentTask )
        taskRight = taskLeft.pop()  # 태스크 목록에서 제거 + 복사본 생성
        taskLeft.record()

        if not taskRight:   # 일어나서는 안되는 일
            continue
        
        taskRight.start = now
        taskRight.push()