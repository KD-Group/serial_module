import logging

import serial
import serial.tools.list_ports

from serial_mod import interface


class RealSerial(interface.SerialInterface):
    timeout = None  # unit: s
    baud_rate = None
    stop_bits = 1

    def __init__(self, timeout=0.5, baud_rate=9600, stop_bits=1):
        self.timeout = timeout
        self.baud_rate = baud_rate
        self.stop_bits = stop_bits
        # self.set_debug()
        self.debug_var("self.timeout")
        self.debug_var("self.baud_rate")
        self.debug_var("self.stop_bits")
        self.debug_var("self.port_list")

    def close(self):
        if self.port is not None:
            self.port.close()
            self.port = None

    def get_all_ports(self) -> list:
        ports = list(serial.tools.list_ports.comports())
        port_list = []
        for port in ports:
            serial_name = list(port)[0]
            if serial_name not in port_list:
                port_list.append(serial_name)
        return port_list

    def connect(self, port_name: str) -> bool:
        try:
            # 关闭之前的连接
            if self.port is not None:
                self.close()

            self.port = serial.Serial(port=port_name,
                                      timeout=self.timeout,
                                      baudrate=self.baud_rate,
                                      stopbits=self.stop_bits)
            return True

        except serial.serialutil.SerialException as e:
            # 打开端口失败
            print(e)
            return False

    # 遍历所有端口，找出适配的端口（即使用通讯协议，进行通讯，通过返回消息来确定端口是否正确）
    def connect_suitable_port(self) -> bool:
        # print(self.get_all_ports())
        for port in self.get_all_ports():
            if not self.connect(port):
                continue
            # todo: 完成初始化通讯，保证接口正确,使用抽象类
            if self.find_port_by_init_msg():
                self.debug_print("连接并校验成功到接口:")
                self.debug_var("self.port.name")
                return True
            else:
                continue
        return False

    def send(self, data: bytes):
        logging.info("上位机发送字节: {}".format(data))
        self.port.write(data)

    # todo: timeout exception handle
    def read(self, size=1) -> str:
        return self.port.read(size)

    # todo: TypeError: object of type 'NoneType' has no len()
    def read_line(self):
        # self.port.timeout = sel
        line = self.port.readline()
        logging.info("单片机发送字节: {}".format(line))
        return line
        # pass

    @property
    def port_list(self):
        return self.get_all_ports()
