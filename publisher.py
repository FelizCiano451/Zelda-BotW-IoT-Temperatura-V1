import cv2
import time
import paho.mqtt.client as mqtt
from yt_dlp import YoutubeDL

# ==========================================
# CONFIGURAÇÕES DO MQTT
# ==========================================
BROKER_MQTT = "localhost"
PORTA_MQTT = 1883
TOPICO_TEMPERATURA = "hyrule/monitoramento/temperatura"

print("[MQTT] Conectando ao broker...")
cliente_mqtt = mqtt.Client()
try:
    cliente_mqtt.connect(BROKER_MQTT, PORTA_MQTT, 60)
    cliente_mqtt.loop_start()
    print("[MQTT] Conectado com sucesso!")
except Exception as e:
    print(f"[MQTT] Erro ao conectar: {e}. O broker Mosquitto está ativo?")

# ==========================================
# CONFIGURAÇÕES DE STREAMING DO YOUTUBE
# ==========================================
URL_YOUTUBE = "https://youtu.be/LtQLKo0T4Co?si=38qc_EH5i_E1ndZS" # Longplay

print("[YOUTUBE] Extraindo URL de streaming...")
ydl_opts = {
    'format': 'best[height<=720]',  # Limitar para 720p para economizar banda e processamento local (Precisa? Não sei, mas é bom. Qualquer coisa eu tiro)
    'quiet': True
}

try:
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(URL_YOUTUBE, download=False)
        # Obtém a URL direta do fluxo de vídeo
        url_streaming = info_dict.get('url')
except Exception as e:
    print(f"Erro ao obter vídeo do YouTube: {e}")
    exit()

# O OpenCV abre a URL de streaming direto do servidor do Google
cap = cv2.VideoCapture(url_streaming)

if not cap.isOpened():
    print("Erro: Não foi possível carregar o streaming do YouTube.")
    exit()

print("[SISTEMA] Iniciando monitoramento da HUD de Hyrule via YouTube...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Falha ao receber frame (fim do streaming ou instabilidade de rede).")
        break

    # Pegar as dimensões dinamicamente (depende da resolução do vídeo)
    altura, largura, _ = frame.shape

    # =========================================================================
    # RECORTE DA HUD (Região de Interesse - ROI)
    # Focado no canto inferior direito do Zelda BotW
    # =========================================================================
    y_inicio = int(altura * 0.75)
    y_fim = int(altura * 0.95)
    x_inicio = int(largura * 0.80)
    x_fim = int(largura * 0.98)

    hud_clima = frame[y_inicio:y_fim, x_inicio:x_fim]

    # Simulação do dado extraído (para validação do fluxo do protocolo MQTT)
    temperatura_simulada = 18.0 
    
    payload = f"{temperatura_simulada}°C"
    cliente_mqtt.publish(TOPICO_TEMPERATURA, payload)
    print(f"[PUBLISHER] Enviado via MQTT -> {payload}")

    # ==========================================
    # EXIBIÇÃO DAS JANELAS
    # ==========================================
    cv2.imshow("Gameplay - YouTube Streaming", frame)
    cv2.imshow("HUD - Termometro Isolado", hud_clima)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Aguarda 2 segundos antes de processar o próximo frame/enviar o dado
    time.sleep(2)

cap.release()
cv2.destroyAllWindows()
cliente_mqtt.loop_stop()
cliente_mqtt.disconnect()
print("[SISTEMA] Encerrado.")
