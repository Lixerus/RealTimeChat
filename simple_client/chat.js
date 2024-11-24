async function connectToChat(){
    async function getTicket(){
        const Url = "http://localhost:8000/ticket";
        const token = localStorage.getItem("access_token");
        if (!token){
            alert("You need to log in");
            return null;
        };
        const header = new Headers({"authorization" : `Bearer ${token}`, 'Accept': 'application/json', credentials:true});
        response = await fetch(
            url=Url,
            {headers : header, credentials:"include", method:"POST"}
        );

        const status = response.status;
        if (status === 201){
            const data = await response.json();
            const ticket = data.ticket
            return ticket;
        }
        else if (status === 400){
            alert("Bad request");
        }
        else if (status === 401){
            alert("Invalid account data. Try to relogin");
        }
        return null;

    };
    const ticket = await getTicket();
    if (!ticket){
        return null;
    };
    var ws = new WebSocket(`ws://localhost:80/ws?ticket=${encodeURIComponent(ticket)}`);
    function setupConnectBtn(){
        let container = document.getElementById('container');
        container.replaceChildren();
        let connectButton = document.createElement('button');
        connectButton.setAttribute('id', 'ws_button');
        connectButton.addEventListener('click', connectToChat);
        connectButton.innerText = 'Connect to chatroom';
        container.replaceChildren(connectButton);
    };
    function setupDisconnectBtn(){
        let connectButton = document.getElementById('ws_button');
        connectButton.removeEventListener('click', connectToChat)
        connectButton.addEventListener('click', () => {ws.close();setupConnectBtn();});
        connectButton.innerText = 'Disconnect';
    };
    setupDisconnectBtn();

    function showMessage(msg){
        const data = msg.split(' ');
        let messages = document.getElementById('chat_room');
        let message = document.createElement('div');
        message.classList.add('message');
        let user = document.createElement('p');
        user.classList.add('user')
        user.innerText = `Username : ${data[0]}`
        message.appendChild(user)
        let chatContent = document.createElement('p');
        chatContent.classList.add('text');
        chatContent.innerText = `Message : ${data.slice(1).join(' ')}`;
        message.appendChild(chatContent);
        messages.appendChild(message);
    };

    ws.onmessage = function(event){
        console.log(event.data);
        if (event.data[0] === '['){
            let allMsgs = event.data.slice(2,-2);
            const msgList = allMsgs.split('","');
            msgList.forEach(element => {
                showMessage(element);
            });
        }
        else {
        showMessage(event.data);
        };
    };
    ws.onopen = function(){
        let chatContainer = document.getElementById('container');

        let chatGroups = document.createElement('div');
        chatGroups.setAttribute('id', 'groups');
        chatGroups.setAttribute('class', 'groups-bar')
        chatGroups.innerText = "Group :";
        let groupNumber = document.createElement('b');
        groupNumber.setAttribute('id', 'group_number');
        groupNumber.innerText = 'null';
        chatGroups.appendChild(groupNumber);
        let groupBtn1 = document.createElement('button');
        groupBtn1.innerText = "Group 1";
        groupBtn1.addEventListener('click', () => sendGroup(1));
        chatGroups.appendChild(groupBtn1);
        let groupBtn2 = document.createElement('button');
        groupBtn2.innerText = "Group 2";
        groupBtn2.addEventListener('click', () => sendGroup(2));
        chatGroups.appendChild(groupBtn2);
        let groupBtn3 = document.createElement('button');
        groupBtn3.innerText = "Group 3";
        groupBtn3.addEventListener('click', () => sendGroup(3));
        chatGroups.appendChild(groupBtn3);
        let groupBtn4 = document.createElement('button');
        groupBtn4.innerText = "Group 4";
        groupBtn4.addEventListener('click', () => sendGroup(4));
        chatGroups.appendChild(groupBtn4);
        let groupBtn5 = document.createElement('button');
        groupBtn5.innerText = "Group 5";
        groupBtn5.addEventListener('click', () => sendGroup(5));
        chatGroups.appendChild(groupBtn5);

        let chatInput = document.createElement('textarea');
        chatInput.setAttribute('id', "text_data")
        chatInput.setAttribute('type', 'text');
        let chatSendBtn = document.createElement("button");
        chatSendBtn.setAttribute("id", "sendText");
        chatSendBtn.innerText = "Send Text";
        chatSendBtn.addEventListener('click', sendMessage);

        let chatRoom = document.createElement('div');
        chatRoom.setAttribute('id', 'chat_room');
        chatRoom.setAttribute('class', 'chat-room');

        chatContainer.appendChild(chatGroups);
        chatContainer.appendChild(chatRoom);
        chatContainer.appendChild(chatInput);
        chatContainer.appendChild(chatSendBtn);
        };
    function sendMessage(){
        const textElem = document.getElementById("text_data");
        const name = document.getElementById("status").innerText;
        const group = document.getElementById('group_number').innerText;
        const header = 'msg';
        ws.send(`${header} ${group} ${name} ${textElem.value.trim()}`);
        textElem.value = '';
        };
    function sendGroup(newGroupNumber){
        let groupNumber = document.getElementById("group_number");
        const currentGroup = groupNumber.innerText;
        const header = 'grp';
        const newGroup = `group${newGroupNumber}`;
        groupNumber.innerText = newGroup;
        ws.send(`${header} ${currentGroup} ${newGroup}`);
        let chatMsgs = document.getElementById("chat_room");
        chatMsgs.innerText = '';
    };
    ws.onerror = function(event){
        alert("Error. Connection may be lost")
    }
    ws.onclose = function(event){
        if (event.wasClean) {
            alert(`Connection closed, code=${event.code} reason=${event.reason}`);
        } else {
            alert('Disconnected');
        };
    };
};