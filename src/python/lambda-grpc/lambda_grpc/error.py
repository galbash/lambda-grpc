class RPCError(Exception):
    """
    A base error for all server errors
    """
    def __init__(self, code, message):
        super(RPCError, self).__init__(message)
        self.code = code
        self.message = message


class RPCWarning(Warning):
    """
    A base class for all warnings
    """
    pass
