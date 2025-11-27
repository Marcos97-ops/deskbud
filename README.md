# 🧠 Deskbud - AI Attention Monitor

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Flask-SocketIO-orange)
![Status](https://img.shields.io/badge/Status-Concluído-success)

O **Deskbud** (Amigo de Mesa) é uma aplicação inteligente de Visão Computacional projetada para monitorar o foco e a postura do usuário em tempo real. Utilizando uma webcam comum, o sistema classifica o comportamento em três estados distintos: **Atento**, **Desatento** ou **Ausente**, fornecendo feedback visual, estatístico e sonoro.

---

## 🚀 Funcionalidades

- **Detecção em Tempo Real:** Processamento de vídeo via webcam com baixa latência.
- **Classificação Inteligente:** Utiliza **Random Forest** treinado com dados reais de postura (33 landmarks corporais via MediaPipe).
- **Lógica Híbrida:** Sistema robusto que diferencia "desatenção" de "ausência total" (usuário fora da cadeira).
- **Feedback Sonoro:** Emite um bipe de alerta (Web Audio API) ao detectar desatenção.
- **Dashboard de Estatísticas:** Acompanhamento percentual do tempo de foco durante a sessão.

---

## 🛠️ Tecnologias Utilizadas

### Backend & IA
- **Python 3:** Linguagem principal.
- **MediaPipe (Google):** Extração de pontos-chave do corpo (Landmarks).
- **Scikit-learn:** Treinamento do modelo de Machine Learning.
- **Flask & Flask-SocketIO:** Servidor web e comunicação via WebSockets.
- **OpenCV:** Manipulação de vídeo e imagens.
- **Pandas:** Estruturação e manipulação do dataset.

### Frontend
- **HTML5 & CSS3:** Interface moderna e responsiva.
- **JavaScript:** Captura de vídeo, lógica de cliente e Web Audio API.

---

## 📦 Guia de Instalação e Execução

Siga os passos abaixo para rodar o projeto no seu computador.

### 1. Preparação do Ambiente

Clone o repositório e instale as dependências:

```bash
# Clone este repositório
git clone [https://github.com/Marcos97-ops/deskbud.git](https://github.com/Marcos97-ops/deskbud.git)

# Entre na pasta
cd deskbud

# Crie um ambiente virtual (Recomendado)
python3 -m venv .venv
source .venv/bin/activate

# Instale as bibliotecas necessárias
pip install -r requirements.txt



...
## 👨‍💻 Autor

Desenvolvido por **Marcos Paulo**.

Entre em contato!
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/marcos-paulo-lourenço-da-silva-84a6a22a7)
