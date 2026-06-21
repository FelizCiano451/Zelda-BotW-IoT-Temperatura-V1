import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime

# =========================================================================
# CONFIGURAÇÕES DO PROTOCOLO MQTT (VERSÃO HIVEMQ CLOUD PRIVADO)
# =========================================================================
BROKER_MQTT = "6be44a2810bc469cb87c7054389b42e7.s1.eu.hivemq.cloud"
PORTA_MQTT = 8883                                   
TOPICO_TEMPERATURA = "hyrule/monitoramento/temperatura"

# Credenciais criadas no painel da HiveMQ
USUARIO_MQTT = "Zelda"
SENHA_MQTT = "Tloz19862026"

# =========================================================================
# ESTRUTURAS DE ARMAZENAMENTO
# =========================================================================
# Listas globais para armazenar o histórico dos dados para o gráfico
tempos = []
temperaturas = []
bioma_atual = "Aguardando Publisher..."

# =============================================================
# RECEBIMENTO DOS DADOS FORMATADOS VIA MQTT
# =============================================================
try:
    print("[MQTT] Inicializando cliente (API V2)...")
    # Correção de compatibilidade para a versão recente do paho-mqtt
    cliente_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    cliente_mqtt.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS_CLIENT)
    cliente_mqtt.username_pw_set(USUARIO_MQTT, SENHA_MQTT)
    
    # Callback de conexão atualizado para a API v2
    def on_connect(client, userdata, flags, reason_code, properties=None):
        if reason_code == 0: 
            print("[MQTT] Conectado com sucesso ao HiveMQ!")
            try: 
                client.subscribe(TOPICO_TEMPERATURA)
                print(f"[MQTT] Inscrição confirmada no tópico: {TOPICO_TEMPERATURA}")
            except Exception as e:
                print(f"[MQTT ERRO] Falha no subscribe: {e}")
        else:
            print(f"[MQTT ERRO] Falha na conexão. Código de retorno: {reason_code}")

    # Callback para quando a mensagem do publisher é recebida
    def on_message(client, userdata, message):
        global bioma_atual
        try:
            text = message.payload.decode("utf-8") # Converte de binário para string
            dados = text.split(",") # Separando os elementos da string por vírgula
            
            val_temperatura = float(dados[0])
            bioma_atual = dados[1]

            print(f"[SUBSCRIBER] Telemetria recebida -> Bioma: {bioma_atual}, Temperatura: {val_temperatura} °C")

            # Alimenta as listas do gráfico histórico ao longo do tempo
            tempos.append(datetime.now().strftime('%H:%M:%S'))
            temperaturas.append(val_temperatura)
            
            # Mantém apenas as últimas 20 leituras para o gráfico não poluir
            if len(tempos) > 20:
                tempos.pop(0)
                temperaturas.pop(0)

        except Exception as e:
            print(f"[SISTEMA ERRO] Erro ao processar payload recebido: {e}")

    # Atribuindo os callbacks ao cliente
    cliente_mqtt.on_connect = on_connect 
    cliente_mqtt.on_message = on_message

    # Conecta ao broker de subscrição
    try:
        cliente_mqtt.connect(BROKER_MQTT, PORTA_MQTT, 60)
    except Exception as e:
        print(f"[MQTT] AVISO: Não foi possível conectar ao broker ({e}).")
        print("[MQTT] Verifique se o serviço do Mosquitto está ativo no seu PC.\n")

    # Usamos loop_start() em vez de loop_forever() para permitir que o Python
    # gerencie a janela do gráfico do Matplotlib na thread principal
    cliente_mqtt.loop_start()

    # =============================================================
    # CONFIGURAÇÃO DO DASHBOARD GRÁFICO (Evolução ao longo do tempo)
    # =============================================================
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.canvas.manager.set_window_title("Dashboard IoT - Telemetria de Hyrule")

    def atualizar_grafico(frame):
        if not temperaturas:
            return
        
        ax.clear()
        # Desenha a linha de evolução da temperatura
        ax.plot(tempos, temperaturas, marker='o', color='darkviolet', linestyle='-', linewidth=2)
        
        # Estilização do Gráfico
        plt.title("Estação Meteorológica Virtual - Monitoramento Temporal", fontsize=12, fontweight='bold')
        plt.ylabel("Temperatura (°C)", fontsize=10)
        plt.xlabel("Tempo de Coleta (HH:MM:SS)", fontsize=10)
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, linestyle='--', alpha=0.6)
        
        # Caixa de texto estática mostrando o Bioma Atual detectado pelo Publisher
        ax.text(0.02, 0.95, f"Bioma Atual: {bioma_atual}", 
                transform=ax.transAxes, fontsize=11, fontweight='bold',
                verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7))
        
        plt.tight_layout()

    # Animação que redesenha o gráfico a cada 1 segundo
    anim = FuncAnimation(fig, atualizar_grafico, interval=1000, cache_frame_data=False)
    plt.show()

except KeyboardInterrupt:
    print("\n[SISTEMA] Interrupção manual detectada. Desconectando do Broker...")
finally:
    try:
        cliente_mqtt.loop_stop()
        cliente_mqtt.disconnect()
    except:
        pass
    print("[SISTEMA] Script do Subscriber encerrado com sucesso.")
