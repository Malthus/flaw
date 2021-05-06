
#from win32com.client import Dispatch

from pythoncom import CoCreateInstance, CLSCTX_INPROC_SERVER, IID_IPersistFile
from win32com.shell import shell, shellcon
from os.path import exists

from module import Parameter, Status, Module


class CreateShortcut(Module):

    def __init__(self):
        super().__init__(
            name = "Create shortcut", 
            key = "shortcut",
            function = self.createshortcut,
            parameters = [
                Parameter('command', required = True), 
                Parameter('name', required = True), 
                Parameter('targetdir', required = True), 
                Parameter('icon', required = False)
            ])


    def createshortcut(self, parameters):
        command = arguments['command']
        name = arguments['name']
        targetdir = arguments['targetdir']
        shortcutpath = join(targetdir, f"{name}.lnk")
        icon = arguments.get('icon', None)
        description = None
        directory = None
        runasadmin = False
        status = Status.OK

        if not exists(shortcutpath):
            self.createlink(path, command, icon, description, directory, runasadmin)
            status = Status.Changed

        return self.buildresult(status)


    def createlink(self, shortcutpath, command, icon, description, directory, runasadmin):
        shortcut = CoCreateInstance(shell.CLSID_ShellLink, None, CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
        shortcut.SetPath(command)
        
        if icon is not None:
            shortcut.SetIconLocation(icon, 0)
        
        if description is not None:
            shortcut.SetDescription(description)

        if directory is not None:
            shortcut.SetWorkingDirectory(directory)

        if runasadmin:
            linkdata = shortcut.QueryInterface(shell.IID_IShellLinkDataList)
            linkdata.SetFlags(linkdata.GetFlags() | shellcon.SLDF_RUNAS_USER)

        file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
        file.Save(shortcutpath, 0)

#            shell = Dispatch("WScript.Shell")
#            shortcut = shell.CreateShortCut(path)
#            shortcut.Targetpath = command
#            shortcut.IconLocation = icon
#            shortcut.WindowStyle = 1
#            shortcut.save()

