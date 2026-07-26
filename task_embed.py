import discord, re
from datetime import datetime
from info import Info
from task import Task
from minutes_to_hours import minutesToHours


weekdays = [ '월', '화', '수', '목', '금', '토', '일' ]


class TaskEmbed( discord.Embed ):
    def __init__( self, task: Task, info: Info ):
        super().__init__(
            title = task.name,
            description = f"{ task.desc }\n<@&{ info.tag[ task.category ].id }> · <t:{ round( task.start.timestamp() ) }:R> 시작",
            color = info.tagColor[ task.category ]
        )
        self.task = task
        self.set_footer( text = f"{ task.start.year }년 { task.start.month }월 { task.start.day }일 { weekdays[ task.start.weekday() ] }요일 #{ task.number }" )


class TaskEmbedView( discord.ui.View ):
    def __init__( self, parentEmbed: discord.Embed ):
        super().__init__( timeout = None )
        self.add_item( FinishButton( parentEmbed ) )
        self.add_item( AbortButton( parentEmbed ) )


class FinishButton( discord.ui.Button ):
    def __init__( self, parentEmbed: discord.Embed ):
        super().__init__(
            style = discord.ButtonStyle.primary,
            label = "태스크 완료"
        )
        self.parentEmbed = parentEmbed

    async def callback( self, interaction: discord.Interaction ):
        result = Task.pop()
        if result is False:
            await interaction.response.send_message( "태스크를 찾지 못함" )
            return

        minutes = round( ( datetime.now() - result.start ).total_seconds() ) // 60
        durationString = minutesToHours( minutes )
        embed = interaction.message.embeds[0]   # type: ignore
        embed.description = re.sub( r"<t:\d+:R> 시작", f"{ durationString }동안 작업", str( embed.description ) )
        await interaction.message.edit( embed = embed ) # type: ignore

        result.record()
        await interaction.response.send_message( "태스크 완료됨" )


class AbortButton( discord.ui.Button ):
    def __init__( self, parentEmbed: discord.Embed ):
        super().__init__(
            style = discord.ButtonStyle.danger,
            label = "태스크 중단"
        )
        self.parentEmbed = parentEmbed

    async def callback( self, interaction: discord.Interaction ):
        result = Task.pop()
        if result is False:
            await interaction.response.send_message( "태스크를 찾지 못함" )
            return

        embed = interaction.message.embeds[0]   # type: ignore
        embed.title = "~~" + str( embed.title ) + "~~"
        embed.description = "~~" + str( embed.description ) + "~~"
        await interaction.message.edit( embed = embed ) # type: ignore

        await interaction.response.send_message( "태스크 중단됨" )