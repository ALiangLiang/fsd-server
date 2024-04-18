from enum import Enum

from messages.IMessage import IMessage


class InformationCommand(Enum):
    FLIGHTPLAN = 'FP'
    COM = 'C?'
    INFO = 'INF'
    ATIS = 'ATIS'
    NAME = 'RN'
    VID = 'RV'
    TRAINING = 'T'
    SELCAL = 'SEL'


class InformationRequestMessage(IMessage):
    command = '$CQ'

    def __init__(self, source: str, destination: str, sub_command: InformationCommand, fields: list[str]):
        super().__init__()
        self.source = source
        self.destination = destination
        self.sub_command = sub_command
        self.fields = fields

    @classmethod
    def parse_raw_message(cls, raw_message: str):
        raw_message = raw_message.rstrip()
        source, destination, command, *fields = raw_message[len(
            cls.command):].split(':')
        return cls(source, destination, command, fields)

    def __str__(self):
        return self.command + ':'.join([
            self.source,
            self.destination,
            self.command,
            ':'.join(self.fields)
        ])
