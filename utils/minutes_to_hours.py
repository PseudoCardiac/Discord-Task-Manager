def minutesToHours( m: int ):
    if m < 60:
        return f"{ m }분"

    h = m // 60
    m %= 60

    if m == 0:
        return f"{ h }시간"
    else:
        return f"{ h }시간 { m }분"