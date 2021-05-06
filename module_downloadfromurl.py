
from os.path import exists, isdir, join
from requests import get

from flaw_library import createdirectory
from module import Parameter, Status, Error, Module


class DownloadFromUrl(Module):

    BLOCKSIZE = 65536

    def __init__(self):
        super().__init__(
            name = "Download file from url", 
            key = "download",
            function = self.downloadfromurl,
            parameters = [
                Parameter('url', required = True), 
                Parameter('targetdir', required = True), 
                Parameter('filename', required = True)
            ])


    def downloadfromurl(self, parameters):
        directory = parameters['targetdir']
        filename = join(directory, parameters['filename'])
        url = parameters['url']
        status = Status.OK

        if not exists(directory):
            status = Status.Changed
            createdirectory(directory)

        if not exists(directory) or not isdir(directory):
            return self.handelerror(Error.DuplicateDirectory, f"The directory {directory} cannot be created because a file with the same name already exists.")

        if not exists(filename):
            status = Status.Changed
            self.downloadfile(url, filename)

        if not exists(filename):
            return self.handleerror(Error.FailedDownloadFile, f"Failed to download the file, the file is missing from the filesystem.")

        return self.buildresult(status)

    
    def downloadfile(self, url, filename):
        request = get(url)
        targetfile = open(filename, 'wb')
        for chunk in request.iter_content(self.BLOCKSIZE):
            targetfile.write(chunk)
        targetfile.close()    

