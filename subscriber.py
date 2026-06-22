import ssl

import paho.mqtt.client as mqtt

# =========================================================================
# CONFIGURAÇÕES DO PROTOCOLO MQTT (BROKER HIVEMQ CLOUD SECURE)
# =========================================================================
BROKER_MQTT = "6be44a2810bc469cb87c7054389b42e7.s1.eu.hivemq.cloud"  
PORTA_MQTT = 8883                 
TOPICO_TEMPERATURA = "hyrule/monitoramento/temperatura"
KEEPALIVE_MQTT = 60

# INSERIR AS CREDENCIAIS CRIADAS NO PAINEL DO HIVEMQ CLOUD:
USUARIO_HIVEMQ = "Zelda"
SENHA_HIVEMQ = "Tloz19862026"

# =========================================================================
# RECEBIMENTO DOS DADOS FORMATADOS VIA MQTT
# =========================================================================

print("[MQTT] Inicializando cliente...")
cliente_mqtt = mqtt.Client()

# Reconecta em caso de perda da conexão
def on_connect(client, userdata, flags, reason_code):
    if reason_code == 0: 
        print("[MQTT] Conectado com sucesso ao broker HiveMQ Cloud!")
        try: 
            client.subscribe(TOPICO_TEMPERATURA)
            print(f"[MQTT] Inscrito com sucesso no tópico: {TOPICO_TEMPERATURA}")
        except Exception as e:
            print(f"[MQTT ERRO] Falha no subscribe: {e}")
    else:
        print(f"[MQTT] Falha na conexão. Código de erro/retorno: {reason_code}")

def on_message(client, userdata, message): #Formatando o texto
    text = message.payload.decode("utf-8")
    dados = text.split(",") 

    if len(dados) != 2: #Para o caso de não ter vírgula
        print(f"[SUBSCRIBER] Mensagem inválida recebida: {text}")
        return

    temperatura = dados[0]
    bioma = dados[1]

    print(
        f"[SUBSCRIBER] Telemetria recebida -> "
        f"Bioma: {bioma}, Temperatura: {temperatura} °C"
    )

# Atribuindo as funções de callback ao cliente
cliente_mqtt.on_connect = on_connect
cliente_mqtt.on_message = on_message

# 1. Configura as credenciais de usuário e senha
if USUARIO_HIVEMQ and SENHA_HIVEMQ:
    cliente_mqtt.username_pw_set(USUARIO_HIVEMQ, SENHA_HIVEMQ)
    print("[MQTT] Credenciais de autenticação configuradas.")
    
# 2. ATIVA A SEGURANÇA TLS
cliente_mqtt.tls_set(cert_reqs=ssl.CERT_REQUIRED)
print("[MQTT] Segurança TLS/SSL ativada para conexão em nuvem.")

# Conecta ao broker de subscrição seguro
try:
    cliente_mqtt.connect(BROKER_MQTT, PORTA_MQTT, KEEPALIVE_MQTT)
except Exception as e:
    print(f"[MQTT ERRO] Não foi possível conectar ao broker: {e}")
    exit(1)

try:
    cliente_mqtt.loop_forever()     # Inicia o loop eterno de escuta
except KeyboardInterrupt:
    print("\n[SISTEMA] Desconectando do Broker...")
finally:
    cliente_mqtt.disconnect()
    print("[SISTEMA] Script do Subscriber encerrado com sucesso.")
