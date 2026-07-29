import discord, re
from datetime import datetime
from objects import Info, Category
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from objects import Task
from utils import minutesToHours, updateTimetable


weekdays = [ '월', '화', '수', '목', '금', '토', '일' ]


class TaskEmbed( discord.Embed ):
    def __init__( self, task: "Task", info: Info ):
        super().__init__(
            title = task.name,
            description = f"{ task.desc }\n<@&{ info.tag[ task.category ].id }> · <t:{ round( task.start.timestamp() ) }:R> 시작",
            color = info.tagColor[ task.category ]
        )
        self.task = task
        self.set_footer( text = f"{ task.start.year }년 { task.start.month }월 { task.start.day }일 { weekdays[ task.start.weekday() ] }요일 #{ task.number }" )


class TaskEmbedView( discord.ui.View ):
    def __init__( self, parentEmbed: TaskEmbed ):
        super().__init__( timeout = None )
        self.add_item( FinishButton( parentEmbed ) )
        self.add_item( TextEditButton( parentEmbed ) )
        self.add_item( CategoryEditButton( parentEmbed ) )
        self.add_item( AbortButton( parentEmbed ) )


class FinishButton( discord.ui.Button ):
    def __init__( self, parentEmbed: TaskEmbed ):
        super().__init__(
            style = discord.ButtonStyle.primary,
            label = "태스크 완료"
        )
        self.parentEmbed = parentEmbed

    async def callback( self, interaction: discord.Interaction ):
        async def confirm( i: discord.Interaction ):
            result = self.parentEmbed.task.pop()
            if result is False:
                await interaction.response.send_message( "태스크를 찾지 못함", ephemeral = True, delete_after = 10 )
                return

            # ===== 원본 메시지 수정 =====
            minutes = round( ( datetime.now() - result.start ).total_seconds() ) // 60
            durationString = minutesToHours( minutes )
            embed = interaction.message.embeds[0]   # type: ignore
            embed.description = re.sub( r"<t:\d+:R> 시작", f"{ durationString }동안 작업", str( embed.description ) )

            for item in self.view.children: # type: ignore
                item.disabled = True

            await interaction.message.edit( embed = embed, view = self.view )  # type: ignore
            # ============================

            result.record()
            await updateTimetable( interaction.client ) # type: ignore
            await i.response.send_message( "태스크 완료됨", ephemeral = True, delete_after = 10 )

        async def cancel( i: discord.Interaction ):
            await i.response.defer()
            await i.message.delete()    # type: ignore

        await interaction.response.send_message( view = ConfirmView( confirm, cancel ), ephemeral = True, delete_after = 10 )


class TextEditButton( discord.ui.Button ):
    def __init__( self, parentEmbed: TaskEmbed ):
        super().__init__(
            style = discord.ButtonStyle.secondary,
            label = "제목 · 세부 사항 수정"
        )
        self.parentEmbed = parentEmbed


    async def callback( self, interaction: discord.Interaction ):
        await interaction.response.send_modal( TextEditModal( self ) )


class TextEditModal( discord.ui.Modal ):
    def __init__( self, button: TextEditButton ):
        super().__init__(
            title = "태스크 제목 · 세부 사항 수정",
            timeout = None
        )
        self.button = button

    name = discord.ui.TextInput( label = "태스크 제목", style = discord.TextStyle.short, required = False )
    desc = discord.ui.TextInput( label = "태스크 세부 사항", style = discord.TextStyle.short, required = False )


    async def on_submit( self, i: discord.Interaction ):
        if not self.name and not self.desc:
            await i.response.send_message( "태스크가 수정되지 않았습니다.", ephemeral = True, delete_after = 10 )
        else:
            self.button.parentEmbed.task.edit( name = self.name.value, desc = self.desc.value )
            await i.message.edit( embed = TaskEmbed( self.button.parentEmbed.task, i.client.info ) )    # type: ignore
            await i.response.send_message( "태스크가 수정되었습니다.", ephemeral = True, delete_after = 10 )


class CategoryEditButton( discord.ui.Button ):
    def __init__( self, parentEmbed: TaskEmbed ):
        super().__init__(
            style = discord.ButtonStyle.secondary,
            label = "카테고리 수정"
        )
        self.parentEmbed = parentEmbed


    async def callback( self, interaction: discord.Interaction ):
        await interaction.response.send_message( view = CategoryEditView( self, interaction.message ), ephemeral = True, delete_after = 10 ) # type: ignore


class CategoryEditView( discord.ui.View ):
    def __init__( self, button: CategoryEditButton, msg: discord.Message ):
        super().__init__( timeout = None )

        self.add_item( CategorySelect( button, msg ) )


class CategorySelect( discord.ui.RoleSelect ):
    def __init__( self, button: CategoryEditButton, msg: discord.Message ):
        super().__init__()
        self.button = button
        self.msg = msg


    async def callback( self, interaction: discord.Interaction ):
        category = self.values[0]

        if category not in interaction.client.info.tag: # type: ignore
            await interaction.response.send_message( "잘못된 카테고리입니다.", ephemeral = True, delete_after = 10 )
            return

        self.button.parentEmbed.task.edit( category = Category( interaction.client.info.tag.index( category ) ) )   # type: ignore
        await self.msg.edit( embed = TaskEmbed( self.button.parentEmbed.task, interaction.client.info ) )    # type: ignore
        await interaction.response.send_message( "태스크가 수정되었습니다.", ephemeral = True, delete_after = 10 )


class AbortButton( discord.ui.Button ):
    def __init__( self, parentEmbed: TaskEmbed ):
        super().__init__(
            style = discord.ButtonStyle.danger,
            label = "태스크 중단"
        )
        self.parentEmbed = parentEmbed

    async def callback( self, interaction: discord.Interaction ):
        async def confirm( i: discord.Interaction ):
            result = self.parentEmbed.task.pop()
            if result is False:
                await interaction.response.send_message( "태스크를 찾지 못함", ephemeral = True, delete_after = 10 )
                return

            # ===== 원본 메시지 수정 =====
            embed = interaction.message.embeds[0]   # type: ignore
            embed.title = "~~" + str( embed.title ) + "~~"
            embed.description = "~~" + str( embed.description ) + "~~"

            for item in self.view.children: # type: ignore
                item.disabled = True

            await interaction.message.edit( embed = embed, view = self.view )  # type: ignore
            # ============================

            await i.response.send_message( "태스크 중단됨", ephemeral = True, delete_after = 10 )

        async def cancel( i: discord.Interaction ):
            await i.response.defer()
            await i.message.delete()    # type: ignore

        await interaction.response.send_message( view = ConfirmView( confirm, cancel ), ephemeral = True, delete_after = 10 )


class ConfirmView( discord.ui.View ):
    """
    :param confirm: 확인 버튼을 눌렀을 때 실행될 함수
    :param cancel: 취소 버튼을 눌렀을 때 실행될 함수
    """
    def __init__( self, confirm, cancel ):
        super().__init__( timeout = None )

        self.add_item( ConfirmButton( confirm ) )
        self.add_item( CancelButton( cancel ) )


class ConfirmButton( discord.ui.Button ):
    def __init__( self, confirm ):
        super().__init__(
            style = discord.ButtonStyle.primary,
            label = "확인"
        )
        self.confirm = confirm


    async def callback( self, interaction: discord.Interaction ):
        await self.confirm( interaction )


class CancelButton( discord.ui.Button ):
    def __init__( self, cancel ):
        super().__init__(
            style = discord.ButtonStyle.secondary,
            label = "취소"
        )
        self.cancel = cancel


    async def callback( self, interaction: discord.Interaction ):
        await self.cancel( interaction )