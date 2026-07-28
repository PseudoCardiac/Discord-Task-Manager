import json


with open( "data/current_tasks.json", 'r', encoding = "UTF-8" ) as f:
    d = json.load( f )


print( type( d ) )