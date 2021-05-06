# pip install pyyaml
# pip install requests

import sys

from threading import Thread
from yaml import safe_load, YAMLError 

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

#from module_installmsi import InstallMSI
#from module_deletefile import DeleteFile
#from module_runprogram import RunProgram


def breakonerror(message):
    print(message)
    exit(1)


def executetasks(modules, play):
    tasklist = play['tasks']
    for task in tasklist:
        result = None
        print(f"---> {task['name'] if task['name'] else '<anonymous>'}:")

        if task.get('when', True):
            for modulekey in modules:
                if modulekey in task:
                    try:
                        parameters = task[modulekey]
                        module = modules[modulekey]
                        result = module.execute(parameters)
                    except Exception as exception:
                        breakonerror(f"     Error: {exception.message}.")
    
            if result is None:
                print(f"     Error: No module found for {task['name']}.")
#                breakonerror(f"     No module found for {task['name']}.")
    
            print(f"     Status: {result.status.name if result is not None else 'Unknown'}\n")
        else:
            print("     Status: Skipped\n")


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
        'addpath': AddToPath(),
        'download': DownloadFromUrl(),
        'firefox': DownloadWithFirefox()
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
    for play in playbook:
        print(f"-> {play['name'] if play['name'] else '<anonymous>'} ({len(play['tasks'])} tasks):")
        executetasks(modules, play)


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

