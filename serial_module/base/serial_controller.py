# comment: 串行接口控制类, 控制是采用模拟接口还是真实接口以及串行接口通讯日志
from serial_module.base.real_serial import RealSerial
from serial_module.base.mock_serial import MockSerial
import logging


class NotSetSerial(Exception):
    pass


class SerialController:
    real_serial = None
    mock_serial = None
    is_mock = False
    debug = False
    __logger = None

    def set_real_serial(self, serial: RealSerial):
        self.real_serial = serial

    def set_mock_serial(self, serial: MockSerial):
        self.mock_serial = serial

    def set_debug(self, debug=True):
        self.debug = debug

    @property
    def logger(self):
        if self.__logger is None:
            # set default logger to print to console
            logger = logging.getLogger()
            sh = logging.StreamHandler()
            sh.setFormatter(
                logging.Formatter(
                    '%(asc'
                    'time)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                ))
            if self.debug:
                logger.setLevel(logging.DEBUG)
            else:
                logger.setLevel(logging.INFO)
            self.__logger = logger
        return self.__logger

    @property
    def serial(self):
        if self.is_mock:
            if self.mock_serial is None:
                raise NotSetSerial(
                    "not set mock serial: use set_mock_serial(serial) to set")
            return self.mock_serial
        else:
            if self.real_serial is None:
                raise NotSetSerial(
                    "not set real serial: use set_real(serial) to set")
            return self.real_serial

    def set_logger(self, logger):
        self.__logger = logger
