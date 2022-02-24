import socket
from enum import Enum
from typing import Union, Optional

class CommandFailed(Exception):
    pass

class NotConnected(Exception):
    pass

class UnrecognisedResponse(Exception):
    pass

class PowerState(Enum):
    ON = 1
    STANDBY = 2
    NOT_SUPPORTED = 3

class Projector:

    def __init__(self, ip: str, port: int = 7142):
        self.ip = ip
        self.port = port
        self.socket = None  # type: Optional[socket.socket]

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))

    def get_power_state(self) -> PowerState:
        if self.socket is None:
            raise Exception('not connected')

        self.socket.send(bytearray.fromhex('00850000010187'))
        data = self.socket.recv(22)
        if len(data) == 8:
            # TODO: add error information
            raise CommandFailed('Command failed: {}'.format(data.hex()))

        # verify the first set of bytes
        if data[0] != 0x20 or data[1] != 0x85 or data[4] != 0x10:
            raise UnrecognisedResponse("wanted 0x20 0x85 ... 0x10 got {} {} .. {}".format(hex(data[0]), hex(data[1]), hex(data[4])))

        if data[7] == 0x00:
            return PowerState.STANDBY
        elif data[7] == 0x01:
            return PowerState.ON
        elif data[7] == 0xFF:
            return PowerState.NOT_SUPPORTED
        else:
            raise UnrecognisedResponse()

    def power_on(self):
        if self.socket is None:
            raise Exception('not connected')

        self.socket.send(bytearray.fromhex('020000000002'))
        data = self.socket.recv(8)
        if len(data) == 8:
            # TODO: add error information
            raise CommandFailed('Command failed: {}'.format(data.hex()))

        if not (data[0] == 0x22 and data[1] == 0x00 and data[4] == 0x00):
            raise UnrecognisedResponse()

    def power_off(self):
        if self.socket is None:
            raise Exception('not connected')

        self.socket.send(bytearray.fromhex('020100000003'))
        data = self.socket.recv(8)
        if len(data) == 8:
            # TODO: add error information
            raise CommandFailed('Command failed: {}'.format(data.hex()))

        if not (data[0] == 0x22 and data[1] == 0x01 and data[4] == 0x00):
            raise UnrecognisedResponse()

    def close(self):
        self.socket.close()

