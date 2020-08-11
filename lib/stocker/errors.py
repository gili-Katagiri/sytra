class StockerError(Exception): pass

class StockPathError(StockerError):
    def __init__(self, filepath, errorstr='No such file or directory.'):
        self.filepath = filepath
        self.errorstr = errorstr

        super().__init__(filepath, filepath2, errorstr)

    def __str__(self):
        s = '[SytraPathError] %s: \'%s\'' % (self.errorstr, str(self.filepath))
        return s
