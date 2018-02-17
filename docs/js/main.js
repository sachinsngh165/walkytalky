var createButton = document.getElementById('create')
var enterButton = document.getElementById('enter')

createButton.onclick = createRoom;
enterButton.onclick = enterRoom;
document.getElementById("send").onclick = sendMessage;

var sendButton = document.getElementById('send');
sendButton.onclick = sendMessage

var message = document.getElementById('message');
message.onkeyup= sendMessageKeyPress;



function sendMessage(){
        console.log('send Message called')
        var text = document.getElementById('message').value
        if (text !== "" && window.mySocket.readyState===1){
            mySocket.send(text)
            insertChat("me", text);              
            document.getElementById('message').value= ''
        }
};


function sendMessageKeyPress(e){
    if (e.which == 13){
        sendMessage()
    }
}

function createRoom()
{
    var roomId = document.getElementById('roomId').value
    var password = document.getElementById('password').value
    connectToServer("ws://localhost:8080/ws",roomId,password,'create');

        // Connection opened
    window.mySocket.addEventListener('open', function (event) {
        document.getElementById('response').innerText = "Room successfully created! ";
        window.mySocket.onmessage = function (event) {
            insertChat("other: ",event.data)
                        };
    });

    // Connetion closed
    window.mySocket.addEventListener('close',function(event){
        document.getElementById('response').innerText = "Room ID already exist";
    });
    
}

function enterRoom()
{
    var roomId = document.getElementById('roomId').value;
    var password = document.getElementById('password').value;
    connectToServer("ws://localhost:8080/ws",roomId,password,'enter');

    // Connection opened
    window.mySocket.addEventListener('open', function (event) {
        document.getElementById('response').innerText = "Success ";
        window.mySocket.onmessage = function (event) {
            insertChat("other: ",event.data)
                        };
    });

    // Connetion closed
    window.mySocket.addEventListener('close',function(event){
        document.getElementById('response').innerText = "Room ID or Password is wrong/ Room ID not exist"
    })
}


function connectToServer(host,roomID,password,type,currentStatus)
{
    window.mySocket = new WebSocket(host+'?'+"roomID="+roomID+'&'+"password="+password+'&'+'requestType='+type);
}


function formatAMPM(date) {
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0'+minutes : minutes;
    var strTime = hours + ':' + minutes + ' ' + ampm;
    return strTime;
}            

function insertChat(who, text){
    if(who=="me")
        text = "You:   ";
    console.log("called")
    var control = "";
    var date = formatAMPM(new Date());

    var entry = document.createElement('li');
    entry.appendChild(document.createTextNode(text));
    var list = document.getElementById('output');
    list.appendChild(entry);
    
}
  