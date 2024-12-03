document.addEventListener("DOMContentLoaded", function () {
    // Obtenha as mensagens do atributo de dados
    const messages = JSON.parse(document.body.dataset.messages || "[]");

    // Elemento para exibir as mensagens
    const messageBox = document.getElementById("messageBox");

    if (messages.length > 0) {
        messages.forEach(([category, text]) => {
            // Define estilos com base na categoria
            const colorClass = category === 'success'
                ? 'bg-green-100 text-green-700'
                : 'bg-red-100 text-red-700';

            messageBox.className = `block ${colorClass} p-4 mb-4 rounded-lg`;
            messageBox.textContent = text;

            // Remove mensagem após 5 segundos
            setTimeout(() => {
                messageBox.classList.add("hidden");
            }, 5000);
        });
    }
});
