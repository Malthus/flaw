
from subprocess import run
from os import chdir
from os.path import exists, isdir

from module import Parameter, Status, Module


class RunGitBashCommand(Module):

    GITBASHEXECUTABLE = "C:/Program Files/Git/git-bash.exe"

    def __init__(self):
        super().__init__(
            name = "Run Git Bash command", 
            key = "gitbash",
            function = self.rungitbashcommand,
            parameters = [
                Parameter('command', required = True), 
                Parameter('executable', required = False), 
                Parameter('silent', required = False),
                Parameter('chdir', required = False)
            ])


    def rungitbashcommand(self, arguments):
        gitbashcommand = arguments.get("command", False)
        gitbashexecutable = arguments.get("executable", self.GITBASHEXECUTABLE)
        directory = arguments.get('chdir', None)
        silentoperation = arguments.get('silent', False)

        if directory is not None:
            if exists(directory) and isdir(directory):
                chdir(directory)
            else:
                return self.handleerror(Error.MissingDirectory, f"Failed to run the command in the directory {directory} because the directory does not exists.")

        result = run([gitbashexecutable, "", arguments['gitbashcommand']), capture_output = True, text = True)

        if not silentoperation:
            self.printdivider()
            self.printmessage(result.stdout)
            self.printmessage(result.stderr)
            self.printdivider()

        if result.returncode != 0:
            return self.handleerror(result.returncode, f"The command exited with return code {result.returncode}.")
        else:
            return self.buildresult(Status.Changed)

