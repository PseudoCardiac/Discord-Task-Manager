import discord, datetime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.faust import Faust
from utils.chart import genChart


async def updateTimetable( faust: "Faust" ):
    embed = discord.Embed( title = datetime.datetime.now().strftime( "%Y%m%d" ) )

    genChart()

    with open( "tt.png", 'rb' ) as f:
        chart = discord.File( f )

    embed.set_image( url = "attachment://tt.png" )
    await faust.info.msg_timetable.edit( attachments = [ chart ], embed = embed )