async function connectToChat(event){
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
        console.log(ticket)
        return null;
    };
    var ws = new WebSocket(`ws://localhost:80/ws?ticket=${encodeURIComponent(ticket)}`);
    ws.onmessage = function(event){
        let messages = document.getElementById('chat_room');
        console.log(event.data);
        const data = event.data.split(' ');
        let message = document.createElement('div');
        message.classList.add('message');
        let user = document.createElement('p');
        user.classList.add('user')
        user.innerText = `Username : ${data[0]}`
        message.appendChild(user)
        let chatContent = document.createElement('p');
        chatContent.classList.add('text');
        chatContent.innerText = `Message : ${data[1]}`;
        message.appendChild(chatContent);
        messages.appendChild(message);
    };
    ws.onopen = function(){
        let chatContainer = document.getElementById('container');

        let chatGroups = document.createElement('div');
        chatGroups.setAttribute('id', 'groups');
        chatGroups.innerText = "Group : ";
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
        chatRoom.setAttribute('class', 'container');

        chatContainer.appendChild(chatGroups);
        chatContainer.appendChild(chatRoom);
        chatContainer.appendChild(chatInput);
        chatContainer.appendChild(chatSendBtn);
        };
    function sendMessage(){
        console.log("SEND IS IN USE");
        const textElem = document.getElementById("text_data");
        const name = document.getElementById("status").innerText;
        const group = document.getElementById('group_number').innerText;
        const header = 'msg';
        ws.send(`${header} ${group} ${name} ${textElem.value}`);
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
            alert(`[close] Connection closed, code=${event.code} reason=${event.reason}`);
        } else {
            alert('[close] Disconnected');
        };
    };
};