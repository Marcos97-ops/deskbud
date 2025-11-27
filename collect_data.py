import cv2
import mediapipe as mp
import numpy as np
import csv
import os
import glob
import time

# --- CONFIGURAÇÕES ---
OUTPUT_CSV_PATH = 'pose_data_atencao.csv'
VIDEO_FOLDER = 'videos/' # Pasta 'videos' (minúsculo)
# ---------------------

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def setup_csv():
    """Cria o cabeçalho do arquivo CSV se ele não existir."""
    num_coords = 33
    landmarks_header = ['class']
    for val in range(1, num_coords + 1):
        landmarks_header += [f'x{val}', f'y{val}', f'z{val}', f'v{val}']
    
    if not os.path.exists(OUTPUT_CSV_PATH):
        with open(OUTPUT_CSV_PATH, mode='w', newline='') as f:
            csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(landmarks_header)
        print(f"Arquivo '{OUTPUT_CSV_PATH}' criado com cabeçalho.")
    else:
        # Se o arquivo já existe, apaga para começar do zero
        print(f"Arquivo '{OUTPUT_CSV_PATH}' antigo encontrado. Apagando para recomeçar.")
        os.remove(OUTPUT_CSV_PATH)
        setup_csv() # Recria o cabeçalho

def save_frame_data(pose_class, results):
    """Salva os landmarks (coordenadas da pose) do frame atual no CSV."""
    
    landmarks_data = []
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        landmarks_data = list(np.array([[lm.x, lm.y, lm.z, lm.visibility] for lm in landmarks]).flatten())
    else:
        landmarks_data = list(np.zeros(33 * 4))
        # Não imprimimos mais a mensagem de "zeros" para não poluir o log
        # print("Nenhuma pose detectada, salvando como zeros (bom para 'ausente').")

    try:
        row = landmarks_data
        row.insert(0, pose_class)
        
        with open(OUTPUT_CSV_PATH, mode='a', newline='') as f:
            csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(row)
            
        # Removido o print de "Frame salvo" para acelerar o processo
        # print(f"Frame salvo para a classe: '{pose_class}'")
            
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")

# --- SCRIPT PRINCIPAL ---
setup_csv()

if not os.path.exists(VIDEO_FOLDER):
    print(f"ERRO: A pasta '{VIDEO_FOLDER}' não foi encontrada.")
    exit()

video_files = glob.glob(os.path.join(VIDEO_FOLDER, '*.mp4')) + \
              glob.glob(os.path.join(VIDEO_FOLDER, '*.webm')) + \
              glob.glob(os.path.join(VIDEO_FOLDER, '*.avi'))

if not video_files:
    print(f"ERRO: Nenhum arquivo de vídeo foi encontrado na pasta '{VIDEO_FOLDER}'.")
    exit()

print(f"Encontrados {len(video_files)} vídeos para processar.")

for video_path in video_files:
    
    video_filename = os.path.basename(video_path).lower()
    
    # Lógica corrigida para checar a classe
    current_class = 'unknown' 
    
    if 'desatento' in video_filename:
        current_class = 'desatento'
    elif 'atento' in video_filename:
        current_class = 'atento'
    elif 'ausente' in video_filename:
        current_class = 'ausente'
        
    if current_class == 'unknown':
        print(f"AVISO: Não foi possível determinar a classe para o vídeo '{video_path}'. Pulando...")
        continue
            
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Erro ao abrir o vídeo: {video_path}. Pulando...")
        continue

    print(f"\n--- Processando vídeo: {video_path} ---")
    print(f"Classe detectada pelo nome: '{current_class.upper()}'")
    print("Processando... (Isso pode levar alguns segundos)")

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        
        frame_count = 0
        total_frames_saved = 0
        while cap.isOpened():
            
            ret, frame = cap.read()
            if not ret:
                print("Fim do vídeo.")
                break
            
            # Processa 1 frame a cada 10
            frame_count += 1
            if frame_count % 10 != 0:
                continue

            # ================== A CORREÇÃO ESTÁ AQUI ==================
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Corrigido de BGRRGB
            # ==========================================================
            
            results = pose.process(image)
            
            save_frame_data(current_class, results)
            total_frames_saved += 1
            time.sleep(0.01)

    print(f"Processamento concluído. Total de {total_frames_saved} frames salvos.")
    cap.release()

print(f"\n--- Coleta de dados 100% AUTOMÁTICA concluída! ---")
print(f"Verifique o arquivo '{OUTPUT_CSV_PATH}'.")