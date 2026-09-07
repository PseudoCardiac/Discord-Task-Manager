import discord, re
from datetime import datetime
from zoneinfo import ZoneInfo
from .info import Info
from .category import Category
from typing import TYPE_CHECKING
# if TYPE_CHECKING:
from .task import Task
from utils import minutesToHours, updateTimeline, editTaskEmbedAborted


weekdays = [ '월', '화', '수', '목', '금', '토', '일' ]


class TaskEmbed( discord.Embed ):
    def __init__( self, task: "Task", info: Info ):
        super().__init__(
            title = task.name,
            description = f"{ task.desc }\n<@&{ info.tag[ task.category ].id }> · <t:{ round( task.start.timestamp() ) }:R> 시작",
            color = info.tagColor[ task.category ]
        )
        self.task = task
        self.set_footer( text = f"{ task.start.year }년 { task.start.month }월 { task.start.day }일 { weekdays[ task.start.weekday() ] }요일 #{ task.ID }" )

        if self.task.end is not None:
            self.description = f"{ task.desc }\n<@&{ info.tag[ task.category ].id }> · { minutesToHours( round( ( self.task.end - self.task.start ).total_seconds() ) // 60 ) }동안 진행"


class TaskEmbedView( discord.ui.View ):
    def __init__( self ):
        super().__init__( timeout = None )
        self.add_item( FinishButton() )
        self.add_item( AbortButton() )
        self.add_item( TextEditButton() )
        self.add_item( CategoryEditButton() )


class FinishButton( discord.ui.Button ):
    def __init__( self ):
        super().__init__(
            style = discord.ButtonStyle.primary,
            label = "태스크 완료",
            row = 0,
            custom_id = "FinishButton"
        )

    async def callback( self, interaction: discord.Interaction ):
        await interaction.response.defer( ephemeral = True, thinking = True )

        if interaction.message is None:
            raise Exception( "No Message" )
        
        view = ConfirmView( interaction.message, True )
        await interaction.followup.send( content = "태스크를 완료하시겠습니까?", view = view )


class TextEditButton( discord.ui.Button ):
    def __init__( self ):
        super().__init__(
            style = discord.ButtonStyle.secondary,
            label = "제목 · 세부 사항 수정",
            row = 1,
            custom_id = "TextEditButton"
        )

    async def callback( self, interaction: discord.Interaction ):
        if interaction.message is None:
            raise Exception( "No Message" )
        
        task = Task.fromEmbed( interaction.message.embeds[ 0 ] )
        
        if task is None:
            raise Exception( "No Task" )
        
        await interaction.response.send_modal( TextEditModal( self, task ) )


class TextEditModal( discord.ui.Modal ):
    def __init__( self, button: TextEditButton, task: Task ):
        super().__init__(
            title = "태스크 제목 · 세부 사항 수정",
            timeout = None
        )
        self.button = button
        self.task = task

    name = discord.ui.TextInput( label = "태스크 제목", style = discord.TextStyle.short, required = False )
    desc = discord.ui.TextInput( label = "태스크 세부 사항", style = discord.TextStyle.short, required = False )


    async def on_submit( self, i: discord.Interaction ):
        await i.response.defer( ephemeral = True, thinking = True )

        if not self.name and not self.desc:
            await i.followup.send( "태스크가 수정되지 않았습니다. 무언가 잘못되었군요." )
        else:
            self.task.edit( name = self.name.value, desc = self.desc.value )
            await i.message.edit( embed = TaskEmbed( self.task, i.client.info ) )    # type: ignore
            await i.followup.send( "태스크가 성공적으로 수정되었습니다." )


class CategoryEditButton( discord.ui.Button ):
    def __init__( self ):
        super().__init__(
            style = discord.ButtonStyle.secondary,
            label = "카테고리 수정",
            row = 1,
            custom_id = "CategoryEditButton"
        )

    async def callback( self, interaction: discord.Interaction ):
        await interaction.response.defer( ephemeral = True, thinking = True )

        if interaction.message is None:
            raise Exception( "No Message" )

        task = Task.fromEmbed( interaction.message.embeds[ 0 ] )
        
        await interaction.followup.send( view = CategoryEditView( interaction.message ) )


class CategoryEditView( discord.ui.View ):
    def __init__( self, msg: discord.Message ):
        super().__init__( timeout = None )

        self.add_item( CategorySelect( msg ) )


class CategorySelect( discord.ui.RoleSelect ):
    def __init__( self, msg: discord.Message ):
        super().__init__()
        self.msg = msg
        self.task = Task.fromEmbed( msg.embeds[ 0 ] )


    async def callback( self, interaction: discord.Interaction ):
        await interaction.response.defer( ephemeral = True, thinking = True )

        category = self.values[0]

        if category not in interaction.client.info.tag: # type: ignore
            await interaction.followup.send( "…파우스트는 카테고리가 아닙니다." )
            return

        self.task.edit( category = Category( interaction.client.info.tag.index( category ) ) )   # type: ignore
        await self.msg.edit( embed = TaskEmbed( self.task, interaction.client.info ) )    # type: ignore
        await interaction.followup.send( "태스크가 성공적으로 수정되었습니다." )


class AbortButton( discord.ui.Button ):
    def __init__( self ):
        super().__init__(
            style = discord.ButtonStyle.danger,
            label = "태스크 중단",
            row = 0,
            custom_id = "AbortButton"
        )

    async def callback( self, interaction: discord.Interaction ):
        await interaction.response.defer( ephemeral = True, thinking = True )

        if interaction.message is None:
            raise Exception( "No Message" )
        
        view = ConfirmView( interaction.message, False )
        await interaction.followup.send( content = "태스크를 중단하시겠습니까?", view = view )


class ConfirmView( discord.ui.View ):
    """
    :param confirm: 확인 버튼을 눌렀을 때 실행될 함수
    :param cancel: 취소 버튼을 눌렀을 때 실행될 함수
    """
    def __init__( self, interactionMessage: discord.Message, isFinish ):
        super().__init__( timeout = None )
        self.interactionMessage = interactionMessage
        self.task = Task.fromEmbed( interactionMessage.embeds[ 0 ] )

        if isFinish:
            self.add_item( ConfirmButton( self.confirmFinish ) )
        else:
            self.add_item( ConfirmButton( self.confirmAbort ) )

        # self.add_item( CancelButton( cancel ) )

    async def confirmFinish( self, i: discord.Interaction ):
        await i.response.defer( ephemeral = True, thinking = True )

        if self.task is None:
            await i.followup.send( "태스크를 찾지 못했습니다. 무언가 잘못되었군요." )
            return

        result = self.task.pop()
        if result is False:
            await i.followup.send( "태스크를 찾지 못했습니다. 무언가 잘못되었군요." )
            return

        result.record()
        
        # ===== 원본 메시지 수정 =====
        embed = TaskEmbed( result, i.client.info )  # type: ignore

        await self.interactionMessage.edit( embed = embed, view = None )  # type: ignore
        # ============================

        await updateTimeline( i.client ) # type: ignore
        await i.followup.send( "태스크가 완료되었습니다." )

    async def confirmAbort( self, i: discord.Interaction ):
        await i.response.defer( ephemeral = True, thinking = True )

        if self.task is None:
            await i.followup.send( "태스크를 찾지 못했습니다. 무언가 잘못되었군요." )
            return
        
        result = self.task.pop()
        if result is False:
            await i.followup.send( "태스크를 찾지 못했습니다. 무언가 잘못되었군요." )
            return

        # ===== 원본 메시지 수정 =====
        embed = self.interactionMessage.embeds[0]   # type: ignore
        editTaskEmbedAborted( embed )

        await self.interactionMessage.edit( embed = embed, view = None )  # type: ignore
        # ============================

        await i.followup.send( "태스크가 성공적으로 중단되었습니다." )

        # async def cancel( i: discord.Interaction ):
        #     await i.response.defer()
        #     await i.response.delete()    # type: ignore


class ConfirmButton( discord.ui.Button ):
    def __init__( self, confirm ):
        super().__init__(
            style = discord.ButtonStyle.primary,
            label = "확정"
        )
        self.confirm = confirm


    async def callback( self, interaction: discord.Interaction ):
        await self.confirm( interaction )


# class CancelButton( discord.ui.Button ):
#     def __init__( self, cancel ):
#         super().__init__(
#             style = discord.ButtonStyle.secondary,
#             label = "취소"
#         )
#         self.cancel = cancel


#     async def callback( self, interaction: discord.Interaction ):
#         await self.cancel( interaction )