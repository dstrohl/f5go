import logging

log = logging.getLogger('go')

def log_error(error, message):
    tmp_ret = error(message)
    log.exception(str(error))
    return tmp_ret

class Error(Exception):
    """base error exception class for go, never raised"""
    def __init__(self, message):
        log.exception(self, message)
        super(Error, self).__init__(message)


class InvalidKeyword(Error):
    """Error raised when a keyword fails the sanity check"""
    pass

class InsecureConfig(Error):
    """Error raised when a configu is not secure and the system started without the allowInsecure flag"""
    pass

class MissingKeys(Error):
    """Error raised when a configu is missing keys"""
    pass

class TemplateError(Error):
    """Error raised when a template is invalid"""
    pass