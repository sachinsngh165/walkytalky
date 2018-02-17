import sys

from twisted.web.static import File
from twisted.python import log
from twisted.web.server import Site
from twisted.internet import reactor

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol

from autobahn.twisted.resource import WebSocketResource

from autobahn.websocket.types import ConnectionDeny
rooms = {}
User2Room = {}

class Room():
    def __init__(self,roomId,password):
        self.roomId = roomId
        self.password = password
        self.Clients = {}

    def addUser(self,client):
        print client.peer + " added "
        self.Clients[client.peer]=client

    def removeUser(self,client):
        try:
            self.Clients.pop(client.peer)
            print client.peer + " removed from room "
        except:
            pass
        
    def authenticate(self,password):
        if self.password==password:
            return True
        return False

    def isExist(self,clientId):
        if clientId in self.Clients:
            return True
        return False

    def numberOfClients(self):
        return len(self.Clients)

    def getAllClients(self):
        return self.Clients

class SomeServerProtocol(WebSocketServerProtocol):


    def onConnect(self, request):
        print request.params
        if 'roomID' not in request.params and 'password' not in request.params:
            raise ConnectionDeny(403, reason=unicode("roomID and password required"))
        roomID = request.params['roomID'][0]
        password = request.params['password'][0]
        requestType = request.params['requestType'][0]
        if requestType=='create':
            print roomID + " room created "
            if roomID not in rooms:
                rooms[roomID]= Room(roomID,password)
                room = rooms[roomID]
                User2Room[request.peer] = roomID
            else:
                raise ConnectionDeny(403, reason=unicode("Requested already exist"))
        elif requestType=='enter':
            if roomID not in rooms:
                raise ConnectionDeny(403, reason=unicode("No such room exist "))
            else:
                if rooms[roomID].authenticate(password):
                    User2Room[request.peer] = roomID
                else:
                    raise ConnectionDeny(403,reason=unicode("Bad request"))

        else :
            raise ConnectionDeny(403,reason=unicode("Bad request"))

    def onOpen(self):
        self.factory.register(self)
        print "Connection is opened"

    def connectionLost(self, reason):
        print "Connect is closed"
        self.factory.unregister(self)

    def onMessage(self, payload, isBinary):
        self.factory.communicate(self, payload, isBinary)



class ChatRouletteFactory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        super(ChatRouletteFactory, self).__init__(*args, **kwargs)

    def register(self,client):
        rid = User2Room[client.peer]
        room = rooms[rid]
        room.addUser(client)

    def unregister(self, client):
        try:
            rid = User2Room[client.peer]
            rooms[rid].removeUser(client.peer)
            User2Room.pop(client.peer)
            if rooms[rid].numberOfClients <=0:
                rooms.pop(rid)
        except:
            pass


    def communicate(self, client, payload, isBinary):
        rid = User2Room[client.peer]
        room = rooms[rid]
        partners = room.getAllClients()
        if not partners:
            client.sendMessage("Sorry you dont have partner yet, check back in a minute")
        else:
            for partner in partners:
                if client.peer != partner:
                    partners[partner].sendMessage(str(client.peer) + " : "+ payload)



if __name__ == "__main__":
    log.startLogging(sys.stdout)

    # static file server seving index.html as root
    root = File(".")

    factory = ChatRouletteFactory(u"ws://127.0.0.1:8080")
    factory.protocol = SomeServerProtocol
    resource = WebSocketResource(factory)
    # websockets resource on "/ws" path
    root.putChild(u"ws", resource)

    site = Site(root)
    reactor.listenTCP(8080, site)
    reactor.run()