import paho.mqtt.client as mqtt

# =========================================================================
# CONFIGURAÇÕES DO PROTOCOLO MQTT (BROKER HIVEMQ COM AUTENTICAÇÃO)
# =========================================================================
BROKER_MQTT = "6be44a2810bc469cb87c7054389b42e7.s1.eu.hivemq.cloud"  
PORTA_MQTT = 8883                 
TOPICO_TEMPERATURA = "hyrule/monitoramento/temperatura"
KEEPALIVE_MQTT = 60

# INSIRA SUAS CREDENCIAIS DO HIVEMQ AQUI (Devem ser as mesmas do Publisher):
USUARIO_HIVEMQ = "Zelda"
SENHA_HIVEMQ = "Tloz19862026"

# =========================================================================
# RECEBIMENTO DOS DADOS FORMATADOS VIA MQTT
# =========================================================================
try:
    print("[MQTT] Inicializando cliente...")
    cliente_mqtt = mqtt.Client()

    # Reconecta em caso de perda da conexão
    def on_connect(client, userdata, flags, reason_code):
        if reason_code == 0: 
            print("[MQTT] Conectado com sucesso ao broker HiveMQ!")
            try: 
                client.subscribe(TOPICO_TEMPERATURA)
                print(f"[MQTT] Inscrito com sucesso no tópico: {TOPICO_TEMPERATURA}")
            except Exception as e:
                print(f"[MQTT ERRO] Falha no subscribe: {e}")
        else:
            print(f"[MQTT] Falha na conexão. Código de retorno: {reason_code}")

    # Callback para quando a mensagem do publisher é recebida
    def on_message(client, userdata, message):
        try:
            text = message.payload.decode("utf-8")
            text = text.split(",")
            print(f"[SUBSCRIBER] Telemetria recebida -> Bioma: {text[1]}, Temperatura: {text[0]} °C")
        except Exception as e:
            print(f"[SUBSCRIBER ERRO] Falha ao processar mensagem recebida: {e}")

    # Atribuindo as funções de callback ao cliente
    cliente_mqtt.on_connect = on_connect 
    cliente_mqtt.on_message = on_message

    # Configurando a autenticação de usuário e senha antes de conectar
    if USUARIO_HIVEMQ and SENHA_HIVEMQ:
        cliente_mqtt.username_pw_set(USUARIO_HIVEMQ, SENHA_HIVEMQ)
        print("[MQTT] Credenciais de autenticação configuradas.")

    # Conecta ao broker de subscrição em nuvem
    try:
        print(f"[MQTT] Tentando conectar ao broker em nuvem ({BROKER_MQTT})...")
        cliente_mqtt.connect(BROKER_MQTT, PORTA_MQTT, KEEPALIVE_MQTT)
    except Exception as e:
        print(f"[MQTT] AVISO: Não foi possível conectar ao broker ({e}).")
        print("[MQTT] O script rodará em modo de simulação em espera.\n")

    # Inicia o loop para processar envio e recebimento de mensagens de forma contínua
    cliente_mqtt.loop_forever() 

except KeyboardInterrupt:
    print("\n[SISTEMA] Desconectando do Broker...")
finally:
    try:
        cliente_mqtt.disconnect()
    except:
        pass
    print("[SISTEMA] Script do Subscriber encerrado com sucesso.")
