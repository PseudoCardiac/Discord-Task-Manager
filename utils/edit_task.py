import json
from datetime import datetime
from zoneinfo import ZoneInfo
from objects import Task


def getTodaysTasks():
    with open( "data/today.json", 'r', encoding = "UTF-8" ) as f:
        today: dict[ str, list[ dict[ str, str ] ] ] = json.load( f )

    todayStr = datetime.now( tz = ZoneInfo( "Asia/Seoul" ) ).strftime( "%Y%m%d" )
    todayTasks = today.get( todayStr )
    
    if todayTasks is None:
        return None

    return list( map( lambda x: Task.toTaskObj( x ), todayTasks ) )