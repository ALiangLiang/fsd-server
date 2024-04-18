from logging import getLogger

from messages.AddATCMessage import AddATCMessage
from messages.AddPilotMessage import AddPilotMessage
from messages.AssumeControlMessage import AssumeControlMessage
from messages.ATCPositionUpdateMessage import ATCPositionUpdateMessage
from messages.ClearedFlightlevelMessage import ClearedFlightlevelMessage
from messages.ClearedSpeedMessage import ClearedSpeedMessage
from messages.ClearedWaypointMessage import ClearedWaypointMessage
from messages.ClientVerificationMessage import ClientVerificationMessage
from messages.ReleaseControlMessage import ReleaseControlMessage
from messages.RegistrationInformationMessage import RegistrationInformationMessage
from messages.RequestPlaneParamsMessage import RequestPlaneParamsMessage
from messages.RequestPlaneInfoMessage import RequestPlaneInfoMessage
from messages.ServerVerificationMessage import ServerVerificationMessage
from messages.InformationRequestMessage import InformationRequestMessage, InformationCommand
from messages.InformationReplyMessage import InformationReplyMessage
from messages.TextMessage import TextMessage
from messages.IMessage import IMessage
from messages.PilotPositionUpdateMessage import PilotPositionUpdateMessage
from utils.connection import Connection
from utils.user import User

logger = getLogger(__name__)


class FsdController:
    def __init__(self, source_conn: Connection, connections: dict[str, Connection]):
        self.source_conn = source_conn
        self.connections = connections

    def route(self, raw_message: str):
        major_command = raw_message[0]
        logger.debug('Data received: %s' % raw_message)
        message = None
        if major_command == '#':  # CommunicationMessage
            minor_command = raw_message[1:3]
            if minor_command == 'AT':
                logger.debug('Received ATISMessage')
            if minor_command == 'AC':
                logger.debug('Received ATISCancelMessage')
            elif minor_command == 'AA':
                message = AddATCMessage.parse_raw_message(raw_message)
                self.handle_add_atc_message(message)
            elif minor_command == 'AP':
                message = AddPilotMessage.parse_raw_message(raw_message)
                self.handle_add_pilot_message(message)
            elif minor_command == 'TM':
                message = TextMessage.parse_raw_message(raw_message)
                self.handle_text_message(message)
        elif major_command == '%':  # PositionUpdateMessage
            message = ATCPositionUpdateMessage.parse_raw_message(raw_message)
            self.handle_atc_position_update_message(message)
        elif major_command == '@':  # PilotPositionUpdateMessage
            message = PilotPositionUpdateMessage.parse_raw_message(raw_message)
            self.handle_pilot_position_update_message(message)
        elif major_command == '$':  # AdministrativeMessage
            minor_command = raw_message[1:3]
            if minor_command == 'CQ':
                message = InformationRequestMessage.parse_raw_message(
                    raw_message)
                self.handle_information_request_message(message)
        elif major_command == '=':  # ClearanceMessage
            minor_command = raw_message[1]
            if minor_command == 'A':
                message = AssumeControlMessage.parse_raw_message(raw_message)
                self.handle_assume_control_message(message)
            if minor_command == 'R':
                message = ReleaseControlMessage.parse_raw_message(raw_message)
                self.handle_release_control_message(message)
            if minor_command == 'W':
                message = ClearedWaypointMessage.parse_raw_message(raw_message)
                self.handle_cleared_waypoint_message(message)
            if minor_command == 'S':
                message = ClearedSpeedMessage.parse_raw_message(raw_message)
                self.handle_cleared_speed_message(message)
            if minor_command == 'F':
                message = ClearedFlightlevelMessage.parse_raw_message(
                    raw_message)
                self.handle_cleared_flightlevel_message(message)
        elif major_command == '!':  # VerificationMessage
            minor_command = raw_message[1]
            if minor_command == 'S':
                logger.debug('Received ServerVerificationMessage')
            if minor_command == 'C':
                message = ClientVerificationMessage.parse_raw_message(
                    raw_message)
                self.handle_client_verification_message(message)
        elif major_command == '-':  # PilotMessage
            minor_command = raw_message[1]
            if minor_command == 'PR':
                message = RequestPlaneInfoMessage.parse_raw_message(
                    raw_message)
                self.handle_request_plane_info_message(message)
            if minor_command == 'MR':
                message = RequestPlaneParamsMessage.parse_raw_message(
                    raw_message)
                self.handle_request_plane_params_message(message)
        else:
            logger.debug('Unknown data received: %s' % raw_message)

        return message

    def relay_to_other_connections(self, message: IMessage):
        for connection in self.connections.values():
            if connection == self.source_conn:
                continue
            connection.send(message)

    def send_to_all_connections(self, message: IMessage):
        for connection in self.connections.values():
            connection.send(message)

    def send_text_to_all_connections(self, source: str, target: str, msg: str):
        for connection in self.connections.values():
            connection.send(
                TextMessage(
                    source,
                    target,
                    msg
                )
            )

    def handle_add_atc_message(self, message: AddATCMessage):
        # self.relay_to_other_connections(message)
        self.source_conn.user = User(
            message.real_name,
            message.rating,
            message.account,
        )
        self.source_conn.send(
            ServerVerificationMessage(
                message.destination,
                message.source,
                0
            )
        )

    def handle_add_pilot_message(self, message: AddPilotMessage):
        self.source_conn.user = User(
            message.real_name,
            message.rating,
            message.account,
        )
        self.source_conn.send(
            ServerVerificationMessage('SERVER', message.source, 0)
        )

    def handle_client_verification_message(self, message: ClientVerificationMessage):
        self.source_conn.send(
            RegistrationInformationMessage(
                source=message.destination,
                destination=message.source,
                signature=RegistrationInformationMessage.compute_signature(
                    message.signature,
                    int(self.source_conn.user.account),
                    message.seed
                ),
                rating=self.source_conn.user.rating,
                admin_level=12,
                ip_address=self.source_conn.transport.get_extra_info(
                    'peername')[0]
            )
        )

    def handle_text_message(self, message: TextMessage):
        self.relay_to_other_connections(message)

    def handle_atc_position_update_message(self, message: ATCPositionUpdateMessage):
        self.relay_to_other_connections(message)

    def handle_pilot_position_update_message(self, message: PilotPositionUpdateMessage):
        self.relay_to_other_connections(message)

    def handle_information_request_message(self, message: InformationRequestMessage):
        if message.sub_command == InformationCommand.FLIGHTPLAN.value:
            callsign = message.fields[0]
            for conn in self.connections.values():
                if conn.type == 'PILOT' and conn.aircraft is not None and conn.aircraft.callsign == callsign:
                    self.source_conn.send(
                        conn.aircraft.get_flightplan_message(callsign)
                    )
        elif message.sub_command == InformationCommand.NAME.value:
            self.source_conn.send(
                str(
                    InformationReplyMessage(
                        message.destination,
                        message.source,
                        InformationCommand.NAME.value,
                        ['A bot', 'USER', '4']
                    )
                )
            )
        elif message.sub_command == InformationCommand.ATIS.value:
            # TODO: send ATIS message back
            pass
        elif message.sub_command == InformationCommand.COM.value:
            self.source_conn.send(
                str(
                    InformationReplyMessage(
                        message.destination,
                        message.source,
                        InformationCommand.COM.value,
                        ['1' + self.frequency[1:3] + '.' + self.frequency[3:]]
                    )
                )
            )

    def handle_assume_control_message(self, message: AssumeControlMessage):
        self.relay_to_other_connections(message)

    def handle_release_control_message(self, message: ReleaseControlMessage):
        self.relay_to_other_connections(message)

    def handle_cleared_waypoint_message(self, message: ClearedWaypointMessage):
        self.relay_to_other_connections(message)

    def handle_cleared_speed_message(self, message: ClearedSpeedMessage):
        self.relay_to_other_connections(message)

    def handle_cleared_flightlevel_message(self, message: ClearedFlightlevelMessage):
        self.relay_to_other_connections(message)

    def handle_request_plane_info_message(self, message: RequestPlaneInfoMessage):
        pass

    def handle_request_plane_params_message(self, message: RequestPlaneParamsMessage):
        pass
