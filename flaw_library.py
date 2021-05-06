

import ctypes
import pathlib


def checkrequiredparameters(parameters, keys):
    for key in keys:
        if key not in parameters:
            return False
    return True

def checkadministratorrole():
    adminrole = False
    try:
        adminrole = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        pass
    return adminrole


def createdirectory(directory):
    pathlib.Path(directory).mkdir(parents = True, exist_ok = True)



