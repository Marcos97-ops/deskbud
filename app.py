import cv2
import mediapipe as mp
import numpy as np
import pickle
import base64
import re
import os

from flask import Flask, send_from_directory
from flask_socketio import SocketIO

# --- CONFIGURAÇÕES ---
MODEL_PATH = 'atencao_model.pkl'
CONFIDENCE_THRESHOLD = 0.70
# ---------------------

print("--- PASSO 3: Iniciando servidor Flask... ---")
app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = 'seu-segredo-super-secreto!'
socketio = SocketIO(app)
print("Servidor Flask e Socket.IO iniciados.")

print(f"Carregando o modelo de IA '{MODEL_PATH}'...")
if not os.path.exists(MODEL_PATH):
    print(f"ERRO: Arquivo '{MODEL_PATH}' não encontrado.")
    exit()
    
try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    print("Modelo carregado com sucesso.")
except Exception as e:
    print(f"Erro ao carregar o modelo: {e}")
    exit()

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose_processor = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
print("MediaPipe Pose inicializado.")

@app.route('/')
def index():
    print("Servindo index.html para um cliente...")
    return send_from_directory('.', 'index.html')

@socketio.on('connect')
def handle_connect():
    print("Cliente (navegador) conectado!")

@socketio.on('disconnect')
def handle_disconnect():
    print("Cliente desconectado.")

# ===================================================================
#  A MUDANÇA ESTÁ AQUI
# ===================================================================
@socketio.on('stream_image')
def handle_stream(image_data):
    """
    Recebe o frame, processa com IA e envia o resultado de volta.
    AGORA COM LÓGICA EXPLÍCITA PARA 'AUSENTE'.
    """
    global pose_processor

    try:
        img_data_cleaned = re.sub('^data:image/.+;base64,', '', image_data)
        img_bytes = base64.b64decode(img_data_cleaned)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return
    except Exception as e:
        print(f"Erro ao decodificar imagem: {e}")
        return

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose_processor.process(image_rgb)
    
    # --- NOVA LÓGICA IF/ELSE ---
    if results.pose_landmarks:
        # 1. PESSOA DETECTADA: Deixa o modelo de IA decidir
        try:
            landmarks = results.pose_landmarks.landmark
            row = np.array([[lm.x, lm.y, lm.z, lm.visibility] for lm in landmarks]).flatten()
            
            prediction = model.predict([row])[0]
            probability = model.predict_proba([row])[0]
            confidence = np.max(probability)
            
            if confidence > CONFIDENCE_THRESHOLD:
                # O modelo pode dizer 'atento' ou 'desatento'
                # (Ele raramente dirá 'ausente' aqui, o que é bom)
                socketio.emit('ia_result', {'status': prediction, 'confidence': confidence})
            
            # Se a confiança for baixa, não enviamos nada (evita piscar)

        except Exception:
            pass # Ignora frames de predição ruins
            
    else:
        # 2. NINGUÉM DETECTADO: Força o status 'ausente'
        # Não precisamos do modelo de IA, isso é um fato.
        socketio.emit('ia_result', {'status': 'ausente', 'confidence': 1.0})
    # --- FIM DA NOVA LÓGICA ---

# ===================================================================
# FIM DA MUDANÇA
# ===================================================================

if __name__ == '__main__':
    print("\n--- INSTRUCOES ---")
    print(f"1. Abra http://localhost:5000 (ou http://127.0.0.1:5000) no seu navegador.")
    print("2. Pressione Ctrl+C no terminal para parar o servidor.")
    
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
    
    print("Servidor finalizado.")
    cv2.destroyAllWindows()