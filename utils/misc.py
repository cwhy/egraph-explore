def get_rounded_num(num: int) -> str:
    if num == 0:
        return chr(0x24EA) + " "
    elif num <= 20:
        return chr(0x245f + num) + " "
    elif num <= 35:
        return chr(0x323C + num) + " "
    elif num <= 50:
        return chr(0x328D + num) + " "
    else:
        return f"({num})"
