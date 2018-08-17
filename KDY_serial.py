import crcmod.predefined

import real_serial


class KDY_serial(real_serial):
    def find_suitable_port(self):
        pass

    def crc8_verify(self, data: str) -> bool:
        data = data.strip("0x")
        crc8_value = data[-2:]
        data = data[:-2]
        calculate_value = self.get_crc8_value(data)

        return calculate_value == crc8_value

    def append_crc8(self, data) -> str:
        return data + self.get_crc8_value(data)

    def get_crc8_value(self, data) -> str:
        data = data.strip("0x")
        crc8 = crcmod.predefined.Crc('crc-8-maxim')

        crc8.update(bytes().fromhex(data))

        calculate_value = str(hex(crc8.crcValue))
        if calculate_value == "0x0":
            calculate_value = "00"
        else:
            calculate_value = calculate_value[-2:]

        return calculate_value
