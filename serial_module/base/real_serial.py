# comment: 真实通讯串行接口基类
import serial
import serial.tools.list_ports
from serial_module.exception import TimeoutException

from serial_module.interface.serial_interface import SerialInterface


class RealSerial(SerialInterface):
    timeout = None  # unit: s
    baud_rate = None
    stop_bits = 1

    def __init__(self,
                 serial_controller,
                 timeout=0.5,
                 baud_rate=9600,
                 stop_bits=1):
        super().__init__(serial_controller)
        self.timeout = timeout
        self.baud_rate = baud_rate
        self.stop_bits = stop_bits
        self.logger.debug("real serial timeout: {}".format(self.timeout))
        self.logger.debug("real serial baud_rate: {}".format(self.baud_rate))
        self.logger.debug("real serial stop_bits: {}".format(self.stop_bits))
        self.logger.debug("real serial port_list: {}".format(self.port_list))

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

            self.port = serial.Serial(
                port=port_name,
                timeout=self.timeout,
                baudrate=self.baud_rate,
                stopbits=self.stop_bits)
            return True

        except serial.serialutil.SerialException as e:
            self.logger.warning("open port {} failed: {}".format(port_name, e))
            return False

    # 遍历所有端口，找出适配的端口（即使用通讯协议，进行通讯，通过返回消息来确定端口是否正确）
    def connect_suitable_port(self) -> bool:
        # print(self.get_all_ports())
        for port in self.get_all_ports():
            if not self.connect(port):
                continue
            # todo: 完成初始化通讯，保证接口正确,使用抽象类
            if self.find_port_by_init_msg():
                self.logger.info("connnect port successfully: {}".format(
                    self.port.name))
                return True
            else:
                continue
        return False

    def send(self, data: bytes):
        self.logger.info("send: {}".format(data))
        try:
            self.port.write(data)
        except serial.serialutil.SerialException as e:
            raise TimeoutException("串行接口超时： {}".format(str(e)))

    # todo: timeout exception handle
    def read(self, size=1) -> str:
        try:
            return self.port.read(size)
        except serial.serialutil.SerialException as e:
            raise TimeoutException("串行接口超时： {}".format(str(e)))

    # todo: TypeError: object of type 'NoneType' has no len()
    def read_line(self):
        try:
            line = self.port.readline()
        except serial.serialutil.SerialException as e:
            raise TimeoutException("串行接口超时： {}".format(str(e)))
        self.logger.info("receive: {}".format(line))
        return line

    @property
    def port_list(self):
        return self.get_all_ports()
