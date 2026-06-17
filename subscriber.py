import paho.mqtt.client as mqtt

# =========================================================================
# CONFIGURAÇÕES DO PROTOCOLO MQTT
# =========================================================================
BROKER_MQTT = "localhost"
PORTA_MQTT = 1883
TOPICO_TEMPERATURA = "hyrule/monitoramento/temperatura"

# =============================================================
# RECEBIMENTO DOS DADOS FORMATADOS VIA MQTT
# =============================================================
try:
    print("[MQTT] Inicializando cliente...")
    cliente_mqtt = mqtt.Client() #Iniciando o cliente do subcriber

    # Reconecta em caso de perda da conexão
    def on_connect(client, userdata, flags, reason_code):
        if (reason_code == 0): 
            print("[MQTT] Conectado com sucesso ao broker local!")
            try: 
                client.subscribe(TOPICO_TEMPERATURA) #subscrição é renovada em caso de reconexão
            except Exception as e:
                print(f"[MQTT ERRO] Falha no subscribe: {e}")

    # Callback para quando a mensagem do publisher é recebida
    def on_message(client, userdata, message):
        text = message.payload.decode("utf-8") #Converte de binário para string
        text = text.split(",") #Separando os elementos da string separados por virgula
        print(f"[SUBSCRIBER] Telemetria recebida -> Bioma: {text[1]}, Temperatura: {text[0]} °C")

    # Atribuindo as funções ao cliente
    try:
        cliente_mqtt.on_connect = on_connect 
    except Exception as e:
        print(f"[MQTT ERRO] Falha na conexão: {e}")

    try:
        cliente_mqtt.on_message = on_message
    except Exception as e:
        print(f"[MQTT ERRO] Falha ao receber payload: {e}")

    # Conecta ao broker de subscrição
    try:
        cliente_mqtt.connect(BROKER_MQTT, PORTA_MQTT, 60)
    except Exception as e:
        print(f"[MQTT] AVISO: Não foi possível conectar ao broker ({e}).")
        print("[MQTT] O script continuará rodando em modo de simulação visual offline.\n")

    cliente_mqtt.loop_forever() #Inicia o loop para processar envio e recebimento de mensagens

except KeyboardInterrupt:
    print("\n[SISTEMA] Desconectando do Broker...")
finally:
    # Garante o encerramento limpo dos recursos de rede
    try:
        cliente_mqtt.disconnect()
    except:
        pass
    print("[SISTEMA] Script do Subscriber encerrado com sucesso.")