import discord, json, datetime, re
from zoneinfo import ZoneInfo
from discord.ext.commands import Cog
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import Faust
from objects import Task, Category, TaskEmbed, TaskEmbedView
from .timer import setTimer
from utils import minutesToHours, updateTimeline, getTodaysTasks, editFinishedTask, editTaskEmbedFinished, editTaskEmbedAborted, deleteTaskFromToday


class TaskManagementCog( Cog ):
    def __init__( self, bot: "Faust" ):
        self.bot = bot

    @discord.app_commands.command( name = "태스크_등록", description = "새로운 태스크를 등록합니다." )
    @discord.app_commands.rename( name = "제목" )
    @discord.app_commands.rename( desc = "세부사항" )
    @discord.app_commands.rename( category = "카테고리" )
    @discord.app_commands.rename( min = "다시_알림_시간_분" )
    async def registerTask( self, i: discord.Interaction, name: str, category: discord.Role, desc: str = "", min: int = 0 ):
        await i.response.defer( ephemeral = True, thinking = True )

        try:
            categoryObj = Category( self.bot.info.tag.index( category ) )
        except ValueError:
            await i.followup.send( "…파우스트는 카테고리가 아닙니다." )
            return
        
        task = Task(
            name = name,
            category = categoryObj,
            desc = desc
        )

        embed = TaskEmbed( task, self.bot.info )
        msg = await self.bot.info.channel_log.send( embed = embed, view = TaskEmbedView( embed ) )
        await i.followup.send( "태스크가 등록되었습니다." )
            
        task.msgID = msg.id
        task.push()

        if min:
            await setTimer( min, task, i.client )   # type: ignore


    @discord.app_commands.command( name = "태스크_완료", description = "진행 중인 태스크를 전부 완료 처리합니다." )
    async def finishTask( self, i: discord.Interaction ):
        await i.response.defer( ephemeral = True, thinking = True )

        with open( "data/current_tasks.json", 'r', encoding = "UTF-8" ) as f:
            currentTasks: list[ dict[ str, str ] ] = json.load( f )

        for currentTask in currentTasks:
            task = Task.toTaskObj( currentTask )
            task.record()

            if task.msgID is None:
                continue

            try:
                msg = await self.bot.info.channel_log.fetch_message( task.msgID )
                embed = msg.embeds[ 0 ]
                editTaskEmbedFinished( embed, task )
                await msg.edit( embed = embed, view = None )
            except discord.errors.NotFound:
                continue

        with open( "data/current_tasks.json", 'w+', encoding = "UTF-8" ) as f:
            json.dump( [], f )

        await updateTimeline( i.client ) # type: ignore
        await i.followup.send( "진행 중인 태스크가 전부 완료 처리되었습니다." )


    @discord.app_commands.command( name = "태스크_중단", description = "진행 중인 태스크를 전부 중단 처리합니다." )
    async def abortTask( self, i: discord.Interaction ):
        await i.response.defer( ephemeral = True, thinking = True )

        with open( "data/current_tasks.json", 'r', encoding = "UTF-8" ) as f:
            currentTasks: list[ dict[ str, str ] ] = json.load( f )

        for currentTask in currentTasks:
            task = Task.toTaskObj( currentTask )

            if task.msgID is None:
                continue

            try:
                msg = await self.bot.info.channel_log.fetch_message( task.msgID )
                embed = msg.embeds[ 0 ]

                editTaskEmbedAborted( embed )
                await msg.edit( embed = embed, view = None )
            except discord.errors.NotFound:
                continue

        with open( "data/current_tasks.json", 'w+', encoding = "UTF-8" ) as f:
            json.dump( [], f )

        await i.followup.send( "진행 중인 태스크가 전부 중단 처리되었습니다." )


    @discord.app_commands.rename( name = "제목" )
    @discord.app_commands.rename( desc = "세부사항" )
    @discord.app_commands.rename( category = "카테고리" )
    @discord.app_commands.rename( start = "시작_시간_6자리" )
    @discord.app_commands.rename( end = "종료_시간_6자리" )
    @discord.app_commands.command( name = "태스크_기록", description = "완료된 태스크를 등록합니다." )
    async def recordTask( self, i: discord.Interaction, name: str, category: discord.Role, start: str, end: str | None = None, desc: str = "" ):
        await i.response.defer( ephemeral = True, thinking = True )
        
        try:
            categoryObj = Category( self.bot.info.tag.index( category ) )
        except ValueError:
            await i.followup.send( "…파우스트는 카테고리가 아닙니다." )
            return

        try:
            tz = ZoneInfo( "Asia/Seoul" )
            today = datetime.datetime.now( tz = tz ).date()
            startTime = datetime.datetime.strptime( start, "%H%M%S" ).time()
            startDateTime = datetime.datetime.combine( today, startTime, tz )
            if end is None:
                endTime = datetime.datetime.now( tz = tz ).time()
            else:
                endTime = datetime.datetime.strptime( end, "%H%M%S" ).time()
            endDateTime = datetime.datetime.combine( today, endTime, tz )
        except ValueError:
            await i.followup.send( "시간 형식이 잘못되었습니다." )
            return

        task = Task(
            name = name,
            category = categoryObj,
            desc = desc,
            start = startDateTime,
            end = endDateTime
        )

        minutes = round( ( endDateTime - startDateTime ).total_seconds() ) // 60
        durationString = minutesToHours( minutes )

        embed = TaskEmbed( task, self.bot.info )
        embed.description = re.sub( r"<t:\d+:R> 시작", f"{ durationString }동안 진행", str( embed.description ) )

        msg = await self.bot.info.channel_log.send( embed = embed )
        task.msgID = msg.id

        task.record( False )

        await updateTimeline( i.client )   # type: ignore

        await i.followup.send( "태스크가 기록되었습니다." )


    @discord.app_commands.command( name = "태스크_수정", description = "완료된 태스크를 수정합니다." )
    async def editTask( self, i: discord.Interaction ):
        await i.response.defer( ephemeral = True, thinking = True )

        if not getTodaysTasks():
            await i.followup.send( "현재 수정 가능한 태스크가 없습니다." )
        else:
            await i.followup.send( view = TaskEditView() )


class TaskEditView( discord.ui.View ):
    def __init__( self ):
        super().__init__( timeout = None )
        self.add_item( TaskEditSelect() )


class TaskEditSelect( discord.ui.Select ):
    def __init__( self ):
        todaysTasks = getTodaysTasks()

        super().__init__(
            options = [
                discord.SelectOption( label = task.name,
                                      description = task.desc,
                                      value = task.ID )
                for task in todaysTasks
            ]
        )

    async def callback( self, interaction: discord.Interaction ):
        self.disabled = True

        task = Task.get( self.values[0] )
        if task is False:
            await interaction.response.send_message( "태스크를 찾지 못했습니다. 무언가 잘못되었군요." )
            return

        await interaction.response.send_modal( TaskEditModal( task ) )


class CategoryRadioGroup( discord.ui.RadioGroup ):
    def __init__( self, task: Task ):
        super().__init__(
            options = [
                discord.RadioGroupOption( label = "대학", value = '0', default = task.category == 0 ),
                discord.RadioGroupOption( label = "생활", value = '1', default = task.category == 1 ),
                discord.RadioGroupOption( label = "운동", value = '2', default = task.category == 2 ),
                discord.RadioGroupOption( label = "휴식", value = '3', default = task.category == 3 ),
                discord.RadioGroupOption( label = "공부", value = '4', default = task.category == 4 ),
                discord.RadioGroupOption( label = "작업", value = '5', default = task.category == 5 ),
                discord.RadioGroupOption( label = "게임", value = '6', default = task.category == 6 ),
                discord.RadioGroupOption( label = "수면", value = '7', default = task.category == 7 ),
                discord.RadioGroupOption( label = "기타", value = '8', default = task.category == 8 ),
                discord.RadioGroupOption( label = "태스크 삭제하기", value = '9' ),
            ],
            required = False
        )


class TaskEditModal( discord.ui.Modal ):
    def __init__( self, task: Task ):
        super().__init__(
            title = "태스크 수정",
            timeout = None
        )
        self.task = task

        self.name = discord.ui.TextInput( label = "제목", style = discord.TextStyle.short, required = False, placeholder = self.task.name )
        self.desc = discord.ui.TextInput( label = "세부 사항", style = discord.TextStyle.short, required = False, placeholder = self.task.desc )
        self.category = discord.ui.Label(
            text = "카테고리",
            component = CategoryRadioGroup( self.task )
            # component = discord.ui.RoleSelect()
        )
        self.start = discord.ui.TextInput( label = "시작 시간 (6자리)", style = discord.TextStyle.short, required = False,
                                           placeholder = self.task.start.strftime( "%H%M%S" ) )
        self.end = discord.ui.TextInput( label = "종료 시간 (6자리)", style = discord.TextStyle.short, required = False,
                                         placeholder = self.task.end.strftime( "%H%M%S" ) ) # type: ignore

        self.add_item( self.name )
        self.add_item( self.desc )
        self.add_item( self.category )
        self.add_item( self.start )
        self.add_item( self.end )


    async def on_submit( self, i: discord.Interaction ):
        await i.response.defer( ephemeral = True, thinking = True )

        if self.category.component.value == '9':   # type: ignore
            deleteTaskFromToday( self.task )
            await updateTimeline( i.client )    # type: ignore
            await i.followup.send( "태스크가 삭제되었습니다." )

        else:
            editedTask = editFinishedTask( self.task, self.name.value, self.desc.value, self.category.component.value, self.start.value, self.end.value ) # type: ignore

            msgID = editedTask.msgID  # type: ignore
            if msgID is None:
                # raise Exception( "수정할 태스크의 메시지 ID 정보가 없음" )
                await updateTimeline( i.client )    # type: ignore
                await i.followup.send( "태스크는 성공적으로 수정되었으나, 태스크 임베드 편집에는 실패했습니다." )
                return

            try:
                msg = await i.client.info.channel_log.fetch_message( msgID )    # type: ignore
                await msg.edit( embed = TaskEmbed( editedTask, i.client.info ) )      # type: ignore
            except discord.errors.NotFound:
                pass

            await updateTimeline( i.client )    # type: ignore
            await i.followup.send( "태스크가 성공적으로 수정되었습니다." )