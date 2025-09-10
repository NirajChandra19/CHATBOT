function sendmessage() {
    const inputElement = document.getElementById("input");
    const message = inputElement.value.trim();
    const chatbot = document.getElementById("output");
    const chatBody = document.getElementById("chat-body");

    if (message === "") return;

    const userMsg = document.createElement("div");
    userMsg.className = "user-message";
    userMsg.innerText = message;

    document.getElementById("chat-body").appendChild(userMsg);
    inputElement.value = "";

    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })  
    })
    .then(response => response.json())  
    .then(data => {
        console.log("Server response:", data);  
        const botMsg = document.createElement("div");
        botMsg.className = "bot-message";
        botMsg.innerText =  data.response;
        document.getElementById("chat-body").appendChild(botMsg);
        document.getElementById("chat-body").scrollTop = document.getElementById("chat-body").scrollHeight;  
    })
    .catch(error => {
        console.error("Fetch error:", error);
    });
}
