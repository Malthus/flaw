
from win32gui import SendMessage
from win32con import HWND_BROADCAST, WM_SETTINGCHANGE
from winreg import CloseKey, OpenKey, QueryValueEx, SetValueEx, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, KEY_ALL_ACCESS, KEY_READ, REG_EXPAND_SZ, REG_SZ
from os.path import exists, isdir

from module import Parameter, Status, Module


class AddToPath(Module):

    USERSUBKEY = "Environment"
    ROOTSUBKEY = "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    PATHKEY = "Path"

    def __init__(self):
        super().__init__(
            name = "Add directory to PATH environment", 
            key = "pathenv",
            function = self.addtopath,
            parameters = [
                Parameter('dir', required = True),
                Parameter('regkey', required = False),
                Parameter('forallusers', required = False),
                Parameter('mode', required = False)
            ])


    def addtopath(self, arguments):
        directory = self.convertdirectory(arguments['dir'])
        regkey = arguments.get('regkey', self.PATHKEY)
        forallusers = arguments.get('forallusers', False)
        mode = arguments.get('mode', 'prepend')
        status = Status.OK
    
        if not exists(directory):
            return self.handleerror(Error.MissingDirectory, f"The directory {directory} does not exist so it will not be added to the PATH.")
        elif not isdir(directory):
            return self.handleerror(Error.NoValidDirectory, f"The directory {directory} is not a valid directory so it will not be added to the PATH.")
    
        originalpath = self.getenvironment(regkey, forallusers)
        if mode.lower() == "prepend":
            self.prependtopath(self.PATHKEY, directory, forallusers)
        elif mode.lower() == "append":
            self.apppendtopath(self.PATHKEY, directory, forallusers)
        else:
            return self.handleerror(Error.BadArgument, f"The mode '{mode}' it not recognized as a valid mode for this command, it should be 'append' or 'prepend'.")

        newpath = self.getenvironment(regkey, forallusers)
        if originalpath != newpath:
            status = Status.Changed

        return self.buildresult(status)


    def prependtopath(self, name, value, forallusers = False):
        paths = self.getenvironment(name, forallusers).split(';')
        self.removefrompath(paths, '')
        paths = self.getuniquepath(paths)
        self.removefrompath(paths, value)
        paths.insert(0, value)
        self.setenvironment(name, ';'.join(paths), forallusers)


    def appendtopath(self, name, value, forallusers = False):
        paths = self.getenvironment(name, forallusers).split(';')
        self.removefrompath(paths, '')
        paths = self.getuniquepath(paths)
        self.removefrompath(paths, value)
        paths.append(value)
        self.setenvironment(name, ';'.join(paths), forallusers)


    def removefrompath(self, paths, value):
        while value in paths:
            paths.remove(value)


    def getuniquepath(self, paths):
        uniquepaths = []
        for value in paths:
            if value not in uniquepaths:
                uniquepaths.append(value)
        return uniquepaths


    def setenvironment(self, name, value, forallusers = False):
        root, subkey = self.getenvironmentkeys(forallusers)
        key = OpenKey(root, subkey, 0, KEY_ALL_ACCESS)
        SetValueEx(key, name, 0, REG_EXPAND_SZ, value)
        CloseKey(key)
        SendMessage(HWND_BROADCAST, WM_SETTINGCHANGE, 0, subkey)


    def getenvironment(self, name, forallusers = False):
        root, subkey = self.getenvironmentkeys(forallusers)
        key = OpenKey(root, subkey, 0, KEY_READ)
        try:
            value, _ = QueryValueEx(key, name)
        except WindowsError:
            return ''
        return value


    def getenvironmentkeys(self, forallusers = False):
        if forallusers:
            root = HKEY_LOCAL_MACHINE
            subkey = self.ROOTSUBKEY
        else:
            root = HKEY_CURRENT_USER
            subkey = self.USERSUBKEY
        return root, subkey


    def convertdirectory(self, directory):
        return directory.replace("/", "\\")

