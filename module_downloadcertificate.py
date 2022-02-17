
from ssl import get_server_certificate, PEM_cert_to_DER_cert
from os.path import exists, join

from module import Parameter, Status, Module


class DownloadCertificate(Module):

    def __init__(self):
        super().__init__(
            name = "Download SSL certificate", 
            key = "certificate",
            function = self.downloadcertificate,
            parameters = [
                Parameter('url', required = True),
                Parameter('port', required = False),
                Parameter('dir', required = False),
                Parameter('filename', required = False)
            ])

    def downloadcertificate(self, arguments):
        url = arguments['url']
        port = arguments.get('port', 443)
        directory = arguments.get('dir', '')
        filename = arguments.get('filename', 'certificate.cer')
        status = Status.OK
        certificatepath = join(directory, filename)

        if not exists(certificatepath):
            certificate = get_server_certificate((url, port))
#            with open(certificatepath, 'wb') as certificatefile:
#                certificatefile.write(PEM_cert_to_DER_cert(certificate))
            with open(certificatepath, 'w') as certificatefile:
                certificatefile.write(str(certificate))
            status = Status.Changed

        return self.buildresult(status)

