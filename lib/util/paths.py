from pathlib import Path

from exceptions import SytraException

class SytraPathError(SytraException):
    def __init__( self, filepath, errorstr='No such file or directory.'):
        self.filepath = filepath
        self.errorstr = errorstr

        super().__init__(filepath, errorstr)

    def __str__( self):
        s = '[SytraPathError] %s: \'%s\'' % (self.errorstr, str(self.filepath))
        return s

# super class for using abstract root directory
class SytraPath():
    # path based string like '/paht/to/rootdir'
    def __init__( self, rootdir: str):
        self._root = Path(rootdir)
        if not self._root.exists():
            raise SytraPathError(self._root)

    # provide relative-path, protected method
    def _get_filepath( self, *args, noerror=False)-> Path:
        path = self._root
        for arg in args: path = path / str(arg)
        try:
            path = path.resolve(strict=(not noerror))
        except FileNotFoundError:
            raise SytraPathError(path)

        return path
