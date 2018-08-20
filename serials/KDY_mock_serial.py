import time

import base
import common


class KDYMockSerial(base.MockSerial):
    current_level = None

    def respond(self, input: str) -> str:
        print("request: " + input)
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
        print(self.current_level)
        if data_list[2] == common.to_hex_str("A1") and self.current_level is not None:
            return common.append_crc8(
                common.to_hex_str("FA 07 1A " + self.current_level + " " + data_list[3] + " 11 11 11"))
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
