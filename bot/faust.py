import discord, os, asyncio, tracemalloc
from discord.ext.commands import Bot
from dotenv import load_dotenv
from objects import Info, TaskEmbedView
from cogs import TaskManagementCog, DailyReportCog, FileManagementCog, PresenceListener
from utils import TimelineView


tracemalloc.start()


class Faust( Bot ):
    def __init__( self ):
        super().__init__( command_prefix = "@Faust", intents = discord.Intents.all() )


    async def setup_hook( self ):
        self.info = Info()
        await self.info.init( self )
        await self.add_cog( TaskManagementCog( self ) )
        await self.add_cog( DailyReportCog( self ) )
        await self.add_cog( FileManagementCog( self ) )
        await self.add_cog( PresenceListener( self ) )
        self.add_view( TimelineView() )
        self.add_view( TaskEmbedView() )
        # await self.tree.sync()
        self.memory_task = asyncio.create_task( self.memorySnapshotTask() )


    async def memorySnapshotTask( self ):
        snapshot1 = None

        while True:
            snapshot2 = tracemalloc.take_snapshot()

            if snapshot1:
                top_stats = snapshot2.compare_to( snapshot1, 'lineno' )
                statMsg = "[ 메모리 증가 Top 10 ]\n"

                for stat in top_stats[:10]:
                    statMsg += statMsg + str( stat ) + '\n'

                await self.info.scy.send( statMsg )

            else:
                await self.info.scy.send( "메모리 모니터링 개시" )

            snapshot1 = snapshot2
            await asyncio.sleep( 3600 )


    async def on_ready( self ):
        print( "파우스트 온라인." )


    def runBot( self ):
        load_dotenv( "../.env" )
        super().run( os.environ.get( "FAUST_TOKEN" ) ) # type: ignore


FAUST = Faust()