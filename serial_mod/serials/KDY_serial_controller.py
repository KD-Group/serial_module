import common
from serial_mod import interface, exception
from serial_mod.serials import KDYMockSerial, KDYRealSerial


class Result():
    current_level = None  # 电流档位
    current_show = None  # 电流表显示数值
    voltage_show = None  # 电压表显示数值
    down = None


class KDYSerialController():
    serial = None
    respond_parse_func_point = None
    last_result = None
    current_level = None
    timeout = 0.5
    current = 1  # 默认电流
    voltage_direction = "00"  # 00 为正向, 01 为反向

    current_map = {
        0.001: "00",
        0.01: "01",
        0.1: "02",
        1: "03",
        10: "04",
        100: "05",
    }

    def __init__(self, mock=True):
        if mock:
            self.set_serial(KDYMockSerial())
        else:
            self.set_serial(KDYRealSerial())
        self.serial.set_timeout(self.timeout)

    def set_serial(self, serial: interface.SerialInterface):
        self.serial = serial

    def connect_serial(self):
        try:
            self.serial.connect_suitable_port()
        except Exception as e:
            raise exception.ConnectionException(str(e))

    # 上位机请求格式: F5 03 C1 [电流档位: 00:0.001mA | 01:0.01mA | 02:0.1mA | 03:1mA | 04:10mA | 05:100mA] [crc8]
    def send_set_current_request(self, current: float):
        assert self.current_map.__contains__(current)
        self.current = current
        converted_current = self.current_map[current]
        self.serial.send(common.append_crc8("F5 03 C1 " + converted_current))
        self.respond_parse_func_point = self.read_current_respond

    # 单片机返回格式: FA 04 1C [电流档位] [探头是否压下: 是:01 | 否:00] [crc8]
    def read_current_respond(self, data: str) -> Result:
        # todo: exception: timeout parse_exception
        result = Result()
        data_list = data.split()
        for k, v in self.current_map.items():
            if common.to_hex_str(v) == data_list[3]:
                result.current_level = k
                self.current_level = common.to_hex_str(v)
                break
        if result.current_level is None:
            raise exception.RespondParseException(
                "解析单片机对设定当前测量档位的返回消息错误: 第4位字节[" + data_list[3] + "]不是电流档位指令")

        if result.current_level != self.current:
            raise exception.RespondParseException(
                "解析单片机对设定当前测量档位的返回消息错误: 第4位字节[" + data_list[3] + "(" + str(result.current_level)
                + ")]不是之前设定的电流档位指令[" + self.current_map[self.current] + "(" + str(self.current) + ")]"
            )

        if data_list[4] == "0x01":
            result.down = True
        elif data_list[4] == "0x00":
            result.down = False
        else:
            raise exception.RespondParseException(
                "解析单片机对设定当前测量档位的返回消息错误: 第4位字节[" + data_list[4] + "]不是探头压下指令")
        return result

    def is_pressed(self) -> bool:
        # if self.current is None:
        #     raise exception.NotSetCurrentException("在测试探头是否压下前须先设置电流档位")
        self.send_set_current_request(self.current)
        res = self.read()
        return res.down

    # 读取当前显示数值（不等待）:
    # 上位机请求格式: F5 03 A1 [01:电压 | 02: 电流] [crc8]
    def send_show_current_request(self):
        self.serial.send(common.append_crc8("F5 03 A1 02"))
        self.respond_parse_func_point = self.read_show_current_respond

    # 读取当前显示数值（不等待）:
    # 单片机返回格式: FA 07 1A [电流档位] ["设备: 电压:01 | 电流表:02] [data1] [data2] [data3] [crc8]
    def read_show_current_respond(self, data: str):
        result = Result()
        data_list = data.split()
        if data_list[2] != common.to_hex_str("1A"):
            raise exception.RespondParseException(
                "解析单片机对获取当前电流的返回消息错误: 第2位字节[" + data_list[2] + "]不是功能指令[0x1A]")

        if data_list[3] != self.current_level:
            raise exception.RespondParseException(
                "解析单片机对获取当前电流的返回消息错误: 第3位字节电流档位[" + data_list[3] + "]不是之前设置的电流档位[" + self.current_level + "]")
        result.current_level = self.get_key_by_value(data_list[3])

        if data_list[4] != common.to_hex_str("02"):
            raise exception.RespondParseException(
                "解析单片机对获取当前电流的返回消息错误: 第4位字节[" + data_list[2] + "]不是电压表指令('02')")
        current_show_number = 0
        current_show_number += common.hex_str_to_int(data_list[5]) * 100
        current_show_number += common.hex_str_to_int(data_list[4])
        current_show_number += common.hex_str_to_int(data_list[4]) * 0.01
        result.current_show = current_show_number

        return result

    # 读取当前显示数值（不等待）:
    # 上位机请求格式: F5 03 A1 [01:电压 | 02: 电流] [crc8]
    def send_show_voltage_request(self):
        self.serial.send(common.append_crc8("F5 03 A1 01"))
        self.respond_parse_func_point = self.read_show_voltage_request

    # 读取当前显示数值（不等待）:
    # 单片机返回格式: FA 07 1A [电流档位] ["设备: 电压:01 | 电流表:02] [data1] [data2] [data3] [crc8]
    def read_show_voltage_request(self, data: str):
        result = Result()
        data_list = data.split()
        if data_list[2] != common.to_hex_str("1A"):
            raise exception.RespondParseException(
                "解析单片机对获取当前电压的返回消息错误: 第3位字节[" + data_list[2] + "]不是功能指令")

        if data_list[3] != self.current_level:
            raise exception.RespondParseException(
                "解析单片机对获取当前电压的返回消息错误: 第3位字节电流档位[" + data_list[2] + "]不是之前设置的电流档位[" + self.current_level + "]")
        result.current_level = self.get_key_by_value(data_list[3])

        if data_list[4] != common.to_hex_str("01"):
            raise exception.RespondParseException(
                "解析单片机对获取当前电压的返回消息错误: 第4位字节[" + data_list[2] + "]不是电压表指令('02')")
        voltage_show_number = 0
        voltage_show_number += common.hex_str_to_int(data_list[5]) * 100
        voltage_show_number += common.hex_str_to_int(data_list[6])
        voltage_show_number += common.hex_str_to_int(data_list[7]) * 0.01
        result.voltage_show = voltage_show_number
        return result

    # 设置电压正反向控制:
    # 上位机请求格式: F5 03 a2 [正反向: 正向:00|反向:01] [crc8]
    # 单片机返回格式: FA 03 2A [正反向: 正向:00|反向:01] [crc8]
    def send_voltage_forward_request(self):
        self.serial.send(common.append_crc8("F5 03 A2 00"))
        self.voltage_direction = "00"
        self.respond_parse_func_point = self.read_set_voltage_direction_respond

    # 设置电压正反向控制:
    # 上位机请求格式: F5 03 a2 [正反向: 正向:00|反向:01] [crc8]
    # 单片机返回格式: FA 03 2A [正反向: 正向:00|反向:01] [crc8]
    def send_voltage_reverse_request(self):
        self.serial.send(common.append_crc8("F5 03 A2 01"))
        self.voltage_direction = "01"
        self.respond_parse_func_point = self.read_set_voltage_direction_respond

    # 设置电压正反向控制:
    # 上位机请求格式: F5 03 a2 [正反向: 正向:00|反向:01] [crc8]
    # 单片机返回格式: FA 03 2A [正反向: 正向:00|反向:01] [crc8]
    def read_set_voltage_direction_respond(self, data):
        data_list = data.split()
        if data_list[2] != common.to_hex_str("2A"):
            raise exception.RespondParseException(
                "解析单片机对设置当前电压方向的返回消息错误: 第3位字节[" + data_list[2] + "]不是功能指令")

        if data_list[3] != common.to_hex_str(self.voltage_direction):
            raise exception.RespondParseException(
                "解析单片机对设置当前电压方向的返回消息错误: 第3位字节电压方向[" + data_list[2] + "]不是之前设置的电压方向[" + self.voltage_direction + "]")
        result = Result()
        return result

    def get_key_by_value(self, value):
        for k, v in self.current_map.items():
            if common.to_hex_str(v) == value:
                return k
        return None

    def read_with_timeout_exception(self):
        return common.exec_with_timeout(self.timeout, self.serial.read_line)

    def read(self) -> Result:
        """
        :raise TimeoutException,RespondParseException
        :return: Result
        """
        # data = self.serial.read_line()
        data = ""
        for i in range(0, 3):  # 尝试3次读取
            # print("第" + str(i) + "次尝试读取数据")
            try:
                data = self.read_with_timeout_exception()
                break
            except exception.TimeoutException:
                continue
        if data == "":
            raise exception.TimeoutException("无法从串行接口读取数据(已重复3次,每次等待" + str(self.timeout) + "s): 通讯错误或无连接")
        data = data.strip()
        data_list = data.split()

        if data_list[0] != common.to_hex_str("FA"):
            raise exception.RespondParseException("返回数据有误: 第一位字节[" + data_list[0] + "]不是预期的字节[0xFA]")
        if common.hex_str_to_int(data_list[1]) != len(data_list) - 2:
            raise exception.RespondParseException(
                "返回数据有误: 第二位字节(表长度)[" + data_list[1] + "]不是预期的字节[" + str(len(data_list) - 2) + "]")

        if not self.check_crc8(data):
            raise exception.RespondParseException(
                "返回数据有误: crc8 计算值有误")

        return self.respond_parse_func_point(data)

    def check_crc8(self, data: str) -> bool:
        expected_value = data[-4:]
        data = data[:-4]
        return common.calculate_crc8(data) == expected_value

    def set_current_with_probe_down(self, current: float):
        self.send_set_current_request(current)
        res = self.read()
        if res.down == False:
            raise exception.ProbeNotDownException("设置电流" + str(current) + "错误,探头未压下")

    def read_voltage(self) -> float:
        """
        :raise TimeoutException,RespondParseException
        """
        self.send_show_voltage_request()
        return self.read().voltage_show

    def read_forward_voltage(self) -> float:
        self.send_voltage_forward_request()
        self.read()
        return self.read_voltage()

    def read_reverse_voltage(self) -> float:
        self.send_voltage_reverse_request()
        self.read()
        return self.read_voltage()

    def read_current(self) -> float:
        """
        :raise TimeoutException,RespondParseException
        """
        self.send_show_current_request()
        return self.read().current_show
