
class NexusFormatException(Exception):
    """Generic Exception for Nexus Format Errors"""
    pass


class TranslateTableException(NexusFormatException):
    """Exception for Translate table Errors"""
    pass
