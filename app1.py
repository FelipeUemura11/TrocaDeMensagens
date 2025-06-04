# Recebe e descriptografa msg
# servidor receptor
from flask import Flask, request, jsonify, render_template
import logging
import random
import hashlib
from datetime import datetime
import uuid

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

msg_lista = []

# teste de miller-rabin para primalidade
def primoTrue(n, k=5):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False
    
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def gerarPrimo(bits):
    while True:
        n = random.getrandbits(bits)
        if primoTrue(n):
            return n

def gerarParChaves():
    logger.debug("Gerando par de chaves RSA...")
    p =  gerarPrimo(512)
    q =  gerarPrimo(512)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    d = pow(e, -1, phi)
    return (e, n), (d, n)

chave_pub, chave_pri = gerarParChaves()

def descriptografarMsg(criptografado, chave_pri):
    d, n = chave_pri
    descriptografado = pow(criptografado, d, n)
    # converte para bytes e depois para string
    descriptografado_bytes = descriptografado.to_bytes((descriptografado.bit_length() + 7) // 8, 'big')
    return descriptografado_bytes.decode('utf-8')

def verificar_hash(mensagem, hash_recebido):
    hash_msg = hashlib.sha256(mensagem.encode('utf-8')).hexdigest()
    return hash_msg == hash_recebido

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    if(request.method == 'POST'):
        dados = request.get_json()
        if not dados or 'mensagem' not in dados:
            return jsonify({'erro': "Mensagem não encontrada"}), 400
        mensagem = dados['mensagem']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message_id = str(uuid.uuid4())[:8]
        msg_lista.append({
            "id": message_id,
            "timestamp": timestamp,
            "texto": mensagem
        })

        return jsonify({"status": "Mensagem recebida com sucesso!"})
    
@app.route("/obter_chave_pub", methods=['GET'])
def obter_chave_pub():
    try:
        logger.debug(" >>>>> Gerando chave publica <<<<<")
        chave_pub_str = f"{chave_pub[0]}, {chave_pub[1]}"
        logger.debug(" >>>>> Chave publica gerada <<<<<")
        return chave_pub_str, 200
    except Exception as e:
        logger.error(f"Erro ao obter chave publica: {e}")
        return jsonify({"ERROR": "Erro ao obter chave publica"}), 500

# verifica as mensagens novas a cada 2 segundos
@app.route("/check_mensagens", methods=['GET'])
def checar_menssagens():
    return jsonify({"mensagens": msg_lista}), 200

@app.route("/webhook", methods=['POST'])
def webhook():
    try:
        logger.debug(" >>>>> Recebendo mensagem do webhook <<<<<")
        criptografada_data = request.json.get('mensagem_criptografada')
        hash_recebido = request.json.get("hash_mensagem")

        if not criptografada_data or not hash_recebido:
            raise ValueError("Mensagem criptografada ou hash não fornecidos")
        
        criptografado_int = int(criptografada_data)
        logger.debug("Mensagem convertida para inteiro")

        msg_descriptografada = descriptografarMsg(criptografado_int, chave_pri)

        if not verificar_hash(msg_descriptografada, hash_recebido):
            raise ValueError("Hash da mensagem não corresponde - manipulação detectada")
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        message_id = str(uuid.uuid4())[:8]
        msg_lista.append({
            "id": message_id,
            "timestamp": timestamp,
            "texto": msg_descriptografada
        })

        logger.debug(f"Mensagem recebida e descriptografada: {msg_descriptografada}")
        return jsonify({"status": "Mensagem recebida e processada com sucesso!"}), 200
    except Exception as e:
        logger.error(f"Erro ao processar mensagem do webhook: {e}")
        return jsonify({"ERROR": "Erro ao processar mensagem"}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
