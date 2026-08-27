import discord, os, asyncio
from discord.ext.commands import Bot
from dotenv import load_dotenv
from objects import Info
from cogs import TaskManagementCog, DailyReportCog, ExportJsonCog, PresenceListener
from utils import TimelineView


class Faust( Bot ):
    def __init__( self ):
        super().__init__( command_prefix = "@Faust", intents = discord.Intents.all() )


    async def on_ready( self ):
        self.info = Info()
        await self.info.init( self )
        await self.add_cog( TaskManagementCog( self ) )
        await self.add_cog( DailyReportCog( self ) )
        await self.add_cog( ExportJsonCog( self ) )
        await self.add_cog( PresenceListener( self ) )
        self.add_view( TimelineView() )
        # await self.tree.sync()
        print( "파우스트 온라인." )


    def runBot( self ):
        load_dotenv( "../.env" )
        super().run( os.environ.get( "FAUST_TOKEN" ) ) # type: ignore


FAUST = Faust()