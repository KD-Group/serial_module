import crcmod.predefined

crc8 = crcmod.predefined.Crc('crc-8-maxim')

crc8.update(bytes().fromhex('0001'))

print(str(hex(crc8.crcValue)))

# a = "abvavbab"
# a.strip("ab")

# https://www.jianshu.com/p/11d48d7017c6