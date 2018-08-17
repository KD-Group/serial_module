# import serial
import serial.tools.list_ports


class RealSerial():
    port = None
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

    def convert_hex(self, string: str):
        hex_list = string.split(" ")
        target_list = []
        for hex_str in hex_list:
            if len(hex_str) != 2 and len(hex_str) != 4:
                raise Exception("hex string is error : " + hex_str + " \n example: f5 0xf5")
            if len(hex_str) == 2:
                hex_str = "0x" + hex_str
            target_list.append(hex_str)
        target_str = ""
        for hex_str in target_list:
            target_str += hex_str
        return target_str

    def get_all_ports(self) -> list:
        ports = list(serial.tools.list_ports.comports())
        port_list = []
        for port in ports:
            serial_name = list(port)[0]
            serial_fd = serial.Serial(serial_name, 9600, timeout=60)
            port_list.append(serial_fd.name)
        return port_list

    def connect(self, port_name: str) -> bool:
        try:
            # 关闭之前的连接
            if self.port is not None:
                self.close()

            # self.port = serial.Serial(port=port_name, baudrate=9600, bytesize=8, parity='E', stopbits=1,
            #                           timeout=self.timeout)
            self.port = serial.Serial(port=port_name,
                                      timeout=self.timeout,
                                      baudrate=self.baud_rate,
                                      stopbits=self.stop_bits)
            # self.port.open()
            return True

        except serial.serialutil.SerialException as e:
            # 打开端口失败
            print(e)
            return False

    # 便利所有端口，找出适配的端口（即使用通讯协议，进行通讯，通过返回消息来确定端口是否正确）
    def connect_suitable_port(self):
        for port in self.get_all_ports():
            if not self.connect(port):
                continue
            # # todo: 完成初始化通讯，保证接口正确,使用抽象类
            if self.find_suitable_port():
                return
            else:
                continue

    # todo: 考虑为抽象类？
    def find_suitable_port(self) -> bool:
        return True

    def send(self, data: str):
        self.port.write(data)

    def read(self) -> str:
        return self.port.read()


s = RealSerial()
print(s.get_all_ports())
print(s.connect("COM12"))
