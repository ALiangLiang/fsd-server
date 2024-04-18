from messages.IMessage import IMessage


class RegistrationInformationMessage(IMessage):
    command = '!R'

    def __init__(
        self,
        source: str,
        destination: str,
        signature: int,
        rating: int,
        admin_level: int,
        ip_address: str,
        protocol_version: str = 'B',
    ):
        super().__init__()
        self.source = source
        self.destination = destination
        self.signature = signature
        self.rating = rating
        self.admin_level = admin_level
        self.ip_address = ip_address
        self.protocol_version = protocol_version

    @staticmethod
    def parse_raw_message(raw_message):
        source, destination, protocol_version, signature_str, rating_str, admin_level_str, ip = raw_message[len(
            RegistrationInformationMessage.command):].split(':')
        return RegistrationInformationMessage(
            source,
            destination,
            int(signature_str),
            int(rating_str),
            int(admin_level_str),
            ip,
            protocol_version
        )

    def __str__(self):
        return self.command + ":".join([
            self.source,
            self.destination,
            self.protocol_version,
            str(self.signature),
            str(self.rating),
            str(self.admin_level),
            self.ip_address,
        ])

    @staticmethod
    def compute_signature(client_sig: int, vid: int, client_seed: int):
        num = 0
        str_vid = str(vid)
        for index, vid_char in enumerate(str_vid):
            if index % 2 == 0:
                num ^= num << ((client_sig + client_seed) %
                               17) ^ ord(vid_char) ^ num >> ((client_sig + client_seed) % 16)
            else:
                num ^= ~((num << ((client_sig + client_seed) % 21)) ^
                         ord(vid_char) ^ (num >> ((client_sig + client_seed) % 19)))
        return num & 0x7FFFFFFF  # Bitwise AND with 0x7FFFFFFF to ensure positive result

    def validate(self, client_sig: int, vid: int, client_seed: int):
        return self.signature == RegistrationInformationMessage.compute_signature(client_sig, vid, client_seed)
