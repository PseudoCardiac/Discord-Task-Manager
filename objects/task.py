import json
from datetime import datetime
from zoneinfo import ZoneInfo
from .category import Category


class Task:
    def __init__( self, name: str, category: Category, desc = "", start = None, end: datetime | None = None, id: str | None = None ):
        self.name = name
        self.category = category
        self.desc = desc
        self.start = datetime.now( tz = ZoneInfo( "Asia/Seoul" ) ) if start is None else start
        with open( "data/today.json", 'r', encoding = "UTF-8" ) as f:
            today: dict[ str, list[ dict[ str, str ] ] ] = json.load( f )
        todaysRecord = today.get( self.start.strftime( "%Y%m%d" ) ) or []
        self.number = len( todaysRecord ) + 1
        self.end = end
        self.ID = self.start.strftime( "%Y%m%d" ) + str( ord( name[0] ) ) if id is None else id


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
            id = d[ "id" ]
        )


    def push( self ):
        """
        현재 기록 중인 태스크 목록에 self를 push한다
        """
        with open( "data/current_tasks.json", 'r', encoding = "UTF-8" ) as f:
            currentTasks: list[ dict[ str, str ] ] = json.load( f )

        currentTasks.append( self.toJsonObj() )
        
        with open( "data/current_tasks.json", 'w', encoding = "UTF-8" ) as f:
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

        with open( "data/current_tasks.json", 'w', encoding = "UTF-8" ) as f:
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


    def record( self ):
        """
        self의 종료 시간을 현재 시간으로 설정하고 오늘의 기록에 추가한다
        """
        with open( "data/today.json", 'r', encoding = "UTF-8" ) as f:
            today: dict[ str, list[ dict[ str, str ] ] ] = json.load( f )

        self.end = datetime.now( tz = ZoneInfo( "Asia/Seoul" ) )
        if today.get( self.start.strftime( "%Y%m%d" ) ):    # 오늘 기록이 있음
            today[ self.start.strftime( "%Y%m%d" ) ].append( self.toJsonObj() )
        else:   # 오늘 기록이 없음
            today[ self.start.strftime( "%Y%m%d" ) ] = [ self.toJsonObj() ]

        with open( "data/today.json", 'w', encoding = "UTF-8" ) as f:
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