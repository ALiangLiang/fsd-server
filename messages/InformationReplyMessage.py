from messages.InformationRequestMessage import InformationRequestMessage


class InformationReplyMessage(InformationRequestMessage):
    command = '$CR'
