import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle
import os

# --- CONFIGURAÇÕES ---
CSV_PATH = 'pose_data_atencao.csv' # LER o CSV que você acabou de criar
MODEL_PATH = 'atencao_model.pkl'   # SALVAR o novo modelo de IA
# ---------------------

print("--- PASSO 2: Iniciando o treinamento do modelo de ATENCAO ---")

# 1. Verifica se o arquivo de dados existe
if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
    print(f"ERRO: Arquivo '{CSV_PATH}' não encontrado ou está vazio.")
    print("Você precisa executar o 'collect_data.py' primeiro e salvar dados.")
    exit()

# 2. Carrega o dataset
df = pd.read_csv(CSV_PATH)
print(f"Dataset '{CSV_PATH}' carregado com sucesso.")

if len(df) < 50:
    print(f"AVISO: Você tem poucas amostras de dados ({len(df)}). O modelo pode não ser muito preciso.")
    print("Para um resultado melhor, colete mais dados no Passo 1.")

print("\nDistribuição das classes:")
print(df['class'].value_counts())

# 3. Separa as features (coordenadas) e o target (classe)
X = df.drop('class', axis=1) # features
y = df['class']              # target

# 4. Divide os dados em conjuntos de treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1234, stratify=y)

# 5. Cria e treina o modelo (RandomForest)
model = RandomForestClassifier(n_estimators=100, random_state=42)
print("\nTreinando o modelo RandomForest...")
model.fit(X_train, y_train)
print("Treinamento concluído.")

# 6. Avalia a performance no conjunto de teste
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\n=======================================================")
print(f"  Acurácia do modelo no conjunto de teste: {accuracy * 100:.2f}%")
print(f"=======================================================")

# 7. Salva o modelo treinado
with open(MODEL_PATH, 'wb') as f:
    pickle.dump(model, f)

print(f"\nModelo salvo com sucesso como '{MODEL_PATH}'!")
print("Próximo passo: execute o 'app.py'.")