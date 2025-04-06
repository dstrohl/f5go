
class Error(Exception):
    """base error exception class for go, never raised"""
    pass


class InvalidKeyword(Error):
    """Error raised when a keyword fails the sanity check"""
    pass

class InsecureConfig(Error):
    """Error raised when a configu is not secure and the system started without the allowInsecure flag"""
    pass

def MissingKeys(Error):
    """Error raised when a configu is missing keys"""
    pass

def TemplateError(Error):
    """Error raised when a template is invalid"""
    pass