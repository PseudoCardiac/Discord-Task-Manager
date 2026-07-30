import discord
from discord.ext.commands import Cog


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