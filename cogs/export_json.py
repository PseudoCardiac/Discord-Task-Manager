import discord, json
from discord.ext.commands import Cog
from utils import genChart


class ExportJsonCog( Cog ):
    @discord.app_commands.command( name = "내보내기", description = "JSON 파일을 내보낸다" )
    async def exportJson( self, i: discord.Interaction ):
        with open( "data/current_tasks.json", 'rb' ) as f:
            currentTasks = discord.File( f )

        with open( "data/today.json", 'rb' ) as f:
            today = discord.File( f )

        with open( "tt.png", 'rb' ) as f:
            timetable = discord.File( f )

        await i.response.send_message( files = [ currentTasks, today, timetable ] )


    @discord.app_commands.command( name = "초기화", description = "JSON 파일을 초기화한다" )
    async def resetJson( self, i: discord.Interaction ):
        with open( "data/current_tasks.json", 'w' ) as f:
            json.dump( {}, f )

        with open( "data/today.json", 'w' ) as f:
            json.dump( {}, f )

        genChart()

        await i.response.send_message( "JSON 초기화됨" )