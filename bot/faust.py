import discord, os, json
from discord.ext.commands import Bot
from dotenv import load_dotenv
from objects import Info
from cogs import RegisterTaskCog, DailyReportCog, ExportJsonCog, PresenceListener


class Faust( Bot ):
    def __init__( self ):
        super().__init__( command_prefix = "@Faust", intents = discord.Intents.all() )


    async def on_ready( self ):
        self.info = Info()
        await self.info.init( self )
        await self.add_cog( RegisterTaskCog( self ) )
        await self.add_cog( DailyReportCog( self ) )
        await self.add_cog( ExportJsonCog( self ) )
        await self.add_cog( PresenceListener( self ) )
        await self.tree.sync()
        print( "파우스트 온라인." )


    def runBot( self ):
        load_dotenv( "../.env" )
        super().run( os.environ.get( "FAUST_TOKEN" ) ) # type: ignore


FAUST = Faust()