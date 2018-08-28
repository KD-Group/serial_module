import unittest

from serial_mod import serials


class TestKDARealSerial(unittest.TestCase):
    # def test_exception(self):
    #     # not connection exception
    #     kdy = serials.KDYSerialController(mock=True)
    #     self.assertRaises(exception.NotConnectedException, kdy.read)
    #
    #     kdy.connect_serial()
    #
    #     # timeout exception: must one request and read one respond
    #     self.assertRaises(exception.TimeoutException, kdy.read)

    def test_connect(self):
        kdy = serials.KDYSerialController(mock=False)
        kdy.connect_serial()
        self.assertTrue(kdy.serial.port is not None)

        kdy.close()

    # 测试原始命令，请参考文档
    def test_origin_cmd(self):
        kdy = serials.KDYSerialController(mock=False)
        kdy.connect_serial()
        kdy.serial.send(b'\xf5\x03\xc1\x01:')

        data = b''
        for i in range(0, 3):
            data = kdy.serial.read_line()
            if data == b'':
                continue
            else:
                break
        self.assertEqual(data, b'\xfa\x04\x1c\x01\x00 ')

        kdy.close()

    # 测试设置电流
    def test_set_current_request(self):
        kdy = serials.KDYSerialController(mock=False)
        kdy.connect_serial()
        kdy.send_set_current_request(0.01)
        self.assertEqual(kdy.read().current_level, 0.01)
        kdy.send_show_current_request()
        self.assertIsInstance(kdy.read_current(), float)
        kdy.close()

    def test_set_show_voltage_request(self):
        kdy = serials.KDYSerialController(mock=False)
        kdy.connect_serial()
        kdy.send_set_current_request(0.01)
        self.assertEqual(kdy.read().current_level, 0.01)

        forward_V = kdy.read_forward_voltage()
        self.assertIsInstance(forward_V, float)
        # print(forward_V)
        reverse_V = kdy.read_reverse_voltage()
        self.assertIsInstance(reverse_V, float)
        # print(reverse_V)
        kdy.close()

    # 测试探头是否压下
    def test_is_pressed(self):
        kdy = serials.KDYSerialController(mock=False)
        kdy.connect_serial()

        kdy.set_current_without_probe_down(0.1)
        self.assertFalse(kdy.is_pressed())
        kdy.close()


if __name__ == '__main__':
    unittest.main()
