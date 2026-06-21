import cv2
import time
import math
import random
import paho.mqtt.client as mqtt
from yt_dlp import YoutubeDL

# =========================================================================
# 1. CONFIGURAÇÕES DO PROTOCOLO MQTT (VERSÃO HIVEMQ CLOUD PRIVADO)
# =========================================================================
BROKER_MQTT = "6be44a2810bc469cb87c7054389b42e7.s1.eu.hivemq.cloud:8883" 
PORTA_MQTT = 8883 
TOPICO_TEMPERATURA = "hyrule/monitoramento/temperatura"

# Credenciais criadas no painel da HiveMQ
USUARIO_MQTT = "Zelda"
SENHA_MQTT = "Tloz19862026"

print("[MQTT] Inicializando cliente (API V2)...")
cliente_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# Configurações de segurança obrigatórias para a nuvem privada:
cliente_mqtt.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS_CLIENT)
cliente_mqtt.username_pw_set(USUARIO_MQTT, SENHA_MQTT)

try:
    cliente_mqtt.connect(BROKER_MQTT, PORTA_MQTT, 60)
    cliente_mqtt.loop_start()
    print("[MQTT] Conectado com sucesso ao HiveMQ Cloud Privado!")
except Exception as e:
    print(f"[MQTT] AVISO: Não foi possível conectar ao broker ({e}).")
    print("[MQTT] O script continuará rodando em modo de simulação visual offline.\n")

# =========================================================================
# 2. DICIONÁRIO DE BIOMAS (Diferentes URLs de Gameplay do YouTube)
# =========================================================================
# Mapeia cada região para sua respectiva URL e faixa de temperatura base
BIOMAS_ZELDA = {
    "Planicie de Hyrule (Temperado)": {
        "url": "https://www.youtube.com/watch?v=w7NszvnqO1w", 
        "temp_base": 25.0,
        "variacao": 4.0
    },
    "Montanha da Morte (Quente)": {
        "url": "https://www.youtube.com/watch?v=TGk2DHYYBV8",
        "temp_base": 50.0,
        "variacao": 6.0
    },
    "Montanhas de Hebra (Gelado)": {
        "url": "https://www.youtube.com/watch?v=_xSti7DlmDE",
        "temp_base": -10.0,
        "variacao": 5.0
    }
}

# Configurações do extrator de streaming do YouTube
ydl_opts = {
    'format': 'best[height<=720]',  # Resolução otimizada para processamento em tempo real
    'quiet': True,
    'no_warnings': True
}

# Quantidade de leituras/frames antes de trocar automaticamente de ambiente
MAX_LEITURAS_POR_BIOMA = 15 

# =========================================================================
# 3. LOOP PRINCIPAL - TRANSIÇÃO ENTRE BIOMAS
# =========================================================================
try:
    while True:  # Loop infinito para manter o monitoramento contínuo
        for nome_bioma, config in BIOMAS_ZELDA.items():
            print("\n" + "="*60)
            print(f"[AMBIENTE] Sincronizando novo bioma: {nome_bioma}")
            print("="*60)
            print("[YOUTUBE] Solicitando fluxo de streaming do Google...")
            
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(config["url"], download=False)
                    url_streaming = info_dict.get('url')
            except Exception as e:
                print(f"[ERRO YOUTUBE] Falha ao extrair streaming para {nome_bioma}: {e}")
                print("[SISTEMA] Pulando para o próximo bioma disponível...")
                continue

            # Inicializa a captura do OpenCV com o link de streaming
            cap = cv2.VideoCapture(url_streaming)
            if not cap.isOpened():
                print(f"[ERRO OPENCV] Não foi possível abrir o canal de vídeo.")
                continue

            contador_leituras = 0
            
            # Sub-loop para processar o vídeo atual do bioma
            while cap.isOpened() and contador_leituras < MAX_LEITURAS_POR_BIOMA:
                ret, frame = cap.read()
                if not ret:
                    print("[REDE] Instabilidade no streaming ou fim do vídeo. Reiniciando conexões...")
                    break

                # Recupera dimensões físicas do frame atual
                altura, largura, _ = frame.shape

                # Recorte da Região de Interesse (ROI) - HUD do Termômetro
                y_inicio = int(altura * 0.75)
                y_fim = int(altura * 0.95)
                x_inicio = int(largura * 0.80)
                x_fim = int(largura * 0.98)
                hud_clima = frame[y_inicio:y_fim, x_inicio:x_fim]

                # =============================================================
                # GERADOR DINÂMICO DE TELEMETRIA
                # Usa uma função seno baseada no tempo + um ruído aleatório do sensor
                # para simular a oscilação térmica real do ambiente de jogo.
                # =============================================================
                tempo_decorrido = contador_leituras * 0.5
                fator_oscilacao = math.sin(tempo_decorrido) * config["variacao"]
# Adiciona uma pequena margem de erro típica de sensores reais (ex: DHT22)
                ruido_sensor = random.uniform(-0.4, 0.4) 
                
                temperatura_calculada = round(config["temp_base"] + fator_oscilacao + ruido_sensor, 2)

                # =============================================================
                # ENVIO DOS DADOS FORMATADOS VIA MQTT
                # =============================================================
                # Enviamos a String no formato CSV estruturado: "valor,bioma"
                payload = f"{temperatura_calculada},{nome_bioma}"
                
                try:
                    cliente_mqtt.publish(TOPICO_TEMPERATURA, payload, qos=1)
                    print(f"[PUBLISHER] Telemetria enviada -> {temperatura_calculada}°C | Origem: {nome_bioma}")
                except Exception as e:
                    print(f"[MQTT ERRO] Falha ao publicar payload: {e}")

                # Incrementa contador do bioma atual
                contador_leituras += 1

                # =============================================================
                # EXIBIÇÃO EM TELA (INTERFACE DO OPERADOR)
                # =============================================================
                # Renderiza textos informativos direto no frame principal do OpenCV
                cv2.putText(frame, f"Bioma: {nome_bioma}", (30, 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(frame, f"Telemetria: {temperatura_calculada} C", (30, 75), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

                # Exibe as janelas de monitoramento local
                cv2.imshow("Estacao de Monitoramento Principal - Hyrule", frame)
                cv2.imshow("ROI Isolada - Sensor HUD", hud_clima)

                # Escuta teclado: Se pressionar 'q', encerra toda a aplicação imediatamente
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n[SISTEMA] Interrupção manual acionada pelo usuário.")
                    raise KeyboardInterrupt

                # Intervalo de amostragem de dados (2 segundos)
                time.sleep(2)

            # Libera o canal do streaming atual para abrir espaço para o próximo bioma
            cap.release()
            cv2.destroyAllWindows()

except KeyboardInterrupt:
    print("\n[SISTEMA] Finalizando serviços e desconectando do Broker...")
finally:
    # Garante o encerramento limpo dos recursos de rede e de vídeo
    try:
        cliente_mqtt.loop_stop()
        cliente_mqtt.disconnect()
    except:
        pass
    print("[SISTEMA] Script do Publisher encerrado com sucesso.")
