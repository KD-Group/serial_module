import serial.tools.list_ports

import interface


class RealSerial(interface.SerialInterface):
    timeout = None  # unit: s
    baud_rate = None
    stop_bits = 1

    def __init__(self, timeout=0.5, baud_rate=9600, stop_bits=1):
        self.timeout = timeout
        self.baud_rate = baud_rate
        self.stop_bits = stop_bits

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
        for port in self.get_all_ports():
            if not self.connect(port):
                continue
            # todo: 完成初始化通讯，保证接口正确,使用抽象类
            if self.find_port_by_init_msg():
                return True
            else:
                continue
        return False

    def send(self, data: str):
        self.port.write(data)

    # todo: timeout exception handle
    def read(self, size=1) -> str:
        return self.port.read(size)

    # todo: timeout exception handle
    def read_until(self, expected=None, size=None):
        pass

    def read_line(self):
        pass

# s = RealSerial()
# print(s.get_all_ports())
# print(s.connect("COM1"))