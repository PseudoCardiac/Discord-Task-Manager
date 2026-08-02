import datetime, json
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import AutoMinorLocator


def genChart( dt: datetime.datetime | None = None ):
    # 날짜 설정
    if dt is None:
        date = datetime.datetime.now( tz = ZoneInfo( "Asia/Seoul" ) ).strftime( "%Y%m%d" )
    else:
        date = dt.strftime( "%Y%m%d" )


    # 한글 폰트 설정
    plt.rcParams[ "font.family" ] = "NanumBarunGothic"
    plt.rcParams[ "axes.unicode_minus" ] = False


    # ==================== 기록 불러오기 ====================

    with open( "data/today.json", "r", encoding = "UTF-8" ) as f:
        today: dict[ str, list[ dict[ str, str ] ] ] = json.load( f )

    tasksDict = today.get( date )
    taskIndices: list[ str ] = []
    taskNames: list[ str ] = []
    taskDescs: list[ str ] = []
    startTimes: list[ datetime.datetime ] = []
    endTimes: list[ datetime.datetime ] = []
    durations: list[ datetime.timedelta ] = []
    colors: list[ str ] = []

    colorsDict = {
        "0": "#c72323A0",
        "1": "#ff8d2aA0",
        "2": "#ffec36A0",
        "3": "#96cc2eA0",
        "4": "#8aefffA0",
        "5": "#e1b6ffA0",
        "6": "#ff59a1A0",
        "7": "#7494a5A0",
        "8": "#898989A0"
    }

    for task in tasksDict if tasksDict is not None else []:
        taskIndices.append( task[ "id" ] )
        taskNames.append( task[ "name" ] )
        taskDescs.append( task[ "desc" ] )
        colors.append( colorsDict[ task[ "category" ] ] )
        startTime = datetime.datetime.strptime( task[ "start" ], "%Y/%m/%d %H:%M:%S %z" )
        endTime = datetime.datetime.strptime( task[ "end" ], "%Y/%m/%d %H:%M:%S %z" )
        startTimes.append( startTime )
        endTimes.append( endTime )
        durations.append( endTime - startTime )

    # =======================================================

    # 플롯 정의
    fig, ax = plt.subplots( figsize = ( 16, max( len( taskIndices ) / 1.5, 3) ), facecolor="#3E3E42")
    ax.set_facecolor("#3E3E42")

    # x축을 날짜로 정의
    ax.xaxis_date()

    # x축 범위 정의
    ax.set_xlim( left = datetime.datetime.now( tz = ZoneInfo( "Asia/Seoul" ) ).replace( hour = 0, minute = 0, second = 0, microsecond = 0 ), # type: ignore
                right = ( datetime.datetime.now( tz = ZoneInfo( "Asia/Seoul" ) ) + datetime.timedelta( days = 1 ) ).replace( hour = 0, minute = 1, second = 0, microsecond = 0 ) ) # type: ignore

    # 막대 그리기
    ax.barh( y = taskIndices, width = durations, left = startTimes, height = 0.8, color = colors ) # type: ignore

    # 그리드 그리기
    ax.grid( axis = "x", which = "major" )
    ax.grid( axis = "x", which = "minor", ls = ":" )

    # 눈금 그리기
    ax.xaxis.set_major_formatter( DateFormatter( "%H시", tz = ZoneInfo( "Asia/Seoul" ) ) )
    ax.xaxis.set_minor_locator( AutoMinorLocator( 3 ) )
    plt.tick_params( colors = "#ffffff" )

    # 테두리 숨기기
    ax.spines[ "top" ].set_visible( False )
    ax.spines[ "left" ].set_visible( False )
    ax.spines[ "right" ].set_visible( False )
    ax.spines[ "bottom" ].set_visible( False )

    # y축 숨기기
    ax.get_yaxis().set_visible( False )

    # 막대 위에 태스크 이름 그리기
    for i in range( len( taskIndices ) ):
        ax.text( startTimes[i], i, f"  {taskNames[i]}", ha = "left", va = "center", color = "white", fontsize = 14, fontweight = "bold" ) # type: ignore
        ax.text( startTimes[i], i + 0.3, f"  {taskDescs[i]}", ha = "left", va = "center", color = "white", fontsize = 12, fontweight = "light" ) # type: ignore

    # 수직 정렬 뒤집기
    plt.gca().invert_yaxis()

    # 플롯 그리기
    plt.savefig( "tt.png" )


if __name__ == "__main__":
    genChart()