document.addEventListener("DOMContentLoaded", function() {
    let chat = document.querySelector("#chat");
let input = document.querySelector("#input");
let botao_enviar = document.querySelector("#botao-enviar");
let imagem_selecionada;
let botao_anexo = document.querySelector("#mais-arquivo");
let miniatura_imagem;

async function buscarImagem() {
    let fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = "image/*";

    fileInput.onchange = async e => {
        if(miniatura_imagem) {
            miniatura_imagem.remove();
        }
        imagem_selecionada = e.target.files[0];
        miniatura_imagem = document.createElement("img");
        miniatura_imagem.src =  URL.createObjectURL(imagem_selecionada);
        miniatura_imagem.style.maxWidth = "3rem";
        miniatura_imagem.style.minWidth = "3rem";
        miniatura_imagem.style.margin = "0.5rem";

        document.querySelector(".entrada__container").insertBefore(miniatura_imagem, input);

        let formData = new FormData();
        formData.append("imagem", imagem_selecionada);

        const response = await fetch("http://127.0.0.1:5000/upload_imagem", {
            method: 'POST',
            body: formData
        });

        const resposta = await response.text();
        console.log(resposta)
        console.log(imagem_selecionada);
    }
    fileInput.click();
}

async function enviarMensagem() {
    if(input.value == "" || input.value == null) return;
    let mensagem = input.value;
    input.value = "";

    let nova_bolha = criaBolhaUsuario();
    nova_bolha.innerHTML = mensagem;
    chat.appendChild(nova_bolha);

    let nova_bolha_bot = criaBolhaBot();
    chat.appendChild(nova_bolha_bot);
    vaiParaFinalDoChat();
    nova_bolha_bot.innerHTML = "Digitando ..."
    
    // Envia requisição com a mensagem para a API do ChatBot
    const resposta = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
        "Content-Type": "application/json",
        },
        body: JSON.stringify({"msg":mensagem}),
    });
    const texto_da_resposta = await resposta.text();
    console.log(texto_da_resposta);
    nova_bolha_bot.innerHTML = texto_da_resposta.replace(/\n/g, '<br>');
    vaiParaFinalDoChat();
}

function criaBolhaUsuario() {
    let bolha = document.createElement('p');
    bolha.classList = "chat__bolha chat__bolha--usuario";
    return bolha;
}

function criaBolhaBot() {
    let bolha = document.createElement('p');
    bolha.classList = "chat__bolha chat__bolha--bot";
    return bolha;
}

function vaiParaFinalDoChat() {
    chat.scrollTop = chat.scrollHeight;
}

botao_enviar.addEventListener('click', enviarMensagem);
input.addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode === 13) {
        botao_enviar.click();
    }
});

botao_anexo.addEventListener('click', buscarImagem);
});