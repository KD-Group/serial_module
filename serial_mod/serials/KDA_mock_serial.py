import random
import time

from serial_mod import base
from serial_mod.data_type import HexStruct


class KDAMockSerial(base.MockSerial):
    current_level = None
    sleep_time = 0.01
    is_forward_current = True

    def __init__(self,timeout = 0 ):
        self.set_timeout(timeout)

    def respond(self, input: bytes) -> bytes:
        if self.debug:
            print("{")
            print("     request  : {} ==> {}".format(input, self.bytes_to_hex_str(input)))

        # time.sleep(self.sleep_time)
        # 查询版本号
        return_value = b''
        if input == b"\xF5\x02\xff\x1c":
            return_value = b"\xFa\x09\xff\x32\x32\x32\x31\x36\x36\x36\xee"

        hs = HexStruct(input)
        # if not hs.check_crc8():
        #     time.sleep(self.timeout * 1.2)

        data_list = hs.list
        # 设定当前测量档位,探头默认压下:
        # 上位机请求格式: F5 03 C1 [电流档位: 00:0.001mA | 01:0.01mA | 02:0.1mA | 03:1mA | 04:10mA | 05:100mA] [crc8]
        # 单片机返回格式: FA 04 1C [电流档位] [探头是否压下: 是:01 | 否:00] [crc8]
        if data_list[2] == int("c1", 16):
            self.current_level = data_list[3]
            return_value = HexStruct("FA 04 1C " + str(self.current_level) + " 01").append_crc8().to_bytes()

        # 读取当前显示数值（不等待）:
        # 上位机请求格式: F5 03 A1 [01:电压 | 02: 电流] [crc8]
        # 单片机返回格式: FA 07 1A [电流档位] ["设备: 电压:01 | 电流表:02] [data1] [data2] [data3] [crc8]
        # exa: Data1, data2, data3表示当前显示的数值， 00 10 10表示10.1
        # print(self.current_level)
        if data_list[2] == int("A1", 16) and self.current_level is not None:
            if data_list[3] == 1:
                # 设置正反向电压偏差过大
                # if self.is_forward_current:
                #     return_value = common.append_crc8(
                #         common.to_hex_str("FA 07 1A " + self.current_level + " " + data_list[3] + " 00 00 " + "33"))
                # else:
                #     return_value = common.append_crc8(
                #         common.to_hex_str("FA 07 1A " + self.current_level + " " + data_list[3] + " 00 00 " + "99"))

                v = random.randint(46, 49)
                return_value = HexStruct(
                    "FA 07 1A {} {} 00 {} {}".format(self.current_level, data_list[3], v,v)).append_crc8().to_bytes()

            if data_list[3] == 2:
                return_value = HexStruct(
                    ("FA 07 1A " + str(self.current_level) + " " + str(
                        data_list[3]) + " 00 02 22")).append_crc8().to_bytes()
                # return_value = common.append_crc8(
                #     common.to_hex_str("FA 07 1A " + self.current_level + " " + data_list[3] + " 00 02 22"))

        # 设置电压正反向控制:
        # 上位机请求格式: F5 03 a2 [正反向: 正向:00|反向:01] [crc8]
        # 单片机返回格式: FA 03 2A [正反向: 正向:00|反向:01] [crc8]
        if data_list[2] == int("A2", 16):
            if data_list[3] == 0:
                self.is_forward_current = True
            else:
                self.is_forward_current = False
            return_value = HexStruct("FA 03 2A cc").append_crc8().to_bytes()

        if self.debug:
            print("     respond  : {} ==> {}".format(return_value, self.bytes_to_hex_str(return_value)))
            print("}")
        return return_value

    def bytes_to_hex_str(self, data: bytes):
        """
        example:   b'\xf5\x03\xa2\x00k' --> 'f5 03 a2 00 6b'
        """
        byte_list = list(data)
        target_str = ' '.join(map(lambda x: hex(int(x)), byte_list))
        target_str = target_str.strip().replace("0x", "")
        target_list = target_str.split()
        for i in range(len(target_list)):
            if len(target_list[i]) == 1:
                target_list[i] = "0" + target_list[i]
        return ' '.join(target_list)
