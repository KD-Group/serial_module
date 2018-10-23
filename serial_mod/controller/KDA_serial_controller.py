import logging

from serial_mod import interface, exception
from serial_mod.base import SerialDebug
from serial_mod.data_type import HexStruct
from serial_mod.serials import KDAMockSerial, KDARealSerial


class Result():
    current_level = None  # 电流档位
    current_show = None  # 电流表显示数值
    voltage_show = None  # 电压表显示数值
    down = None


class KDASerialController(SerialDebug):
    serial = None
    respond_parse_func_point = None
    last_result = None
    current_level = None
    timeout = 0.5
    current = 1  # 默认电流
    voltage_direction = "00"  # 00 为正向, 01 为反向

    current_map = {
        0.01: 1,
        0.1: 2,
        1: 3,
        10: 4,
        100: 5,
    }

    def __init__(self, mock=True, debug=False, log_file_path=None):
        if mock:
            self.set_serial(KDAMockSerial())
        else:
            self.set_serial(KDARealSerial())
        self.serial.set_timeout(self.timeout)

        if debug:
            self.set_debug()
            self.serial.set_debug()

        if log_file_path is not None:
            logging.basicConfig(filename=log_file_path, level=logging.INFO,
                                format='%(asc''time)s:%(level''name)s:%(message)s')
            logging.info("start serial controller......")

    def set_serial(self, serial: interface.SerialInterface):
        self.serial = serial

    def connect_serial(self):
        try:
            if not self.serial.connect_suitable_port():
                raise Exception("请检查接口是否接好，或者串行端口是否被占用")
        except Exception as e:
            raise exception.ConnectionException(str(e))

    # 上位机请求格式: F5 03 C1 [电流档位: 00:0.001mA | 01:0.01mA | 02:0.1mA | 03:1mA | 04:10mA | 05:100mA] [crc8]
    def send_set_current_request(self, current: float):
        logging.info("请求设置电流档位...")
        assert self.current_map.__contains__(current)
        self.current = current
        converted_current = self.current_map[current]
        self.serial.send(HexStruct("F5 03 C1 " + str(converted_current)).append_crc8().to_bytes())
        self.respond_parse_func_point = self.read_current_respond

    # 单片机返回格式: FA 04 1C [电流档位] [探头是否压下: 是:01 | 否:00] [crc8]
    def read_current_respond(self, data: HexStruct) -> Result:
        logging.info("读取电流测量档位...")
        # todo: exception: timeout parse_exception
        result = Result()
        data_list = data.list
        for actual_value, map_value in self.current_map.items():
            if map_value == data_list[3]:
                result.current_level = actual_value
                self.current_level = map_value
                break
        if result.current_level is None:
            logging.info("解析单片机对设定当前测量档位的返回消息错误: 第4位字节[" + data_list[3] + "]不是电流档位指令")
            raise exception.RespondParseException(
                "解析单片机对设定当前测量档位的返回消息错误: 第4位字节[" + data_list[3] + "]不是电流档位指令")

        if result.current_level != self.current:
            logging.info("解析单片机对设定当前测量档位的返回消息错误: 第4位字节[{}({})]不是之前设定的电流档位指令[{}({})]"
                         .format(data_list[3], result.current_level, self.current_map[self.current], self.current))
            raise exception.RespondParseException(
                "解析单片机对设定当前测量档位的返回消息错误: 第4位字节[{}({})]不是之前设定的电流档位指令[{}({})]"
                    .format(data_list[3], result.current_level, self.current_map[self.current], self.current)
            )

        if data_list[4] == 1:
            result.down = True
        elif data_list[4] == 0:
            result.down = False
        else:
            logging.info("解析单片机对设定当前测量档位的返回消息错误: 第4位字节[{}]不是探头压下指令".format(data_list[4]))
            raise exception.RespondParseException(
                "解析单片机对设定当前测量档位的返回消息错误: 第4位字节[{}]不是探头压下指令".format(data_list[4]))
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
        logging.info("请求显示数值...")
        self.serial.send(HexStruct("F5 03 A1 02").append_crc8().to_bytes())
        self.respond_parse_func_point = self.read_show_current_respond

    # 读取当前显示数值（不等待）:
    # 单片机返回格式: FA 07 1A [电流档位] ["设备: 电压:01 | 电流表:02] [data1] [data2] [data3] [crc8]
    def read_show_current_respond(self, data: HexStruct):
        logging.info("读取显示数值...")
        result = Result()
        data_list = data.list
        if data_list[2] != int("1A", 16):
            logging.info("解析单片机对获取当前电流的返回消息错误: 第2位字节[" + data_list[2] + "]不是功能指令[0x1A]")
            raise exception.RespondParseException(
                "解析单片机对获取当前电流的返回消息错误: 第2位字节[" + data_list[2] + "]不是功能指令[0x1A]")

        if data_list[3] != self.current_level:
            logging.info("解析单片机对获取当前电流的返回消息错误: 第3位字节电流档位[" + data_list[3] +
                         "]不是之前设置的电流档位[" + self.current_level + "]")
            raise exception.RespondParseException(
                "解析单片机对获取当前电流的返回消息错误: 第3位字节电流档位[" + data_list[3] + "]不是之前设置的电流档位[" + self.current_level + "]")
        result.current_level = self.get_key_by_value(data_list[3])

        if data_list[4] != 2:
            logging.info("解析单片机对获取当前电流的返回消息错误: 第4位字节[" + data_list[2] + "]不是电压表指令('02')")
            raise exception.RespondParseException(
                "解析单片机对获取当前电流的返回消息错误: 第4位字节[" + data_list[2] + "]不是电压表指令('02')")
        current_show_str = self.int_to_hex_show_str(data_list[5]) + self.int_to_hex_show_str(data_list[6]) + \
                           self.int_to_hex_show_str(data_list[7])
        result.current_show = int(current_show_str[0:-1])
        return result

    # 读取当前电压（不等待）:
    # 上位机请求格式: F5 03 A1 [01:电压 | 02: 电流] [crc8]
    def send_show_voltage_request(self):
        logging.info("请求电压显示数值...")
        self.serial.send(HexStruct("F5 03 A1 01").append_crc8().to_bytes())
        self.respond_parse_func_point = self.read_show_voltage_request

    # 读取当前显示数值（不等待）:
    # 单片机返回格式: FA 07 1A [电流档位] ["设备: 电压:01 | 电流表:02] [data1] [data2] [data3] [crc8]
    def read_show_voltage_request(self, data: HexStruct):
        logging.info("读取电压显示数值...")
        result = Result()
        data_list = data.list
        if data_list[2] != int("1A", 16):
            logging.info("解析单片机对获取当前电压的返回消息错误: 第3位字节[" + data_list[2] + "]不是功能指令")
            raise exception.RespondParseException(
                "解析单片机对获取当前电压的返回消息错误: 第3位字节[" + data_list[2] + "]不是功能指令")

        if data_list[3] != self.current_level:
            logging.info("解析单片机对获取当前电压的返回消息错误: 第3位字节电流档位[" + data_list[2] + "]不是之前设置的电流档位[" + self.current_level + "]")
            raise exception.RespondParseException(
                "解析单片机对获取当前电压的返回消息错误: 第3位字节电流档位[" + data_list[2] + "]不是之前设置的电流档位[" + self.current_level + "]")
        result.current_level = self.get_key_by_value(data_list[3])

        if data_list[4] != 1:
            logging.info("解析单片机对获取当前电压的返回消息错误: 第4位字节[" + data_list[2] + "]不是电压表指令('02')")
            raise exception.RespondParseException(
                "解析单片机对获取当前电压的返回消息错误: 第4位字节[" + data_list[2] + "]不是电压表指令('02')")
        voltage_show_str = self.int_to_hex_show_str(data_list[5]) + \
                           self.int_to_hex_show_str(data_list[6]) + \
                           self.int_to_hex_show_str(data_list[7])
        result.voltage_show = int(voltage_show_str[0:-1])
        return result

    # 设置电压正反向控制:
    # 上位机请求格式: F5 03 a2 [正反向: 正向:00|反向:01] [crc8]
    # 单片机返回格式: FA 03 2A [正反向: 正向:00|反向:01] [crc8]
    def send_voltage_forward_request(self):
        logging.info("请求设置电压为正向...")
        self.serial.send(HexStruct("F5 03 A2 00").append_crc8().to_bytes())
        self.voltage_direction = 0
        self.respond_parse_func_point = self.read_set_voltage_direction_respond

    # 设置电压正反向控制:
    # 上位机请求格式: F5 03 a2 [正反向: 正向:00|反向:01] [crc8]
    # 单片机返回格式: FA 03 2A [正反向: 正向:00|反向:01] [crc8]
    def send_voltage_reverse_request(self):
        logging.info("请求设置电压为反向...")
        self.serial.send(HexStruct("F5 03 A2 01").append_crc8().to_bytes())
        self.voltage_direction = 1
        self.respond_parse_func_point = self.read_set_voltage_direction_respond

    # 设置电压正反向控制:
    # 上位机请求格式: F5 03 a2 [正反向: 正向:00|反向:01] [crc8]
    # 单片机返回格式: FA 03 2A [正反向: 正向:00|反向:01] [crc8]
    def read_set_voltage_direction_respond(self, data: HexStruct):
        logging.info(" 读取设置电压正反向控制返回结果")
        data_list = data.list
        if data_list[2] != int("2a", 16):
            logging.info("解析单片机对设置当前电压方向的返回消息错误: 第3位字节[{}]不是功能指令".format(data_list[2]))
            raise exception.RespondParseException(
                "解析单片机对设置当前电压方向的返回消息错误: 第3位字节[{}]不是功能指令".format(data_list[2]))
        if data_list[3] != int("cc", 16):
            logging.info(
                "解析单片机对设置当前电压方向的返回消息错误: 第4位字节电压方向[{}]不是之前设置的电压方向[{}]".format(data_list[2], self.voltage_direction))
            raise exception.RespondParseException(
                "解析单片机对设置当前电压方向的返回消息错误: 第4位字节电压方向[{}]不是之前设置的电压方向[{}]".format(data_list[2], self.voltage_direction))
        result = Result()
        return result

    def get_key_by_value(self, value):
        for k, v in self.current_map.items():
            if v == value:
                return k
        return None

    def read(self) -> Result:
        """
        :raise TimeoutException,RespondParseException
        :return: Result
        """
        # data = self.serial.read_line()
        data = b''
        for i in range(0, 5):  # 尝试3次读取
            # print("第" + str(i) + "次尝试读取数据")
            data = self.serial.read_line()
            if data == b'':
                continue
            else:
                break

        if data == b'':
            logging.info("无法从串行接口读取数据(已重复3次,每次等待" + str(self.timeout) + "s): 通讯错误或无连接")
            raise exception.TimeoutException("无法从串行接口读取数据(已重复3次,每次等待" + str(self.timeout) + "s): 通讯错误或无连接")

        hs = HexStruct(data)
        data_list = hs.list

        if data_list[0] != int("fa", 16):
            logging.info("返回数据有误: 第一位字节[" + data_list[0] + "]不是预期的字节[0xFA]")
            raise exception.RespondParseException("返回数据有误: 第一位字节[" + data_list[0] + "]不是预期的字节[0xFA]")
        if data_list[1] != len(data_list) - 2:
            logging.info("返回数据有误: 第二位字节(表长度)[{}]不是预期的字节[{}]".format(data_list[1], len(data_list) - 2))
            raise exception.RespondParseException(
                "返回数据有误: 第二位字节(表长度)[{}]不是预期的字节[{}]".format(data_list[1], len(data_list) - 2))

        if not hs.check_crc8():
            logging.info("返回数据有误: crc8 计算值有误")
            raise exception.RespondParseException("返回数据有误: crc8 计算值有误")

        return self.respond_parse_func_point(hs)

    def set_current_with_probe_down(self, current: float):
        self.send_set_current_request(current)
        res = self.read()
        if res.down == False:
            raise exception.ProbeNotDownException("设置电流" + str(current) + "错误,探头未压下")

    def set_current_without_probe_down(self, current: float):
        self.send_set_current_request(current)
        res = self.read()
        if res.down == True:
            raise exception.ProbeNotDownException("设置电流" + str(current) + "错误,探头未压下")

    def read_voltage(self) -> float:
        """
        :raise TimeoutException,RespondParseException
        """
        self.send_show_voltage_request()
        return self.read().voltage_show

    def read_forward_voltage(self) -> float:
        logging.info("读取正向电压...")
        self.send_voltage_forward_request()
        self.read()
        return self.read_voltage()

    def read_reverse_voltage(self) -> float:
        logging.info("读取反向电压...")
        self.send_voltage_reverse_request()
        self.read()
        return self.read_voltage()

    def read_current(self) -> float:
        logging.info("读取电流...")
        """
        :raise TimeoutException,RespondParseException
        """
        self.send_show_current_request()
        return self.read().current_show

    def close(self):
        self.serial.close()

    def int_to_hex_show_str(self, data: int):
        hex_str = hex(data)
        int_str = hex_str[2:]
        if(len(int_str) == 1):
            int_str = '0'+int_str
        return int_str
