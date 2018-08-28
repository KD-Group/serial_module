import unittest

from serial_mod import exception, serials,KDASerialController


class KDYSerialTest(unittest.TestCase):

    def test_exception(self):
        # not connection exception
        kdy = KDASerialController(mock=True)
        self.assertRaises(exception.NotConnectedException, kdy.read)

        kdy.connect_serial()

        # timeout exception: must one request and read one respond
        # todo: excetion?
        # self.assertRaises(exception.TimeoutException, kdy.read)

    def test_connect(self):
        kdy = KDASerialController(mock=True)
        self.assertIsInstance(kdy.serial, serials.KDAMockSerial)
        kdy.connect_serial()
        self.assertTrue(kdy.serial.port is not None)

    def test_set_current_request(self):
        kdy = KDASerialController(mock=True)
        kdy.connect_serial()
        kdy.send_set_current_request(0.01)
        self.assertEqual(kdy.read().current_level, 0.01)
        kdy.send_show_current_request()
        self.assertIsInstance(kdy.read_current(), float)

    def test_set_show_voltage_request(self):
        kdy = KDASerialController(mock=True)
        kdy.connect_serial()
        kdy.send_set_current_request(0.01)
        self.assertEqual(kdy.read().current_level, 0.01)

        self.assertIsInstance(kdy.read_forward_voltage(), float)
        self.assertIsInstance(kdy.read_reverse_voltage(), float)

    def test_is_pressed(self):
        kdy = KDASerialController(mock=True)
        kdy.connect_serial()

        # self.assertRaises(exception.NotSetCurrentException, kdy.is_pressed)

        kdy.send_set_current_request(0.1)
        self.assertTrue(kdy.is_pressed())


if __name__ == '__main__':
    unittest.main()
