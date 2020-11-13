from pathlib import Path

from exceptions import SytraPathError

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
        path = path.resolve()
        if not (noerror or path.exists()):
            raise SytraPathError(path)

        return path
