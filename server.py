import sys,json

from twisted.web.static import File
from twisted.python import log
from twisted.web.server import Site
from twisted.internet import reactor,ssl

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol,listenWS

from autobahn.twisted.resource import WebSocketResource

from autobahn.websocket.types import ConnectionDeny
rooms = {}
User2Room = {}
Peer2Username ={}
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
        if 'roomID' not in request.params and 'password' not in request.params and 'username' not in request.params:
            raise ConnectionDeny(403, reason=unicode("roomID and password required"))
        roomID = request.params['roomID'][0]
        password = request.params['password'][0]
        requestType = request.params['requestType'][0]
        username = request.params['username'][0]
        if username in Peer2Username:
            raise ConnectionDeny(403, reason=unicode("Username already exist"))

        if requestType=='create':
            print roomID + " room created "
            if roomID not in rooms:
                rooms[roomID]= Room(roomID,password)

                User2Room[request.peer] = roomID
            else:
                raise ConnectionDeny(403, reason=unicode("Requested room already exist"))
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
        Peer2Username[request.peer] = username

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
        message = {'username':Peer2Username[client.peer],'msg':'joined','type':1}
        msg = (json.dumps(message))
        partners = room.getAllClients()
        for partner in partners:
            if client.peer != partner:
                partners[partner].sendMessage(msg)

    def unregister(self, client):
        try:
            rid = User2Room[client.peer]
            room = rooms[rid]
            message = {'username':Peer2Username[client.peer],'msg':'left','type':1}
            msg = (json.dumps(message))
            partners = room.getAllClients()
            for partner in partners:
                if client.peer != partner:
                    partners[partner].sendMessage(msg)
            
            rooms[rid].removeUser(client)
            User2Room.pop(client.peer)
            Peer2Username.pop(client.peer)
            if rooms[rid].numberOfClients()<=0:
                rooms.pop(rid)
        except:
            pass


    def communicate(self, client, payload, isBinary):
        rid = User2Room[client.peer]
        room = rooms[rid]
        message = {'username':Peer2Username[client.peer],'msg':payload,'type':0}
        msg = json.dumps(message)
        partners = room.getAllClients()
        if not partners:
            client.sendMessage("Sorry you dont have partner yet, check back in a minute")
        else:
            for partner in partners:
                if client.peer != partner:
                    partners[partner].sendMessage(msg)



if __name__ == "__main__":
    log.startLogging(sys.stdout)



    log.startLogging(sys.stdout)

    # SSL server context: load server key and certificate
    # We use this for both WS and Web!
    contextFactory = ssl.DefaultOpenSSLContextFactory('/etc/letsencrypt/live/sachinsingh.co.in/privkey.pem',
                                                      '/etc/letsencrypt/live/sachinsingh.co.in/fullchain.pem')

    factory = ChatRouletteFactory(u"wss://sachinsingh.co.in:81")
    # by default, allowedOrigins is "*" and will work fine out of the
    # box, but we can do better and be more-explicit about what we
    # allow. We are serving the Web content on 8080, but our WebSocket
    # listener is on 9000 so the Origin sent by the browser will be
    # from port 8080...


    factory.setProtocolOptions(maxFramePayloadSize=1048576,
                                     maxMessagePayloadSize=1048576,
                                     autoFragmentSize=65536,
                                     failByDrop=False,
                                     openHandshakeTimeout=20.5,
                                     closeHandshakeTimeout=10.,
                                     tcpNoDelay=True,
                                     autoPingInterval=10.,
                                     autoPingTimeout=5.,
                                     autoPingSize=4,
                                     # perMessageCompressionOffers=offers,
                                     # perMessageCompressionAccept=accept,
                                     allowedOrigins=[
                                         "https://sachinsngh165.github.io:443",
                                         "https://sachinsngh165.github.io:80",
                                         "https://sachinsingh.co.in:443",
                                         "https://35.229.213.23:443",
                                        "https://127.0.0.1:8080",
                                        "https://localhost:8080",
        ],)


    factory.protocol = SomeServerProtocol
    listenWS(factory,contextFactory)
    reactor.run()
