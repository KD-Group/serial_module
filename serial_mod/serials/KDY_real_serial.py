from data_type import HexStruct
from serial_mod import base


class KDYRealSerial(base.RealSerial):
    # 通过对已连接的端口发送初始化的信息,根据返回消息来获取判定该端口是否是所需要的端口
    def find_port_by_init_msg(self) -> bool:
        hs = HexStruct("F5 02 ff")
        self.send(hs.append_crc8().to_bytes())
        data = self.read_line()
        # todo: need to cmp respond msg
        # if data == HexStruct("FA 03 2A CC").append_crc8().to_bytes():
        if data == b'\xfa\t\xffKDN-100\x0b':
            return True
        else:
            return False
