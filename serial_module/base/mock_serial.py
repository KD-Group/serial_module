# comment: 模拟通讯串行接口基类
import random
import time
from abc import abstractmethod
from serial_module import exception
from serial_module.interface.serial_interface import SerialInterface


class MockSerial(SerialInterface):
    current_request = None

    @abstractmethod
    def respond(self, input: str) -> str:
        pass

    def send(self, data: str):
        if self.port is None:
            raise exception.NotConnectedException(
                "未连接串行接口,请使用connect(port_name)或connect_suitable_port()进行连接")
        self.current_request = data

    def read(self, size=1):
        pass

    def read_until(self, expected=None, size=None):
        if self.port is None:
            raise exception.NotConnectedException(
                "未连接串行接口,请使用connect(port_name)或connect_suitable_port()进行连接")
        if self.current_request is None:
            time.sleep(self.timeout)
        else:
            request = self.current_request
            self.current_request = None
            return self.respond(request)

    def read_line(self):
        return self.read_until()

    def close(self):
        self.port = None

    def connect(self, port_name: str) -> bool:
        self.port = port_name
        return True

    def get_all_ports(self) -> list:
        return ["COM99", "COM98", "COM97"]

    def connect_suitable_port(self) -> bool:
        self.port = random.sample(self.get_all_ports(), 1)[0]
        return True

    def find_port_by_init_msg(self) -> bool:
        pass
