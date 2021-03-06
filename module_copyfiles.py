
from os import remove, scandir
from os.path import basename, exists, isdir, isfile, join
from shutil import copy
from glob import glob

from flaw_library import createdirectory
from module import Parameter, Status, Error, Module


class CopyFiles(Module):

    def __init__(self):
        super().__init__(
            name = "Copy one or more files", 
            key = "copyfiles",
            function = self.copyfiles,
            parameters = [
                Parameter('sourcedir', required = True),
                Parameter('targetdir', required = True),
                Parameter('filename', required = False),
                Parameter('targetname', required = False),
                Parameter('mode', required = False),
                Parameter('overwrite', required = False),
                Parameter('recursive', required = False)
            ])


    def copyfiles(self, arguments):
        sourcedirectory = arguments['sourcedir']
        targetdirectory = arguments['targetdir']
        filename = arguments.get('filename', "*.*")
        newfilename = arguments.get('targetname', filename)
        mode = arguments.get('mode', 'copy')
        overwrite = arguments.get('overwrite', False)
        recursive = arguments.get('recursive', False)

        if not exists(sourcedirectory) or not isdir(sourcedirectory):
            return self.handleerror(Error.MissingDirectory, f"Failed to copy the file(s) from the directory {sourcedirectory}, because the directory does not exist.")
        elif recursive:
            return self.copyrecursive(sourcedirectory, targetdirectory, filename, mode, overwrite)
        else:
            return self.copynormal(sourcedirectory, targetdirectory, filename, newfilename, mode, overwrite)


    def copyrecursive(self, sourcedirectory, targetdirectory, filename, mode, overwrite):
        subdirectories = [ file.name for file in os.scandir(sourcedirectory) if file.is_dir() ]
        sourcemask = join(sourcedirectory, filename)
        sourcepaths = glob(sourcemask)
        status = Status.OK

        for subdirectory in subdirectories:
            sourcesubdirectory = join(sourcedirectory, subdirectory)
            targetsubdirectory = join(targetdirectory, subdirectory)
            
            if not exists(targetsubdirectory):
                createdirectory(targetsubdirectory)
                status = Status.Changed

            if not exists(targetsubdirectory):
                return self.handeerror(Error.FailedMakeDirectory, f"Failed to create the target directory {targetsubdirectory} for recursive file copy.")

            result = self.copyrecursive(sourcesubdirectory, targetsubdirectory, filename, mode, overwrite)
            if result.status == Status.Error:
                return result
            elif result.status == Status.Changed:
                status = Status.Changed
    
        result = self.copymultiple(sourcepaths, targetdirectory, mode, overwrite)
        return result if result.status != Status.OK else self.buildresult(status)
    

    def copynormal(self, sourcedirectory, targetdirectory, filename, newfilename, mode, overwrite):
        sourcemask = join(sourcedirectory, filename)
        sourcepaths = glob(sourcemask)
        
        if len(sourcepaths) == 0:
            return self.handleerror(Error.MissingFile, f"Failed to copy the file(s) {filename} from the directory {sourcedirectory}, because the files do not exist.")
        elif len(sourcepaths) == 1:
            return self.copysingle(sourcepaths[0], targetdirectory, newfilename, mode, overwrite)
        else:
            return self.copymultiple(sourcepaths, targetdirectory, mode, overwrite)


    def copymultiple(self, sourcepaths, targetdirectory, mode, overwrite):
        status = Status.OK
    
        for sourcepath in sourcepaths:
            filename = basename(sourcepath)
            result = self.copysingle(sourcepath, targetdirectory, filename, mode, overwrite)
            if result.status == Status.Error:
                return result
            elif result.status == Status.Changed:
                status = Status.Changed
    
        return self.buildresult(status)


    def copysingle(self, sourcepath, targetdirectory, newfilename, mode, overwrite):
        targetpath = join(targetdirectory, newfilename)
        status = Status.OK

        if not exists(sourcepath) or not isfile(sourcepath):
            return self.handleerror(Error.MissingDirectory, f"Failed to copy the file {sourcepath}, the file does not exist.")

        if not exists(targetdirectory):
            createdirectory(directory)
            status = Status.Changed

        if exists(targetpath) and not isfile(targetpath):
            return self.handleerror(Error.FailedCopyFile, f"Failed to copy the file {sourcepath} to {targetdirectory}, the same name already exists on the filesystem.")
        elif exists(targetpath) and overwrite:
            remove(targetpath)
            status = Status.Changed
        
        if not exists(targetpath):
            if mode == 'copy':
                copy(sourcepath, targetpath)
            elif mode == 'move':
                move(sourcepath, targetpath)
            else:
                self.handleerror(Error.BadArgument, f"The mode {mode} is not supported by this module.")
            status = Status.Changed

        if not exists(targetpath) or not isfile(targetpath):
            return self.handleerror(Error.FailedCopyFile, f"Failed to copy the file {sourcepath} to {targetdirectory}.")
        else:
            return self.buildresult(status)

