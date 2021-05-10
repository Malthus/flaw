
from getpass import getpass

from module import Parameter, Status, Error, Module


class ShowInformation(Module):

    def __init__(self):
        super().__init__(
            name = "Show information", 
            key = "info",
            function = self.showinformation,
            parameters = [
                Parameter('mode', required = True),
                Parameter('variable', required = True)
            ])


    def showinformation(self, arguments):
        mode = arguments['mode']
        variable = arguments['variable']

        self.printdivider()
        print(variable)
        self.printdivider()

        return self.buildresult(Status.OK)

