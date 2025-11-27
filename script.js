const startCameraBtn = document.getElementById("startCameraBtn");
const stopCameraBtn = document.getElementById("stopCameraBtn");
const cameraCircle = document.getElementById("cameraCircle");
const statusDisplay = document.getElementById("status-display"); 

const atentoPercentSpan = document.getElementById("atento-percent");
const desatentoPercentSpan = document.getElementById("desatento-percent");
const ausentePercentSpan = document.getElementById("ausente-percent");

const socket = io(); 
console.log("Socket.IO inicializado.");

let mediaStream;
let videoElement;
let captureInterval;

let atentoCount = 0;
let desatentoCount = 0;
let ausenteCount = 0;
let totalCount = 0;

// =============================================
// =    NOVAS VARIÁVEIS (PARA O SOM)     =
// =============================================
let audioCtx; // O "contexto de áudio" do navegador
let ultimoStatus = ""; // Para saber quando o status MUDA
// =============================================


// =======================
// 🎥 CONTROLES DA CÂMERA
// =======================
startCameraBtn.addEventListener("click", async () => {
  try {
    
    // Pedimos a resolução ideal
    const constraints = {
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 }
      }
    };
    mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
    
    console.log("Câmera acessada.");

    // =============================================
    // =    DESBLOQUEAR O ÁUDIO (MUITO IMPORTANTE)    =
    // =============================================
    // O áudio só pode começar após um clique do usuário.
    // Vamos usar este clique para criar e "desbloquear" o áudio.
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      console.log("Contexto de áudio desbloqueado.");
    }
    // =============================================

    videoElement = document.createElement("video");
    videoElement.srcObject = mediaStream;
    videoElement.autoplay = true;
    videoElement.playsInline = true;
    videoElement.style.width = "100%";
    videoElement.style.height = "100%";
    videoElement.style.objectFit = "cover";
    videoElement.style.transform = "scaleX(-1)"; 

    cameraCircle.innerHTML = "";
    cameraCircle.appendChild(videoElement);

    startCameraBtn.disabled = true;
    stopCameraBtn.disabled = false;

    captureInterval = setInterval(() => enviarFrame(videoElement), 400); 
    
    statusDisplay.textContent = "Status: Analisando...";
    statusDisplay.className = "";
    ultimoStatus = "analisando"; // Reseta o status

    // Resetar contagem
    atentoCount = 0;
    desatentoCount = 0;
    ausenteCount = 0;
    totalCount = 0;
    atentoPercentSpan.textContent = "0%";
    desatentoPercentSpan.textContent = "0%";
    ausentePercentSpan.textContent = "0%";

  } catch (err) {
    alert("Erro ao acessar câmera: " + err.message);
    console.error(err);
  }
});

stopCameraBtn.addEventListener("click", () => {
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop());
    mediaStream = null;
    console.log("Câmera parada.");
  }
  clearInterval(captureInterval);
  cameraCircle.innerHTML = "<span style='color:#555;font-size:14px;'>Câmera desligada</span>";
  startCameraBtn.disabled = false;
  stopCameraBtn.disabled = true;

  statusDisplay.textContent = "Status: Aguardando...";
  statusDisplay.className = "";
  ultimoStatus = ""; // Limpa o status
});

// =======================
// ENVIO DE FRAMES (JS -> Python)
// =======================
function enviarFrame(video) {
  if (!video.videoWidth || !video.videoHeight) return;
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");

  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  
  const imageData = canvas.toDataURL("image/jpeg");
  socket.emit("stream_image", imageData);
}

// =============================================
// =    FUNÇÃO PARA TOCAR O BIPE     =
// =============================================
function tocarBipe() {
  if (!audioCtx) return; // Se o áudio não foi desbloqueado, não faz nada

  const oscillator = audioCtx.createOscillator(); // Cria o "som"
  const gainNode = audioCtx.createGain(); // Cria o "volume"

  // Conecta o som ao volume, e o volume aos alto-falantes
  oscillator.connect(gainNode);
  gainNode.connect(audioCtx.destination);

  oscillator.type = 'sine'; // Tipo de onda (um bipe limpo)
  oscillator.frequency.setValueAtTime(800, audioCtx.currentTime); // Frequência (800 Hz é um bom bipe)
  gainNode.gain.setValueAtTime(0.5, audioCtx.currentTime); // Metade do volume

  oscillator.start(audioCtx.currentTime); // Toca agora
  oscillator.stop(audioCtx.currentTime + 0.1); // Para de tocar depois de 0.1 segundos
}
// =============================================

// =============================================
// RECEBIMENTO DE RESULTADOS (Python -> JS)
// =============================================
socket.on('ia_result', (data) => {
  const status = data.status;
  
  // =============================================
  // =    LÓGICA DO ALERTA SONORO     =
  // =============================================
  // Queremos tocar o bipe APENAS se o status MUDOU e se ele MUDOU PARA "desatento"
  // Isso evita que o bipe toque 10x por segundo se você continuar desatento.
  if (status === 'desatento' && ultimoStatus !== 'desatento') {
    tocarBipe();
  }
  ultimoStatus = status; // Atualiza o último status conhecido
  // =============================================


  // 1. Atualiza o status principal
  if (status === 'atento') {
    statusDisplay.textContent = "Status: ATENTO ✅";
    statusDisplay.className = "status-atento"; 
  } else if (status === 'desatento') {
    statusDisplay.textContent = "Status: DESATENTO ❌";
    statusDisplay.className = "status-desatento";
  } else if (status === 'ausente') {
    statusDisplay.textContent = "Status: AUSENTE 🤷‍♂️";
    statusDisplay.className = "status-ausente";
  }

  // 2. Lógica de contagem
  totalCount++;
  if (status === 'atento') {
    atentoCount++;
  } else if (status === 'desatento') {
    desatentoCount++;
  } else if (status === 'ausente') {
    ausenteCount++;
  }

  // 3. Calcula e exibe as porcentagens
  atentoPercentSpan.textContent = `${((atentoCount / totalCount) * 100).toFixed(0)}%`;
  desatentoPercentSpan.textContent = `${((desatentoCount / totalCount) * 100).toFixed(0)}%`;
  ausentePercentSpan.textContent = `${((ausenteCount / totalCount) * 100).toFixed(0)}%`;
});

socket.on('connect', () => {
    console.log('Conectado ao servidor (Python)!');
});

socket.on('disconnect', () => {
    console.log('Desconectado do servidor (Python).');
});