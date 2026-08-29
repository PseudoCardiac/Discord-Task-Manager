import discord, json
from discord.ext.commands import Cog
from typing import Literal
from utils import genChart, updateTimeline


class FileManagementCog( Cog ):
    @discord.app_commands.command( name = "내보내기", description = "JSON 파일을 내보냅니다." )
    async def exportJson( self, i: discord.Interaction ):
        await i.response.defer( ephemeral = True, thinking = True )

        with open( "data/current_tasks.json", 'rb' ) as f:
            currentTasks = discord.File( f )

        with open( "data/today.json", 'rb' ) as f:
            today = discord.File( f )

        with open( "tt.png", 'rb' ) as f:
            timetable = discord.File( f )

        with open( "data/game_blacklist.txt", 'rb' ) as f:
            blacklist = discord.File( f )

        await i.followup.send( files = [ currentTasks, today, timetable, blacklist ] )


    @discord.app_commands.command( name = "불러오기", description = "시스템 파일을 불러옵니다." )
    async def importJson( self, i: discord.Interaction, file: discord.Attachment, name: Literal[ "current_tasks.json", "today.json", "game_blacklist.txt" ] ):
        await i.response.defer( ephemeral = True, thinking = True )

        b = await file.read()
        text = b.decode( "UTF-8" )

        if name == "current_tasks.json":
            with open( "data/current_tasks.json", 'w+', encoding = "UTF-8" ) as f:
                f.write( text )

        elif name == "today.json":
            with open( "data/today.json", 'w+', encoding = "UTF-8" ) as f:
                f.write( text )

        elif name == "game_blacklist.txt":
            with open( "data/game_blacklist.txt", 'w+', encoding = "UTF-8" ) as f:
                f.write( text )

        else:
            await i.followup.send( "잘못된 옵션입니다." )
            return

        await i.followup.send( "시스템 파일을 성공적으로 불러왔습니다." )


    @discord.app_commands.command( name = "초기화", description = "블랙리스트를 제외한 시스템 파일을 초기화합니다." )
    async def resetJson( self, i: discord.Interaction ):
        await i.response.defer( ephemeral = True, thinking = True )

        with open( "data/current_tasks.json", 'w+' ) as f:
            json.dump( [], f )

        with open( "data/today.json", 'w+' ) as f:
            json.dump( {}, f )

        genChart()

        await i.followup.send( "시스템 파일을 성공적으로 초기화했습니다." )


    @discord.app_commands.command( name = "새로고침", description = "대시보드를 새로고침합니다." )
    async def refreshDashboard( self, i: discord.Interaction ):
        await i.response.defer( ephemeral = True, thinking = True )

        genChart()
        await updateTimeline( i.client )   # type: ignore

        await i.followup.send( "대시보드를 성공적으로 새로고침했습니다." )