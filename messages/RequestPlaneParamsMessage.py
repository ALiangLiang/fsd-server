from messages.RequestPlaneInfoMessage import RequestPlaneInfoMessage


class RequestPlaneParamsMessage(RequestPlaneInfoMessage):
    command = '-MR'
