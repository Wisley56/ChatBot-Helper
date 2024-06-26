from concurrent.futures import thread
from time import sleep
from flask import Flask,render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from helpers import *
from selecionar_persona import *
from assistente_openai import *
from vision_inner_friend import analisar_imagem
import uuid 

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4o"
caminho_imagem_enviada = None
STATUS_COMPLETED = "completed" 
UPLOAD_FOLDER = 'dados' 

app = Flask(__name__)
app.secret_key = 'wisley'
sinais_negativos = carrega("dados\palavras_chave.txt")
idade = 21 #puxar do banco/front.
assistente = pegar_json()
thread_id = assistente["thread_id"]
assistente_id = assistente["assistant_id"]

def bot(prompt):
    global caminho_imagem_enviada
    maximo_tentativas = 2
    repeticao = 0
    
    while True:
        try:
            personalidade = retorno_personalidade(idade)

            cliente.beta.threads.messages.create(
                thread_id=thread_id, 
                role = "user",
                content =  f"""
                Assuma, de agora em diante, a personalidade abaixo. 
                Ignore as personalidades anteriores.

                # Persona
                {personalidade}
                """
            )

            resposta_vision = ""
            if caminho_imagem_enviada != None:
                 resposta_vision = analisar_imagem(caminho_imagem_enviada)
                 os.remove(caminho_imagem_enviada)
                 caminho_imagem_enviada = ""

            cliente.beta.threads.messages.create(
                thread_id=thread_id, 
                role = "user",
                content =  resposta_vision+prompt
            )

            run = cliente.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistente_id
            )

            while run.status != STATUS_COMPLETED:
                run = cliente.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
            )
            
            historico = list(cliente.beta.threads.messages.list(thread_id=thread_id).data)
            resposta = historico[0]
            print(historico)
            return resposta

        except Exception as erro:
                repeticao += 1
                if repeticao >= maximo_tentativas:
                        return "Erro no GPT: %s" % erro
                print('Erro de comunicação com OpenAI:', erro)
                sleep(1)


@app.route("/upload_imagem", methods=["POST"])
def upload_imagem():
     global caminho_imagem_enviada
     if "imagem" in request.files:
        imagem_enviada = request.files["imagem"]
        nome_arquivo = str(uuid.uuid4()) + os.path.splitext(imagem_enviada.filename)[1]
        caminho_arquivo = os.path.join(UPLOAD_FOLDER, nome_arquivo)
        imagem_enviada.save(caminho_arquivo)
        caminho_imagem_enviada = caminho_arquivo
        return "Imagem recebida com sucesso.", 200
     return "Nenhum arquivo foi enviado.", 400

@app.route("/chat", methods=["POST"])
def chat():
    prompt = request.json["msg"]
    resposta = bot(prompt)
    if isinstance(resposta, str):
        return resposta 
    texto_resposta = resposta.content[0].text.value
    return texto_resposta

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True)
