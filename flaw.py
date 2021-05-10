# pip install pyyaml
# pip install requests

import sys

from threading import Thread
from yaml import safe_load, YAMLError 
from datetime import datetime

from flaw_library import checkadministratorrole
from module import Status, Result
from module_executecommand import ExecuteCommand
from module_copyfiles import CopyFiles
from module_deletefiles import DeleteFiles
from module_replacelineinfile import ReplaceLineInFile
from module_makedirectory import MakeDirectory
from module_createshortcut import CreateShortcut
from module_addtopath import AddToPath
from module_downloadfromurl import DownloadFromUrl
from module_downloadwithfirefox import DownloadWithFirefox
from module_checkrunasadmin import CheckRunAsAdmin
from module_keyboardinput import KeyboardInput
from module_showinformation import ShowInformation

#from module_installmsi import InstallMSI
#from module_deletefile import DeleteFile
#from module_runprogram import RunProgram


class Player(object):

    def __init__(self, modules):
        self.modules = modules


    def execute(self, play):
        print(f"-> {play['name'] if play['name'] else '<anonymous>'} ({len(play['tasks'])} tasks):")
        variables = self.parsevariables(play)
        self.runtasks(play, variables)

    
    def parsevariables(self, play):
        variables = {}
        for key in play.get('vars', {}):
            variables[key] = play['vars'][key]
        return variables


    def runtasks(self, play, variables):
        for taskmodel in play.get('tasks', []):
            task = self.preparetask(taskmodel, variables)
            result = self.runtask(task, variables)
            variables = self.mergetask(result, variables)


    def preparetask(self, taskmodel, variables):
        task = self.replaceindictionary(taskmodel, variables)
        print(f"---> {task['name'] if task['name'] else '<anonymous>'}:")
        return task

    
    def runtask(self, task, variables):
        result = None

        if task.get('when', True):
            modulekey = self.findmodule(modules, task)
            if modulekey is not None:
                try:
                    parameters = task[modulekey]
                    module = modules[modulekey]
                    result = module.execute(parameters)
                except Exception as exception:
                    breakonerror(f"     Error: {exception.message}.")
            else:
                breakonerror(f"     No module found for {task['name']}.")
        else:
            result = Result(Status.Skipped, 0, datetime.now(), datetime.now())

        return result


    def mergetask(self, result, variables):
        payload = result.payload
        
        newvariables = payload.get('variables', {})
        for key in newvariables:
            variables[key] = newvariables[key]

        print(f"     Status: {result.status.name if result is not None else 'Unknown'}\n")
        return variables


    def replaceindictionary(self, originalvalue, variables):
        newvalue = {}
        for key in originalvalue:
            originalelement = originalvalue[key]
            if isinstance(originalelement, dict):
                newelement = self.replaceindictionary(originalelement, variables)
            elif isinstance(originalelement, str) and "{{" in originalelement:
                newelement = self.replaceinstring(originalelement, variables)
            else:
                newelement = originalelement
            newvalue[key] = newelement
        return newvalue


    def replaceinstring(self, originalvalue, variables):
        startindex = originalvalue.find("{{") + 2
        endindex = originalvalue.find("}}", startindex)
        variable = originalvalue[startindex:endindex].strip()
        value = variables if variable == '*' else variables[variable]
        newvalue = originalvalue[:startindex - 2] + value + originalvalue[endindex + 2:]
        return newvalue


    def findmodule(self, modules, task):
        for key in modules:
            if key in task:
                return key
    
        return None


def breakonerror(message):
    print(message)
    exit(1)


def parsecommandline(arguments):
    if arguments is not None and len(arguments) >= 2:
        return arguments[1]

def loadmodules():
    return {
        'command': ExecuteCommand(),
        'copyfiles': CopyFiles(),
        'deletefiles': DeleteFiles(),
        'replaceline': ReplaceLineInFile(),
        'mkdir': MakeDirectory(),
        'shortcut': CreateShortcut(),
        'pathenv': AddToPath(),
        'download': DownloadFromUrl(),
        'firefox': DownloadWithFirefox(),
        'checkadmin': CheckRunAsAdmin(),
        'input': KeyboardInput(),
        'info': ShowInformation()
#        'install': InstallMSI(),
#        'program': RunProgram(),
        } 

def readplaybook(playbookfile):
    with open(playbookfile, 'r') as playbookcontents:
        try:
            return safe_load(playbookcontents)
        except yaml.YAMLError as exception:
            print(exception)
            return None

def executeplaybook(modules, playbook):
    player = Player(modules)
    for play in playbook:
        player.execute(play)


# Start script and load modules
print("Flaw - Fake Local Ansible / Windows")
modules = loadmodules()

# Parse command line arguments
playbookfile = parsecommandline(sys.argv)
if playbookfile is None:
    breakonerror("A playbookfile is missing from the command line.")

# Check administrator role
#if not checkadministratorrole():
#    breakonerror("Flaw needs to run with administrator-privileges")

# Read yaml file
print(f"\nReading playbook from file {playbookfile}.")
playbook = readplaybook(playbookfile)
if playbook is None:
    breakonerror(f"Error reading the playbook file {playbookfile}.")
elif len(playbook) == 0:
    breakonerror(f"The playbook file {playbookfile} does not contain any plays.")

# Run playbook
print(f"\nExecuting {len(playbook)} plays from playbook file {playbookfile}.")
executeplaybook(modules, playbook)

# Close script
print("\nDone")

