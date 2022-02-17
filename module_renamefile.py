
from os import rename
from os.path import exists, join

from flaw_library import createdirectory
from module import Parameter, Status, Error, Module


class RenameFile(Module):

    def __init__(self):
        super().__init__(
            name = "Rename one file or directory", 
            key = "renamefile",
            function = self.renamefile,
            parameters = [
                Parameter('dir', required = False),
                Parameter('filename', required = True),
                Parameter('targetname', required = True)
            ])


    def renamefile(self, arguments):
        directory = arguments.get('dir', '')
        filename = arguments['filename']
        targetname = arguments['targetname']

        filepath = join(directory, filename)
        targetpath = join(directory, targetname)
        
        if not exists(filepath):
            return self.buildresult(Status.OK)

        if exists(targetpath):
            return self.buildresult(Status.OK)

        rename(filepath, targetpath)
        return self.buildresult(Status.Changed)

