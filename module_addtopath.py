
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
    
        originalpath = self.getenvironment(regkey)
        if mode.lower() == "prepend":
            print('self.prependtopath(PATHKEY, directory)')
            self.prependtopath(self.PATHKEY, directory)
        elif mode.lower() == "append":
            print('self.apppendtopath(PATHKEY, directory)')
            self.apppendtopath(self.PATHKEY, directory)
        else:
            return self.handleerror(Error.BadArgument, f"The mode '{mode}' it not recognized as a valid mode for this command, it should be 'append' or 'prepend'.")

        newpath = self.getenvironment(regkey)
        if originalpath != newpath:
            status = Status.Changed

        return self.buildresult(status)


    def prependtopath(self, name, value):
        paths = self.getenvironment(name).split(';')
        self.removefrompath(paths, '')
        paths = self.getuniquepath(paths)
        self.removefrompath(paths, value)
        paths.insert(0, value)
        self.setenvironment(name, ';'.join(paths))


    def appendtopath(self, name, value):
        paths = self.getenvironment(name).split(';')
        self.removefrompath(paths, '')
        paths = self.getuniquepath(paths)
        self.removefrompath(paths, value)
        paths.append(value)
        self.setenvironment(name, ';'.join(paths))


    def removefrompath(self, paths, value):
        while value in paths:
            paths.remove(value)


    def getuniquepath(self, paths):
        uniquepaths = []
        for value in paths:
            if value not in uniquepaths:
                uniquepaths.append(value)
        return uniquepaths


    def setenvironment(self, name, value, user = True):
        root, subkey = getenvironmentkeys(user)
        key = OpenKey(root, subkey, 0, KEY_ALL_ACCESS)
        SetValueEx(key, name, 0, REG_EXPAND_SZ, value)
        CloseKey(key)
        SendMessage(HWND_BROADCAST, WM_SETTINGCHANGE, 0, subkey)


    def getenvironment(self, name, user = True):
        root, subkey = getenvironmentkeys(user)
        key = OpenKey(root, subkey, 0, KEY_READ)
        try:
            value, _ = QueryValueEx(key, name)
        except WindowsError:
            return ''
        return value


    def getenvironmentkeys(self, user = True):
        if user:
            root = HKEY_CURRENT_USER
            subkey = self.USERSUBKEY
        else:
            root = HKEY_LOCAL_MACHINE
            subkey = self.ROOTSUBKEY
        return root, subkey


    def convertdirectory(self, directory):
        return directory.replace("/", "\\")



#from os import system, environ
#import win32con
#from win32gui import SendMessage
#from _winreg import (
#    CloseKey, OpenKey, QueryValueEx, SetValueEx,
#    HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE,
#    KEY_ALL_ACCESS, KEY_READ, REG_EXPAND_SZ, REG_SZ
#)
#
#def prepend_env(name, values):
#    for value in values:
#        paths = get_env(name).split(';')
#        remove(paths, '')
#        paths = unique(paths)
#        remove(paths, value)
#        paths.insert(0, value)
#        set_env(name, ';'.join(paths))
#
#
#def prepend_env_pathext(values):
#    prepend_env('PathExt_User', values)
#    pathext = ';'.join([
#        get_env('PathExt_User'),
#        get_env('PathExt', user=False)
#    ])
#    set_env('PathExt', pathext)
#
#
#
#set_env('Home', '%HomeDrive%%HomePath%')
#set_env('Docs', '%HomeDrive%%HomePath%\docs')
#set_env('Prompt', '$P$_$G$S')
#
#prepend_env('Path', [
#    r'%SystemDrive%\cygwin\bin', # Add cygwin binaries to path
#    r'%HomeDrive%%HomePath%\bin', # shortcuts and 'pass-through' bat files
#    r'%HomeDrive%%HomePath%\docs\bin\mswin', # copies of standalone executables
#])
#
## allow running of these filetypes without having to type the extension
#prepend_env_pathext(['.lnk', '.exe.lnk', '.py'])
#