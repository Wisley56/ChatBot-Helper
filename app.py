from concurrent.futures import thread
from time import sleep
from flask import Flask,render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from helpers import *
from selecionar_persona import *
from assistente_openai import *

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-3.5-turbo"

app = Flask(__name__)
app.secret_key = 'wisley'
sinais_negativos = carrega("dados\palavras_chave.txt")
idade = 21 #puxar do banco/front.
assistente = criar_assistente(idade)
thread = criar_thread()

def bot(prompt):
    maximo_tentativas = 2
    repeticao = 0
    
    while True:
        try:
            cliente.beta.threads.messages.create(
                 thread_id = thread.id,
                 role = "user",
                 content = prompt
            )

            run = cliente.beta.threads.runs.create(
                 thread_id = thread.id,
                 assistant_id = assistente.id 
            )
        
            while run.status != "completed":
                run = cliente.beta.threads.runs.create(
                    thread_id = thread.id,
                    run_id = run.id
            )
            
            historico = list(cliente.beta.threads.messages.lis(thread_id = thread.id).data)
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
     if "imagem" in request.files:
          imagem_enviada = request.files["imagem"]
          print(imagem_enviada)
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
