
from getpass import getpass

from module import Parameter, Status, Error, Module


class KeyboardInput(Module):

    def __init__(self):
        super().__init__(
            name = "Keyboard input", 
            key = "input",
            function = self.getkeyboardinput,
            parameters = [
                Parameter('name', required = True),
                Parameter('prompt', required = False),
                Parameter('default', required = False),
                Parameter('password', required = False),
                Parameter('optional', required = False)
            ])


    def getkeyboardinput(self, arguments):
        name = arguments['name']
        baseprompt = arguments.get('prompt', f"Enter {name}")
        defaultvalue = arguments.get('default', None)
        ispassword = arguments.get('password', False)
        isoptional = arguments.get('optional', False)
        prompt = f"{baseprompt} ({defaultvalue}): " if defaultvalue is not None and not ispassword else f"{baseprompt}: "
        inputvalue = None

        self.printdivider()
        loop = True
        while loop:
            if ispassword:
                inputvalue = getpass(prompt = prompt)
            else:
                print(prompt)
                inputvalue = input().rstrip()

            if defaultvalue is not None and (inputvalue is None or inputvalue == ""):
                inputvalue = defaultvalue

            loop = (inputvalue is None or inputvalue == "") and not isoptional
        self.printdivider()

        return self.buildresult(Status.OK, payload = {'variables': {name: inputvalue}})

