from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import Faust
    from objects import Task
from objects.notification_view import NotificationView


async def notify( task: "Task", faust: "Faust" ):
    taskExists = task.pop()
    if not taskExists:
        return

    await faust.info.channel_log.send( f"<@{ faust.info.scy.id }> 알림: { task.name }", view = NotificationView( task ) )