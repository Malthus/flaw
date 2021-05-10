
from os import remove, scandir
from os.path import exists, isfile, join
from glob import glob

from flaw_library import createdirectory
from module import Parameter, Status, Error, Module


class DeleteFiles(Module):

    def __init__(self):
        super().__init__(
            name = "Delete one or more files", 
            key = "deletefile",
            function = self.deletefiles,
            parameters = [
                Parameter('dir', required = True),
                Parameter('filename', required = False),
                Parameter('recursive', required = False)
            ])


    def deletefiles(self, arguments):
        directory = arguments['dir']
        filename = arguments.get('filename', "*.*")
        recursive = arguments.get('recursive', False)

        if not exists(directory) or not isdir(directory):
            return self.buildresult(Status.OK)

        path = join(directory, filename)
        filenames = glob(path)
        
        if recursive:
            return self.deleterecursive(directory, filename)
        elif len(filenames) == 0:
            return self.buildresult(Status.OK)
        elif len(filenames) == 1:
            return self.deletesingle(directory, filenames[0])
        else:
            return self.deletemultiple(directory, filenames)


    def deleterecursive(self, directory, filename):
        subdirectories = [ file.name for file in os.scandir(directory) if file.is_dir() ]
        path = join(directory, filename)
        filenames = glob(path)
        status = Status.OK

        for subdirectory in subdirectories:
            subdirectory = join(directory, subdirectory)
            
            result = self.deleterecursive(subdirectory, filename)
            if result.status == Status.Error:
                return result
            elif result.status == Status.Changed:
                status = Status.Changed

        result = self.deletemultiple(directory, filenames)
        # Remove directory if empty?
        return result if result.status != Status.OK else self.buildresult(status)
    

    def deletemultiple(self, directory, filenames):
        status = Status.OK
    
        for filename in filenames:
            result = self.deletesingle(directory, filename)
            if result.status == Status.Error:
                return result
            elif result.status == Status.Changed:
                status = Status.Changed
    
        return self.buildresult(status)


    def deletesingle(self, directory, filename):
        filepath = join(directory, filename)
        if not exists(filepath) or not isfile(filepath):
            return self.buildresult(status)

        remove(filepath)
        if exists(filename):
            return self.handleerror(Error.FailedDeleteFile, f"Failed to delete the file {filepath}.")
        else:
            return self.buildresult(Status.Changed)

