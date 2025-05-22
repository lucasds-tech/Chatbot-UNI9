function addMessage(sender, text) {
    const msg = document.createElement('div');
    msg.className = 'item';
    if (sender === 'user') msg.classList.add('right');

    const msgText = document.createElement('div');
    msgText.className = 'msg';
    msgText.innerText = text;

    if (sender === 'bot') {
        const icon = document.createElement('div');
        icon.className = 'icon';
        const img = document.createElement('img');
        img.src = '/uninoveProject/assets/images/icon.png';
        img.alt = 'icon';
        icon.appendChild(img);
        msg.appendChild(icon);
    }

    msg.appendChild(msgText);
    document.getElementById('messages').appendChild(msg);

    // Scroll automático para a última mensagem
    const messages = document.getElementById('messages');
    messages.scrollTop = messages.scrollHeight;
}

// Envia a mensagem para o backend e trata a resposta
async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    if (!message) return;

    addMessage('user', message);
    input.value = '';

    try {
        const res = await fetch('http://localhost:5000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        if (!res.ok) throw new Error('Erro na resposta do servidor');

        const data = await res.json();
        addMessage('bot', data.reply);
    } catch (error) {
        addMessage('bot', 'Erro ao se comunicar com o servidor. Tente novamente mais tarde.');
        console.error(error);
    }
}

// Eventos de clique e tecla enter para enviar mensagem
document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById('userInput');
    const btn = document.getElementById('sendBtn');

    btn.addEventListener('click', sendMessage);

    input.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });
});