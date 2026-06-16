import cv2
import time
import paho.mqtt.client as mqtt

# ==========================================
# CONFIGURAÇÕES DO MQTT
# ==========================================
BROKER_MQTT = "localhost"  # Com o Mosquitto rodando localmente
PORTA_MQTT = 1883
TOPICO_TEMPERATURA = "hyrule/monitoramento/temperatura"

# Inicializa o cliente MQTT
print("[MQTT] Conectando ao broker...")
cliente_mqtt = mqtt.Client()
try:
    cliente_mqtt.connect(BROKER_MQTT, PORTA_MQTT, 60)
    cliente_mqtt.loop_start()
    print("[MQTT] Conectado com sucesso!")
except Exception as e:
    print(f"[MQTT] Erro ao conectar: {e}. O broker Mosquitto está ativo?")

# ==========================================
# CONFIGURAÇÕES DE VÍDEO (OPENCV)
# ==========================================
# Substituir pelo caminho do vídeo de gameplay do Zelda
CAMINHO_VIDEO = "gameplay_zelda.mp4" 

cap = cv2.VideoCapture(CAMINHO_VIDEO)

if not cap.isOpened():
    print(f"Erro: Não foi possível abrir o vídeo '{CAMINHO_VIDEO}'.")
    exit()

print("[SISTEMA] Iniciando monitoramento da HUD de Hyrule...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Fim do vídeo ou erro na leitura do frame.")
        break

    # Pegar as dimensões do vídeo para calcular a posição da HUD
    altura, largura, _ = frame.shape

    # =========================================================================
    # RECORTE DA HUD (Região de Interesse - ROI)
    # No Zelda BotW, o termômetro fica no canto inferior direito.
    # Ajustar os valores abaixo conforme a resolução do vídeo.
    # =========================================================================
    # Teste 1 para vídeo 1080p (1920x1080): pegando o canto inferior direito
    y_inicio = int(altura * 0.75)  # Começa em 75% da altura
    y_fim = int(altura * 0.95)     # Vai até 95% da altura
    x_inicio = int(largura * 0.80) # Começa em 80% da largura
    x_fim = int(largura * 0.98)    # Vai até 98% da largura

    hud_clima = frame[y_inicio:y_fim, x_inicio:x_fim]

    # =========================================================================
    # LÓGICA DE PROCESSAMENTO DA IMAGEM
    # Aqui entrará a análise de cor ou correspondência de imagem.
    # Por enquanto, simulamr o valor que seria extraído para testar o MQTT.
    # =========================================================================
    temperatura_simulada = 22.5 # Substituir pela leitura real do OpenCV
    
    # Publica o dado no Broker MQTT
    payload = f"{temperatura_simulada}°C"
    cliente_mqtt.publish(TOPICO_TEMPERATURA, payload)
    print(f"[PUBLISHER] Dados de Hyrule enviados -> {payload}")

    # ==========================================
    # EXIBIÇÃO DAS JANELAS (Interface Gráfica)
    # ==========================================
    # Mostra o jogo completo
    cv2.imshow("Gameplay - Visao Geral", frame)
    
    # Mostra apenas o recorte que o algoritmo está analisando
    cv2.imshow("HUD - Termometro Isolado", hud_clima)

    # Tecla 'q' para sair do loop
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

    # Delay para não inundar o broker (envia a cada 2 segundos)
    time.sleep(2)

# Limpeza final
cap.release()
cv2.destroyAllWindows()
cliente_mqtt.loop_stop()
cliente_mqtt.disconnect()
print("[SISTEMA] Encerrado.")
