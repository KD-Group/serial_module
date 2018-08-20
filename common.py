import crcmod
from func_timeout import exceptions, func_timeout

import exception


def calculate_crc8(data) -> str:
    data = to_hex_str(data)
    data = data.replace("0x", "")
    crc8 = crcmod.predefined.Crc('crc-8-maxim')

    crc8.update(bytes().fromhex(data))

    calculate_value = str(hex(crc8.crcValue))
    if calculate_value == "0x0":
        calculate_value = "00"
    else:
        calculate_value = calculate_value[-2:]

    return to_hex_str(calculate_value)


def to_hex_str(string: str):
    """from common string convert to hexadecimal string

    example:
        to_hex_str("f5 0xf5") -> "0xf5 0xf5"
        to_hex_str("") -> ""
        to_hex_str("ff 0") -> "0xff 0x00"
    """

    hex_list = string.split(" ")
    target_list = []
    for hex_str in hex_list:
        if hex_str == "":
            continue
        if len(hex_str) != 2 and len(hex_str) != 4:
            raise Exception("hex string is error : " + hex_str + " \n example: f5 0xf5")
        if len(hex_str) == 2:
            hex_str = "0x" + hex_str
        target_list.append(hex_str)
    target_str = ""
    for hex_str in target_list:
        target_str += hex_str + " "
    target_str = target_str[:-1]
    return target_str


def hex_str_to_int(hex_str: str) -> int:
    hex_str = hex_str.replace("0x", "")
    return int(hex_str)


def append_crc8(data: str) -> str:
    return to_hex_str(data) + " " + calculate_crc8(data)


def exec_with_timeout(timeout, func, *args, **kwargs):
    try:
        return func_timeout(timeout, func, args, kwargs)
    except exceptions.FunctionTimedOut as e:
        raise exception.TimeoutException("run " + func.__name__ + "() timeout: " + str(timeout) + "s")
