import json
from datetime import datetime
from zoneinfo import ZoneInfo
from .category import Category


class Task:
    def __init__( self, name: str, category: Category, desc = "", start = None, end: datetime | None = None, id: str = "", msgID: int | None = None ):
        self.name = name
        self.category = category
        self.desc = desc
        self.start = datetime.now( tz = ZoneInfo( "Asia/Seoul" ) ) if start is None else start
        with open( "data/today.json", 'r', encoding = "UTF-8" ) as f:
            today: dict[ str, list[ dict[ str, str ] ] ] = json.load( f )
        todaysRecord = today.get( self.start.strftime( "%Y%m%d" ) ) or []
        self.number = len( todaysRecord ) + 1
        self.end = end
        self.ID = self.start.strftime( "%H%M%S" ) + str( ord( name[0] ) ) if id == "" else id
        self.msgID = msgID


    def toJsonObj( self ):
        """
        태스크 오브젝트를 딕셔너리 오브젝트로 변환한다
        """
        obj: dict[ str, str ] = {}

        obj[ "name" ] = self.name
        obj[ "category" ] = str( self.category )
        obj[ "desc" ] = self.desc
        obj[ "number" ] = str( self.number )
        obj[ "start" ] = self.start.strftime( "%Y/%m/%d %H:%M:%S %z" )
        obj[ "end" ] = self.end.strftime( "%Y/%m/%d %H:%M:%S %z" ) if self.end is not None else "None"
        obj[ "id" ] = self.ID
        obj[ "msgID" ] = str( self.msgID ) if self.msgID is not None else "None"

        return obj


    @staticmethod
    def toTaskObj( d: dict[ str, str ] ):
        """
        딕셔너리 오브젝트를 태스크 오브젝트로 변환한다
        """
        return Task(
            name = d[ "name" ],
            category = Category( int( d[ "category" ] ) ),
            desc = d[ "desc" ],
            start = datetime.strptime( d[ "start" ], "%Y/%m/%d %H:%M:%S %z" ),
            end = datetime.strptime( d[ "end" ], "%Y/%m/%d %H:%M:%S %z" ) if d[ "end" ] != "None" else None,
            id = d[ "id" ],
            msgID= int( d[ "msgID" ] ) if d[ "msgID" ] != "None" else None
        )


    def push( self ):
        """
        현재 기록 중인 태스크 목록에 self를 push한다
        """
        with open( "data/current_tasks.json", 'r', encoding = "UTF-8" ) as f:
            currentTasks: list[ dict[ str, str ] ] = json.load( f )

        currentTasks.append( self.toJsonObj() )
        
        with open( "data/current_tasks.json", 'w+', encoding = "UTF-8" ) as f:
            json.dump( currentTasks, f, indent = 4 )


    def pop( self ):
        """
        현재 기록 중인 태스크 목록에서 self를 pop한다
        """
        jsonObj = self.toJsonObj()

        with open( "data/current_tasks.json", 'r', encoding = "UTF-8" ) as f:
            currentTasks: list[ dict[ str, str ] ] = json.load( f )

        if not currentTasks:
            return False

        idx = 0

        for i in range( len( currentTasks ) ):
            if currentTasks[i][ "id" ] == jsonObj[ "id" ]:
                break
            idx += 1
        else:
            return False

        # try:
        #     idx = currentTasks.index( jsonObj )
        # except ValueError:
        #     return False

        task = currentTasks.pop( idx )

        with open( "data/current_tasks.json", 'w+', encoding = "UTF-8" ) as f:
            json.dump( currentTasks, f, indent = 4 )

        return Task.toTaskObj( task )


    def exists( self ):
        """
        현재 기록 중인 태스크 목록에 self가 존재하는지 여부를 반환한다
        """
        jsonObj = self.toJsonObj()

        with open( "data/current_tasks.json", 'r', encoding = "UTF-8" ) as f:
            currentTasks: list[ dict[ str, str ] ] = json.load( f )

        if not currentTasks:
            return False

        for i in range( len( currentTasks ) ):
            if currentTasks[i][ "id" ] == jsonObj[ "id" ]:
                return True

        return False


    def record( self, setEndTimeToNow = True ):
        """
        self의 종료 시간을 현재 시간으로 설정하고 오늘의 기록에 추가한다
        """
        with open( "data/today.json", 'r', encoding = "UTF-8" ) as f:
            today: dict[ str, list[ dict[ str, str ] ] ] = json.load( f )

        if setEndTimeToNow:
            self.end = datetime.now( tz = ZoneInfo( "Asia/Seoul" ) )
            
        if today.get( self.start.strftime( "%Y%m%d" ) ):    # 오늘 기록이 있음
            today[ self.start.strftime( "%Y%m%d" ) ].append( self.toJsonObj() )
        else:   # 오늘 기록이 없음
            today[ self.start.strftime( "%Y%m%d" ) ] = [ self.toJsonObj() ]

        with open( "data/today.json", 'w+', encoding = "UTF-8" ) as f:
            json.dump( today, f, indent = 4 )


    def edit( self, name = "", category = None, desc = "" ):
        """
        self의 name, category, 또는 desc를 수정한다
        """
        self.pop()

        if name != "":
            self.name = name
        if category is not None:
            self.category = category
        if desc != "":
            self.desc = desc

        self.push()


    def editFull( self, name, category, desc, start, end ):
        """
        self의 name, category, desc, start, end를 수정한다. 완료된 태스크 전용!
        """
        if name != "":
            self.name = name
        if category is not None:
            self.category = Category( int( category ) )
        if desc != "":
            self.desc = desc
        if start != "":
            hour = int( start[ :2 ] )
            minute = int( start[ 2:4 ] )
            second = int( start[ 4: ] )
            start = datetime.now( tz = ZoneInfo( "Asia/Seoul" ) ).replace( hour = hour, minute = minute, second = second )

            self.start = start
            self.ID = start.strftime( "%H%M%S" ) + str( ord( self.name[0] ) )
        if end != "":
            hour = int( end[ :2 ] )
            minute = int( end[ 2:4 ] )
            second = int( end[ 4: ] )
            self.end = datetime.now( tz = ZoneInfo( "Asia/Seoul" ) ).replace( hour = hour, minute = minute, second = second )


    @staticmethod
    def get( id: str ):
        """
        진행 중인 태스크와 완료된 태스크 목록에서 id를 가진 태스크를 찾는다.
        """
        # 완료된 목록에서 찾기
        with open( "data/today.json", 'r', encoding = "UTF-8" ) as f:
            todays: dict[ str, list[ dict[ str, str ] ] ] = json.load( f )

        today = todays.get( datetime.now( tz = ZoneInfo( "Asia/Seoul" ) ).strftime( "%Y%m%d" ) )
        if today:
            for task in today:
                if task[ "id" ] == id:
                    return Task.toTaskObj( task )

        # 완료된 목록에 없을 시, 진행 중인 태스크 목록에서 찾기
        with open( "data/current_tasks.json", 'r', encoding = "UTF-8" ) as f:
            currentTasks: list[ dict[ str, str ] ] = json.load( f )

        for task in currentTasks:
            if task[ "id" ] == id:
                return Task.toTaskObj( task )

        else:
            return False