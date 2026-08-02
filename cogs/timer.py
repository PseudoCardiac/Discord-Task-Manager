from discord.ext import tasks
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import Faust
    from objects import Task
from objects import NotificationView
from utils import minutesToHours


async def setTimer( min: int, task: "Task", faust: "Faust" ):
    @tasks.loop( minutes = float( min ), count = 2 )
    async def timer():
        if timer.current_loop == 0:
            return

        taskExists = task.exists()
        if not taskExists:
            return

        await faust.info.channel_log.send( f"<@{ faust.info.scy.id }>\n{ task.name } 태스크가 시작된 이후 { minutesToHours( min ) }이 지났습니다.", view = NotificationView( task, setTimer ) )

    await timer.start()