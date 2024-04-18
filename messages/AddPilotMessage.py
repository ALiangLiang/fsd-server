from enum import Enum

from messages.AddATCMessage import AddATCMessage


class SimulatorType(Enum):
    FS95 = 1
    FS98 = 2
    CFS = 3
    FS2000 = 4
    CFS2 = 5
    FS2002 = 6
    CFS3 = 7
    FS2004 = 8
    X_PLANE = 11  # 0x0000000B
    PS1 = 15  # 0x0000000F
    FLY = 20  # 0x00000014
    FLIGHT_GEAR = 25  # 0x00000019
    MSFS = 40  # 0x00000028


class AddPilotMessage(AddATCMessage):
    command = '#AP'

    def __init__(
        self,
        source: str,
        destination: str,
        real_name: str,
        account: str,
        password: str,
        rating: int,
        protocol_version: str = 'B',
        simulator: SimulatorType = SimulatorType.MSFS
    ):
        super().__init__(
            source=source,
            destination=destination,
            real_name=real_name,
            account=account,
            password=password,
            rating=rating,
            protocol_version=protocol_version,
        )
        self.simulator = simulator

    @staticmethod
    def parse_raw_message(raw_message):
        [source, destination, account, password, simulator, protocol_version,
            rating, real_name] = raw_message[3:].split(':')
        return AddPilotMessage(
            source=source,
            destination=destination,
            real_name=real_name,
            account=account,
            password=password,
            rating=int(rating),
            protocol_version=protocol_version,
            simulator=SimulatorType(int(simulator))
        )

    def __str__(self):
        return self.command + ':'.join([
            self.source,
            self.destination,
            self.account,
            self.password,
            str(self.rating),
            self.protocol_version,
            str(self.simulator.value),
            self.real_name,
        ])
