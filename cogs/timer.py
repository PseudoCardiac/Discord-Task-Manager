import discord
from discord.ext import tasks
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import Faust
    from objects import Task
from objects import NotificationView


async def setTimer( min: int, task: "Task", faust: "Faust" ):
    @tasks.loop( seconds = float( min ), count = 2 ) # TODO change seconds to minutes after testing
    async def timer():
        if timer.current_loop == 0:
            return

        taskExists = task.exists()
        if not taskExists:
            return

        await faust.info.channel_log.send( f"<@{ faust.info.scy.id }> 알림: { task.name }", view = NotificationView( task, setTimer ) )

    await timer.start()