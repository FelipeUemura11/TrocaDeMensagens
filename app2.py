# Envia msg criptografada
# servidor remetente
from flask import Flask, request, jsonify, render_template
import requests
import logging
import hashlib
from datetime import datetime
import uuid

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

msg_lista = []
msg_processadas = set()

def obterChavePub():
    try:
        logger.debug("Obtendo chave publica do servidor receptor...")
        resposta = requests.get('http://localhost:5000/obter_chave_pub')
        resposta.raise_for_status()

        n, e = map(int, resposta.text.split(','))
        chave_pub = (n, e)
        logger.debug("Chave publica obtida com sucesso")
        return chave_pub
    except Exception as e:
        logger.error(f"Erro ao obter chave publica: {str(e)}")
        raise
def criptografarMsg(msg, chave_pub):
    n, e = chave_pub
    msg_bytes = msg.encode('utf-8')
    msg_int = int.from_bytes(msg_bytes, 'big')

    criptografada = pow(msg_int, e, n)
    return criptografada

def gerarHashMsg(msg):
    return hashlib.sha256(msg.encode('utf-8')).hexdigest()

def enviarMsgCriptografada(msg):
    try:
        chave_pub = obterChavePub()

        logger.debug("Criptografando mensagem...")
        criptografada = criptografarMsg(msg, chave_pub)
        logger.debug("Mensagem criptografada com sucesso")

        logger.debug("Gerando hash da msg...")
        hash_msg = gerarHashMsg(msg)
        logger.debug("Hash gerado com sucesso")

        logger.debug("Enviando mensagem para webhook...")
        resposta = request.post(
            'http://localhost:5000/webhook',
            json={
                "mensagem_criptografada": str(criptografada),
                "hash_msg": hash_msg
            }
        )
        resposta.raise_for_status()
        logger.debug("Mensagem enviada com sucesso")

        return resposta.json()
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Erro ao conectar com o servidor de chaves: {e}")
    except Exception as e:
        logger.error(f"Erro de conexao: {str(e)}")
        return {"erro": "Erro ao obter chave pública"}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        dados = request.get_json()
        if not dados or 'mensagem' not in dados:
            return jsonify({'erro': "Mensagem não encontrada"}), 400
        msg = dados['mensagem']
        resultado = enviarMsgCriptografada(msg)
        return jsonify(resultado)

@app.route("/check_mensagens", methods=['POST'])
def check_messages():
    try:
        resposta = requests.get('http://localhost:5000/check_mensagens')
        resposta.raise_for_status()
        mensagens_receptor = resposta.json().get('mensagens', [])
        
        msg_novas = [msg for msg in mensagens_receptor if msg['id'] not in msg_processadas]
        
        for msg in msg_novas:
            msg_processadas.add(msg['id'])
            if not any(m['id'] == msg['id'] for m in msg_lista):
                msg_lista.append(msg)
            
        if len(msg_lista) > 100:
            msg_lista.pop(0)
            
        return jsonify({"mensagens": msg_lista})
    except Exception as e:
        logger.error(f"Erro ao buscar mensagens do receptor: {str(e)}")
        return jsonify({"mensagens": [], "erro": str(e)})

if __name__ == '__main__':
    app.run(port=5001, debug=True)
