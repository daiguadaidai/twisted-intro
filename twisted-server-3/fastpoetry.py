# This is the Twisted Fast Poetry Server, version 2.0

from twisted.application import internet, service
from twisted.internet.protocol import ServerFactory, Protocol
from twisted.python import log


# configuration parameters, used below
port = 10000
iface = 'localhost'
poetry_file = 'poetry/ecstasy.txt'


# Normally we would import these classes from another module.

class PoetryProtocol(Protocol):

    def connectionMade(self):
        poem = self.factory.service.poem
        log.msg('sending %d bytes of poetry to %s'
                % (len(poem), self.transport.getPeer()))
        self.transport.write(poem)
        self.transport.loseConnection()


class PoetryFactory(ServerFactory):

    protocol = PoetryProtocol

    def __init__(self, service):
        self.service = service


class PoetryService(service.Service):

    def startService(self):
        self.poem = open(poetry_file).read()
        log.msg('loaded a poem from: %s' % (poetry_file,))


# this variable has to be named 'application'
application = service.Application("fastpoetry")

# this will hold the services that combine to form the poetry server
top_service = service.MultiService()

# the poetry service holds the poem
poetry_service = PoetryService()
poetry_service.setServiceParent(top_service)

# the tcp service connects the factory to the listening port
factory = PoetryFactory(poetry_service)
tcp_service = internet.TCPServer(port, factory, interface=iface)
tcp_service.setServiceParent(top_service)

# this hooks the collection we just made to the application
top_service.setServiceParent(application)

# at this point, the application is ready to go. when it is started by
# twistd, it will start the child services, thus starting up the
# poetry server
