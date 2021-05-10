
from shlex import split
from subprocess import run
from os import chdir
from os.path import exists, isdir

from module import Parameter, Status, Module


class ExecuteCommand(Module):

    def __init__(self):
        super().__init__(
            name = "Execute command", 
            key = "command",
            function = self.executecommand,
            parameters = [
                Parameter('command', required = True), 
                Parameter('shell', required = False), 
                Parameter('silent', required = False), 
                Parameter('chdir', required = False)
            ])


    def executecommand(self, arguments):
        shellcommand = arguments.get("shell", False)
        silentoperation = arguments.get("silent", False)
        directory = arguments.get('chdir', None)

        if directory is not None:
            if exists(directory) and isdir(directory):
                chdir(directory)
            else:
                return self.handleerror(Error.MissingDirectory, f"Failed to run the command in the directory {directory} because the directory does not exists.")

        result = run(split(arguments['command']), shell = shellcommand, capture_output = True, text = True)

        if not silentoperation:
            self.printdivider()
            self.printmessage(result.stdout)
            self.printmessage(result.stderr)
            self.printdivider()

        if result.returncode != 0:
            return self.handleerror(result.returncode, f"The command exited with return code {result.returncode}.")
        else:
            return self.buildresult(Status.Changed)

