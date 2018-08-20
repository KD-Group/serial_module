import unittest

import exception
import serials


class KDYSerialTest(unittest.TestCase):

    def test_exception(self):
        # not connection exception
        kdy = serials.KDYSerialController(mock=True)
        self.assertRaises(exception.NotConnectedException, kdy.read)

        kdy.connect_serial()

        # timeout exception: must one request and read one respond
        self.assertRaises(exception.TimeoutException, kdy.read)

    def test_connect(self):
        kdy = serials.KDYSerialController(mock=True)
        self.assertIsInstance(kdy.serial, serials.KDYMockSerial)
        kdy.connect_serial()
        self.assertTrue(kdy.serial.port is not None)

    def test_set_current_request(self):
        kdy = serials.KDYSerialController(mock=True)
        kdy.connect_serial()
        kdy.send_set_current_request(0.01)
        self.assertEqual(kdy.read().current_level, 0.01)
        kdy.send_show_current_request()
        self.assertIsInstance(kdy.read().current_show, float)

    def test_set_show_voltage_request(self):
        kdy = serials.KDYSerialController(mock=True)
        kdy.connect_serial()
        kdy.send_set_current_request(0.01)
        self.assertEqual(kdy.read().current_level, 0.01)
        kdy.send_show_voltage_request()
        self.assertIsInstance(kdy.read().voltage_show, float)


if __name__ == '__main__':
    unittest.main()
