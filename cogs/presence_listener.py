import discord, json
from discord.ext.commands import Cog
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import Faust
from objects import Category, Task
from utils import updateTimetable


class PresenceListener( Cog ):
    def __init__( self, faust: "Faust" ):
        self.faust = faust

        with open( "data/game_blacklist.txt", 'r', encoding = "UTF-8" ) as f:
            self.blacklist = f.readlines()


    @Cog.listener( name = "on_presence_update" )
    async def on_presence_update( self, before: discord.Member, after: discord.Member ):
        if before.guild != self.faust.info.guild:
            return

        if before != self.faust.info.scy:
            return

        gamesBefore = [ game for game in before.activities if game.type == discord.ActivityType.playing \
                        and game.name not in self.blacklist]
        gamesAfter = [ game for game in after.activities if game.type == discord.ActivityType.playing \
                       and game.name not in self.blacklist ]

        stoppedPlaying = [ game for game in gamesBefore if game.name not in [ _game.name for _game in gamesAfter ] ]
        startedPlaying = [ game for game in gamesAfter if game.name not in [ _game.name for _game in gamesBefore ] ]

        if not ( stoppedPlaying or startedPlaying ):
            return

        with open( "data/current_tasks.json", 'r', encoding = "UTF-8" ) as f:
            currentTasks: list[ dict[ str, str ] ] = json.load( f )

        if stoppedPlaying:
            for game in stoppedPlaying:
                for currentTask in currentTasks:
                    if currentTask[ "name" ] == game.name:
                        task = Task.toTaskObj( currentTask )
                        break
                else:
                    # game not found
                    break
                
                task.pop()
                task.record()

            await updateTimetable( self.faust )

        if startedPlaying:
            for game in startedPlaying:
                task = Task(
                    name = game.name,   # type: ignore
                    category = Category.GAME
                )
                task.push()