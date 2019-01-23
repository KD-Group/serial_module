# comment: 串行接口类的通用接口,如有其它接口可放在这

from abc import ABCMeta, abstractmethod


class SerialInterface(metaclass=ABCMeta):
    port = None
    timeout = 0.5  # unit: s
    parent = None

    def __init__(self, serial_controller):
        self.parent = serial_controller

    @property
    def logger(self):
        return self.parent.logger

    def set_timeout(self, timeout: float):
        self.timeout = timeout

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_all_ports(self) -> list:
        pass

    @abstractmethod
    def connect(self, port_name: str) -> bool:
        pass

    # 遍历所有端口，找出适配的端口
    @abstractmethod
    def connect_suitable_port(self) -> bool:
        pass

    # 通过对已连接的端口发送初始化的信息,根据返回消息来获取判定该端口是否是所需要的端口
    @abstractmethod
    def find_port_by_init_msg(self) -> bool:
        pass

    @abstractmethod
    def send(self, data: str):
        pass

    @abstractmethod
    def read(self, size=1) -> str:
        pass

    @abstractmethod
    def read_line(self):
        pass
