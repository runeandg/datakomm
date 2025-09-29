# --- Errors --- 

class ProtocolError(Exception):
    """Base class for protocol-level errors"""

class UnknownCommandError(ProtocolError):
    """Raised when a command is not valid"""

class InvalidArgumentError(ProtocolError):
    """Raised when args are missing or wrong type"""

