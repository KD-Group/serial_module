import random
import time

import common
from serial_mod import base


class KDYMockSerial(base.MockSerial):
    current_level = None
    sleep_time = 0.01
    is_forward_current = True

    def respond(self, input: str) -> str:
        time.sleep(self.sleep_time)
        # print("request: " + input)
        # 查询版本号
        if input == "0xF5 0x02 0xff 0x1c":
            return "0xFa 0x09 0xff 0x32 0x32 0x32 0x31 0x36 0x36 0x36 0xee"

        if not self.check_crc8(input) or not self.check_len(input):
            time.sleep(self.timeout * 1.2)

        data_list = input.split()
        # 设定当前测量档位,探头默认压下:
        # 上位机请求格式: F5 03 C1 [电流档位: 00:0.001mA | 01:0.01mA | 02:0.1mA | 03:1mA | 04:10mA | 05:100mA] [crc8]
        # 单片机返回格式: FA 04 1C [电流档位] [探头是否压下: 是:01 | 否:00] [crc8]
        if data_list[2] == common.to_hex_str("C1"):
            self.current_level = data_list[3]
            return common.append_crc8(common.to_hex_str("FA 04 1C " + self.current_level + " 01"))

        # 读取当前显示数值（不等待）:
        # 上位机请求格式: F5 03 A1 [01:电压 | 02: 电流] [crc8]
        # 单片机返回格式: FA 07 1A [电流档位] ["设备: 电压:01 | 电流表:02] [data1] [data2] [data3] [crc8]
        # exa: Data1, data2, data3表示当前显示的数值， 00 10 10表示10.1
        # print(self.current_level)
        if data_list[2] == common.to_hex_str("A1") and self.current_level is not None:
            if data_list[3] == common.to_hex_str("01"):
                # 设置正反向电压偏差过大
                # if self.is_forward_current:
                #     return common.append_crc8(
                #         common.to_hex_str("FA 07 1A " + self.current_level + " " + data_list[3] + " 00 00 " + "33"))
                # else:
                #     return common.append_crc8(
                #         common.to_hex_str("FA 07 1A " + self.current_level + " " + data_list[3] + " 00 00 " + "99"))

                v = random.randint(46, 49)
                return common.append_crc8(
                    common.to_hex_str("FA 07 1A " + self.current_level + " " + data_list[3] + " 00 00 " + str(v)))

            if data_list[3] == common.to_hex_str("02"):
                return common.append_crc8(
                    common.to_hex_str("FA 07 1A " + self.current_level + " " + data_list[3] + " 00 02 22"))

        # 设置电压正反向控制:
        # 上位机请求格式: F5 03 a2 [正反向: 正向:00|反向:01] [crc8]
        # 单片机返回格式: FA 03 2A [正反向: 正向:00|反向:01] [crc8]
        if data_list[2] == common.to_hex_str("A2"):
            if data_list[3] == common.to_hex_str("00"):
                self.is_forward_current = True
            else:
                self.is_forward_current = False
            return common.append_crc8(
                common.to_hex_str("FA 03 2A " + data_list[3]))

        time.sleep(self.timeout * 1.2)

    def check_crc8(self, data: str) -> bool:
        expected_value = data[-4:]
        data = data[:-4]
        return common.calculate_crc8(data) == expected_value

    def check_len(self, data: str) -> bool:
        data_list = data.split()

        if common.hex_str_to_int(data_list[1]) != len(data_list) - 2:
            return False
        else:
            return True
