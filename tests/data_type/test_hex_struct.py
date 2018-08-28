import unittest

from data_type import HexStruct


class TestHexStruct(unittest.TestCase):
    def test_init(self):
        # init by string
        hs1 = HexStruct("fa 0 fb")
        self.assertEqual(hs1.to_bytes(), b'\xfa\x00\xfb')

        # init by list
        hs2 = HexStruct([0xff, 0x00, 0xfa, 0x02, 41])
        self.assertEqual(hs2.to_bytes(), b'\xff\x00\xfa\x02)')

    def test_append_and_check_crc8(self):
        ls = [0xff, 0x00, 0xfa, 0x02, 41]
        hs = HexStruct(ls)
        self.assertTrue(hs.append_crc8().check_crc8())
        self.assertEqual(len(hs.list), len(ls) + 1)


if __name__ == '__main__':
    unittest.main()
