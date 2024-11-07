// Função para validar o formulário de login
function validateLogin(event) {
    // Impede o envio do formulário se não for válido
    event.preventDefault();

    // Obter os valores dos campos
    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;

    // Seleciona a mensagem de erro
    var errorMessage = document.getElementById('errorMessage');

    // Verifica se ambos os campos estão preenchidos
    if (email === "" || password === "") {
        // Exibe a mensagem de erro se algum campo estiver vazio
        errorMessage.style.display = "block";
        errorMessage.textContent = "Por favor, preencha todos os campos!";
    } else {
        // Caso contrário, a mensagem de erro é escondida
        errorMessage.style.display = "none";
        
        // Aqui você pode adicionar qualquer lógica de login (como chamar a API ou verificar no servidor)
        
        // Exemplo de sucesso:
        alert("Login realizado com sucesso!");

        // Se você estiver usando Flask, pode deixar o formulário enviar normalmente depois da validação
        document.querySelector('form').submit();
    }
}
