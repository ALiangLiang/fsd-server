from messages.IMessage import IMessage


class ClientVerificationMessage(IMessage):
    command = '!C'

    def __init__(
        self,
        source: str,
        destination: str,
        seed: int,
        client_signature: str | None = None,
        software_name: str = 'Aurora/win',
        software_version: str = '1.2.21b',
        software_key: str = '',
    ):
        super().__init__()
        self.source = source
        self.destination = destination
        self.client_signature = client_signature
        self.software_name = software_name
        self.software_version = software_version
        self.software_key = software_key
        self.seed = seed

    @property
    def signature(self):
        return ClientVerificationMessage.compute_signature(self.software_key, int(self.seed))

    @staticmethod
    def parse_raw_message(raw_message):
        source, destination, _, client_signature, software_name, software_version, seed_str = raw_message[len(
            ClientVerificationMessage.command):].split(':')
        return ClientVerificationMessage(
            source,
            destination,
            int(seed_str),
            client_signature,
            software_name,
            software_version,
        )

    def __str__(self):
        return self.command + ":".join([
            self.source,
            self.destination,
            self.client_signature,
            self.software_name,
            self.software_version,
            str(self.seed),
        ])

    @staticmethod
    def compute_signature(software_key: str, server_seed: int):
        num = 0
        for index, key_char in enumerate(software_key):
            if index % 2 == 0:
                num ^= num << (server_seed % 23) ^ ord(
                    key_char) ^ num >> (server_seed % 19)
            else:
                num ^= ~((num << (server_seed % 26)) ^ ord(
                    key_char) ^ (num >> (server_seed % 24)))
        return num & 0x7FFFFFFF  # Bitwise AND with 0x7FFFFFFF to ensure positive result

    def validate(self, software_key: str, server_seed: int):
        return self.signature == ClientVerificationMessage.compute_signature(software_key, server_seed)
