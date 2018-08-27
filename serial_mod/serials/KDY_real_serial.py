from serial_mod import base


class KDYRealSerial(base.RealSerial):
    # 通过对已连接的端口发送初始化的信息,根据返回消息来获取判定该端口是否是所需要的端口
    # todo: exception handle
    def find_port_by_init_msg(self) -> bool:
        return True
