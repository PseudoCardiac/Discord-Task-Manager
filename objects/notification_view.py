import discord
from utils import minutesToHours
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .task import Task


class NotifyLaterModal( discord.ui.Modal ):
    def __init__( self, task: "Task", action ):
        super().__init__(
            title = "알림 설정",
            timeout = None
        )
        self.task = task
        self.action = action

    minutes = discord.ui.TextInput( label = "다시 알릴 시간 (분)", style = discord.TextStyle.short )

    async def on_submit( self, interaction: discord.Interaction ):
        # await interaction.response.defer( ephemeral = True, thinking = True )
        await interaction.response.send_message( f"{ minutesToHours( int( self.minutes.value ) ) } 후 다시 알리겠습니다.", ephemeral = True )
        await self.action( int( self.minutes.value ), self.task, interaction.client )


class NotifyLaterButton( discord.ui.Button ):
    def __init__( self, task: "Task", action ):
        super().__init__(
            style = discord.ButtonStyle.primary,
            label = "다시 알림"
        )
        self.task = task
        self.action = action

    async def callback( self, interaction: discord.Interaction ):
        await interaction.response.send_modal( NotifyLaterModal( self.task, self.action ) )


class NotifyHideButton( discord.ui.Button ):
    def __init__( self ):
        super().__init__(
            style = discord.ButtonStyle.secondary,
            label = "숨기기"
        )

    async def callback( self, interaction: discord.Interaction ):
        await interaction.message.delete()  # type: ignore


class NotificationView( discord.ui.View ):
    def __init__( self, task: "Task", action ):
        super().__init__( timeout = None )

        self.add_item( NotifyLaterButton( task, action ) )
        self.add_item( NotifyHideButton() )