
from os.path import exists, isdir, join

from flaw_library import createdirectory
from module import Parameter, Status, Module


class MakeDirectory(Module):

    def __init__(self):
        super().__init__(
            name = "Make directory", 
            key = "mkdir",
            function = self.makedirectory,
            parameters = [
                Parameter('dir', required = True)
            ])


    def makedirectory(self, arguments):
        directory = arguments['dir']
        status = Status.OK

        if not exists(directory):
            status = Status.Changed
            createdirectory(directory)
        elif not isdir(directory):
            return self.handelerror(21, f"The directory {directory} cannot be created because a file with the same name already exists.")

        if not exists(directory):
            return self.handleerror(22, f"Failed to create the directory {directory}.")

        return self.buildresult(status)
