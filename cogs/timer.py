from discord.ext import tasks
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import Faust
    from objects import Task
from utils import notify


def newTimer( min: int, task: "Task", faust: "Faust" ):
    @tasks.loop( seconds = float( min ), count = 2 ) # TODO change seconds to minutes after testing
    async def timer():
        if timer.current_loop == 0:
            return

        await notify( task, faust )

    return timer