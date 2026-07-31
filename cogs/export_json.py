import discord, json
from discord.ext.commands import Cog
from typing import Literal
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

        with open( "data/game_blacklist.txt", 'rb' ) as f:
            blacklist = discord.File( f )

        await i.response.send_message( files = [ currentTasks, today, timetable, blacklist ] )


    @discord.app_commands.command( name = "불러오기", description = "JSON 파일을 불러온다" )
    async def importJson( self, i: discord.Interaction, file: discord.Attachment, name: Literal[ "current_tasks.json", "today.json", "game_blacklist.txt" ] ):
        b = await file.read()

        if name == "current_tasks.json":
            with open( "data/current_tasks.json", 'wb' ) as f:
                f.write( b )

        elif name == "today.json":
            with open( "data/today.json", 'wb' ) as f:
                f.write( b )

        elif name == "game_blacklist.txt":
            with open( "data/game_blacklist.txt", 'wb' ) as f:
                f.write( b )

        else:
            await i.response.send_message( "잘못된 선택" )
            return

        await i.response.send_message( "파일 불러옴" )


    @discord.app_commands.command( name = "초기화", description = "JSON 파일을 초기화한다" )
    async def resetJson( self, i: discord.Interaction ):
        with open( "data/current_tasks.json", 'w' ) as f:
            json.dump( [], f )

        with open( "data/today.json", 'w' ) as f:
            json.dump( {}, f )

        genChart()

        await i.response.send_message( "JSON 초기화됨" )