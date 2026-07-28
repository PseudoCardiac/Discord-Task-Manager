import json
from datetime import datetime
from objects.category import Category


class Task:
    def __init__( self, name: str, category: Category, desc = "", number = 0, start = None, end: datetime | None = None ):
        self.name = name
        self.category = category
        self.desc = desc
        self.start = datetime.now() if start is None else start
        with open( "data/today.json", 'r', encoding = "UTF-8" ) as f:
            today = json.load( f )
        todaysRecord = today.get( self.start.strftime( "%Y%m%d" ) ) or []
        self.number = len( todaysRecord ) + 1
        self.end = end


    def toJsonObj( self ):
        obj: dict[ str, str ] = {}

        obj[ "name" ] = self.name
        obj[ "category" ] = str( self.category )
        obj[ "desc" ] = self.desc
        obj[ "number" ] = str( self.number )
        obj[ "start" ] = self.start.strftime( "%d/%m/%Y, %H:%M:%S" )
        obj[ "end" ] = self.end.strftime( "%d/%m/%Y, %H:%M:%S" ) if self.end is not None else "None"

        return obj


    @staticmethod
    def toTaskObj( d: dict[ str, str ] ):
        return Task(
            name = d[ "name" ],
            category = Category( int( d[ "category" ] ) ),
            desc = d[ "desc" ],
            number = int( d[ "number" ] ),
            start = datetime.strptime( d[ "start" ], "%d/%m/%Y, %H:%M:%S" ),
            end = datetime.strptime( d[ "end" ], "%d/%m/%Y, %H:%M:%S" ) if d[ "end" ] != "None" else None
        )


    def push( self ):
        with open( "data/current_task.json", 'r', encoding = "UTF-8" ) as f:
            task = json.load( f )

        if task != {}:
            return False

        with open( "data/current_task.json", 'w', encoding = "UTF-8" ) as f:
            json.dump( self.toJsonObj(), f, indent = 4 )


    @staticmethod
    def pop():
        with open( "data/current_task.json", 'r', encoding = "UTF-8" ) as f:
            task = json.load( f )

        if task == {}:
            return False

        with open( "data/current_task.json", 'w', encoding = "UTF-8" ) as f:
            json.dump( {}, f, indent = 4 )

        return Task.toTaskObj( task )


    def record( self ):
        with open( "data/today.json", 'r', encoding = "UTF-8" ) as f:
            today = json.load( f )

        self.end = datetime.now()
        if today.get( self.start.strftime( "%Y%m%d" ) ):
            today[ self.start.strftime( "%Y%m%d" ) ].append( self.toJsonObj() )
        else:
            today[ self.start.strftime( "%Y%m%d" ) ] = [ self.toJsonObj() ]

        with open( "data/today.json", 'w', encoding = "UTF-8" ) as f:
            json.dump( today, f, indent = 4 )