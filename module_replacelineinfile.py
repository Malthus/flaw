
from os.path import exists, isfile, join

from module import Parameter, Status, Error, Module


class ReplaceLineInFile(Module):

    def __init__(self):
        super().__init__(
            name = "Replace line in file", 
            key = "replaceline",
            function = self.replacelineinfile,
            parameters = [
                Parameter('dir', required = True),
                Parameter('filename', required = True),
                Parameter('marker', required = True),
                Parameter('substitute', required = True),
                Parameter('targetname', required = False),
                Parameter('mode', required = False)
            ])


    def replacelineinfile(self, arguments):
        directory = arguments['dir']
        filename = arguments['filename']
        newfilename = arguments.get('targetname', filename)
        marker = arguments['marker']
        substitute = arguments['substitute']
        mode = arguments.get('mode', 'replace')
        sourcepath = join(directory, filename)
        targetpath = join(directory, newfilename)
        status = Status.OK
        
        if mode.lower() == "append":
            substitute = f"{marker}{substitute}"
        elif mode.lower() == "prepend":
            substitute = f"{substitute}{marker}"
        elif mode.lower() != "replace":
            return self.handleerror(Error.BadArgument, f"The mode '{mode}' it not recognized as a valid mode for this command, it should be 'replace', 'append', or 'prepend'.")

        if not exists(sourcepath) or not isfile(sourcepath):
            return self.handleerror(Error.MissingFile, f"The file {sourcepath} does not exist, so it cannot be modified.")

        sourcehandle = open(sourcepath, "r")
        sourcelines = sourcehandle.readlines()
        sourcehandle.close()
        
        targetlines = []
        for line in sourcelines:
            if marker in line:
                line = line.replace(marker, substitute)
                status = Status.Changed
            targetlines.append(line)

        targethandle = open(targetpath, "w")
        targethandle.writelines(targetlines)
        targethandle.close()

        return self.buildresult(status)

