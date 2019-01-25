# comment: 十六进制结构体
import crcmod


class HexStruct():
    def __init__(self, data):
        self.list = []  # contain int obj
        origin_data = data
        if isinstance(data, str):
            data = data.replace("0x", "")
            data_list = data.split()
            if len(data_list) == 0:
                return
            for i in data_list:
                self.list.append(int(i, 16))
            else:
                assert "HexStruct __init__ argument " + origin_data + "->" + data + " length must be even number"
        elif isinstance(data, list):
            self.list = data.copy()
        elif isinstance(data, bytes):
            self.list = list(data)
        else:
            assert "HexStruct __init__ argument must str or list"

    def to_bytes(self):
        return bytes(self.list)

    def append_crc8(self):
        crc8 = crcmod.predefined.Crc('crc-8-maxim')
        crc8.update(self.to_bytes())
        self.list.append(crc8.crcValue)
        return self

    def check_crc8(self):
        if len(self.list) < 2:
            raise Exception("can't check the crc8 value: the length of" +
                            str(self.list) + " is less than 2")
        expected_crc8_value = self.list[-1]
        crc8 = crcmod.predefined.Crc('crc-8-maxim')
        crc8.update(bytes(self.list[0:-1]))
        return expected_crc8_value == crc8.crcValue
