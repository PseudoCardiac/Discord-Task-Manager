import datetime, json
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import AutoMinorLocator


# 한글 폰트 설정
plt.rcParams[ "font.family" ] = "NanumBarunGothic"
plt.rcParams[ "axes.unicode_minus" ] = False


# ==================== 기록 불러오기 ====================

with open( "data/today.json", "r", encoding = "UTF-8" ) as f:
    today: dict[ str, list[ dict[ str, str ] ] ] = json.load( f )


date = "20260726"
tasksDict = today[ date ]
taskIndices: list[ str ] = []
taskNames: list[ str ] = []
taskDescs: list[ str ] = []
startTimes: list[ datetime.datetime ] = []
endTimes: list[ datetime.datetime ] = []
durations: list[ datetime.timedelta ] = []
colors: list[ str ] = []

colorsDict = {
    "1": "#c72323A0",
    "2": "#ff8d2aA0",
    "3": "#ffec36A0",
    "4": "#96cc2eA0",
    "5": "#8aefffA0",
    "6": "#e1b6ffA0",
    "7": "#ff59a1A0",
    "8": "#7494a5A0",
    "9": "#898989A0"
}

for task in tasksDict:
    taskIndices.append( task[ "number" ] )
    taskNames.append( task[ "name" ] )
    taskDescs.append( task[ "desc" ] )
    colors.append( colorsDict[ task[ "category" ] ] )
    startTime = datetime.datetime.strptime( task[ "start" ], "%d/%m/%Y, %H:%M:%S" )
    endTime = datetime.datetime.strptime( task[ "end" ], "%d/%m/%Y, %H:%M:%S" )
    startTimes.append( startTime )
    endTimes.append( endTime )
    durations.append( endTime - startTime )

# =======================================================

# 플롯 정의
fig, ax = plt.subplots( figsize = ( 16, len( taskIndices ) / 1.5 ), facecolor="#3E3E42")
ax.set_facecolor("#3E3E42")

# x축을 날짜로 정의
ax.xaxis_date()

# x축 범위 정의
ax.set_xlim( left = startTimes[0].replace( hour = 0, minute = 0, second = 0, microsecond = 0 ), # type: ignore
             right = ( startTimes[0] + datetime.timedelta( days = 1 )).replace( hour = 0, minute = 1, second = 0, microsecond = 0 ) ) # type: ignore

# 막대 그리기
ax.barh( y = taskIndices, width = durations, left = startTimes, height = 0.8, color = colors ) # type: ignore

# 그리드 그리기
ax.grid( axis = "x", which = "major" )
ax.grid( axis = "x", which = "minor", ls = ":" )

# 눈금 그리기
ax.xaxis.set_major_formatter( DateFormatter( "%H시" ) )
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
    ax.text( startTimes[i], i + 0.4, f"  {taskDescs[i]}", ha = "left", va = "center", color = "white", fontsize = 12, fontweight = "light" ) # type: ignore

# 수직 정렬 뒤집기
plt.gca().invert_yaxis()

# 플롯 그리기
plt.show()