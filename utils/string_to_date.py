import re
from datetime import datetime


def stringToDate( string: str ):
    """
    `YYYY년 MM월 DD일` 형식의 문자열을 날짜 오브젝트로 변환한다.
    """
    match = re.search( r"(\d{4})년 (\d{1,2})월 (\d{1,2})일", string )

    if match:
        year, month, day = map( int, match.groups() )
        return datetime( year, month, day ).date()

    return False