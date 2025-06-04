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

# Lista para armazenar mensagens
mensagens = []

def eh_primo(n, k=5):
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

def gerar_primo(bits):
    while True:
        n = random.getrandbits(bits)
        if eh_primo(n):
            return n

def gerar_par_chaves():
    p = gerar_primo(512)
    q = gerar_primo(512)
    
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    d = pow(e, -1, phi)
    
    return (n, e), (n, d)

chave_publica, chave_privada = gerar_par_chaves()

def criptografar_mensagem(mensagem, chave_publica):
    n, e = chave_publica
    mensagem_bytes = mensagem.encode('utf-8')
    mensagem_int = int.from_bytes(mensagem_bytes, 'big')
    
    criptografado = pow(mensagem_int, e, n)
    return criptografado

def descriptografar_mensagem(criptografado, chave_privada):
    n, d = chave_privada
    descriptografado = pow(criptografado, d, n)
    
    descriptografado_bytes = descriptografado.to_bytes((descriptografado.bit_length() + 7) // 8, 'big')
    return descriptografado_bytes.decode('utf-8')

def verificar_hash(mensagem, hash_recebido):
    hash_mensagem = hashlib.sha256(mensagem.encode('utf-8')).hexdigest()
    return hash_mensagem == hash_recebido

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        dados = request.get_json()
        if not dados or 'mensagem' not in dados:
            return jsonify({"erro": "Mensagem não fornecida"}), 400
        mensagem = dados['mensagem']
        # Adiciona mensagem localmente (opcional, pois mensagens recebidas vêm do webhook)
        timestamp = datetime.now().strftime("%H:%M:%S")
        message_id = str(uuid.uuid4())[:8]
        mensagens.append({
            "id": message_id,
            "timestamp": timestamp,
            "texto": mensagem
        })
        if len(mensagens) > 100:
            mensagens.pop(0)
        return jsonify({"status": "Mensagem recebida com sucesso!"})

@app.route("/obter_chave_publica", methods=['GET'])
def obter_chave_publica():
    try:
        logger.debug("Gerando chave publica...")
        chave_publica_str = f"{chave_publica[0]},{chave_publica[1]}"
        logger.debug("Chave publica gerada com sucesso")
        return chave_publica_str
    except Exception as e:
        logger.error(f"Erro ao gerar chave publica: {str(e)}")
        return jsonify({"erro": str(e)}), 500

@app.route("/check_messages", methods=['GET'])
def check_messages():
    return jsonify({"mensagens": mensagens})

@app.route("/webhook", methods=['POST'])
def webhook():
    try:
        logger.debug("Recebendo mensagem criptografada...")
        criptografado_data = request.json.get('mensagem_criptografada')
        hash_recebido = request.json.get('hash_mensagem')
        
        if not criptografado_data or not hash_recebido:
            raise ValueError("Mensagem criptografada ou hash não recebidos")
            
        criptografado_int = int(criptografado_data)
        logger.debug("Mensagem convertida para inteiro")

        mensagem_descriptografada = descriptografar_mensagem(criptografado_int, chave_privada)
        
        if not verificar_hash(mensagem_descriptografada, hash_recebido):
            raise ValueError("Hash da mensagem não corresponde - possível manipulação detectada")

        # Adicionar mensagem à lista com timestamp e ID único
        timestamp = datetime.now().strftime("%H:%M:%S")
        message_id = str(uuid.uuid4())[:8]  # Usa os primeiros 8 caracteres do UUID
        mensagens.append({
            "id": message_id,
            "timestamp": timestamp,
            "texto": mensagem_descriptografada
        })
        
        # Limitar o número de mensagens armazenadas
        if len(mensagens) > 100:
            mensagens.pop(0)

        logger.debug(f"Mensagem recebida (Descriptografada): {mensagem_descriptografada}")
        return jsonify({"status": "Mensagem recebida e verificada com sucesso!"}), 200
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)