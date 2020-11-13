
class SytraException(Exception):

    pass

class SytraDayError(SytraException):

    def __init__(self, ermes: str = ''):
        self.ermes = ermes
        super().__init__(ermes)
    def __str__(self):
        s = '[SytraDayError]' + self.ermes
        return s

class SytraPathError(SytraException):

    def __init__( self, filepath, ermes='No such file or directory.'):
        self.filepath = filepath
        self.ermes = ermes
        super().__init__(filepath, ermes)
    def __str__(self):
        s = '[SytraPathError] %s: \'%s\'' % (self.ermes, str(self.filepath))
        return s

class StockerError(SytraException):

    pass

class AnalyzerError(SytraException):

    pass

class StemError(AnalyzerError):

    pass
