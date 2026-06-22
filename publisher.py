import time
import math
import random
import paho.mqtt.client as mqtt
import ssl  # Garantindo a importação para suporte a TLS/SSL

# =========================================================================
# 1. CONFIGURAÇÕES DO PROTOCOLO MQTT (BROKER HIVEMQ CLOUD SECURE)
# =========================================================================
BROKER_MQTT = "6be44a2810bc469cb87c7054389b42e7.s1.eu.hivemq.cloud"  
PORTA_MQTT = 8883                  
TOPICO_TEMPERATURA = "hyrule/monitoramento/temperatura"
KEEPALIVE_MQTT = 60

# INSIRir AS CREDENCIAIS CRIADAS NO PAINEL DO HIVEMQ CLOUD:
USUARIO_HIVEMQ = "Zelda"
SENHA_HIVEMQ = "Tloz19862026"

print("[MQTT] Inicializando cliente...")
cliente_mqtt = mqtt.Client()

# A. Configura as credenciais de usuário e senha
if USUARIO_HIVEMQ and SENHA_HIVEMQ:
    cliente_mqtt.username_pw_set(USUARIO_HIVEMQ, SENHA_HIVEMQ)
    print("[MQTT] Credenciais de autenticação configuradas.")

# B. ATIVA A SEGURANÇA TLS
cliente_mqtt.tls_set(cert_reqs=ssl.CERT_REQUIRED)
print("[MQTT] Segurança TLS/SSL ativada para conexão em nuvem.")

try:
    print(f"[MQTT] Tentando conectar de forma segura ao cluster ({BROKER_MQTT})...")
    cliente_mqtt.connect(BROKER_MQTT, PORTA_MQTT, KEEPALIVE_MQTT)
    cliente_mqtt.loop_start()
    print("[MQTT] Conectado com sucesso ao broker HiveMQ!")
except Exception as e:
    print(f"[MQTT] AVISO: Não foi possível conectar ao broker ({e}).")
    print("[MQTT] O script continuará rodando em modo offline.\n")

# =========================================================================
# 2. DICIONÁRIO DE BIOMAS EXPANDIDO (6 Ambientes de Hyrule)
# =========================================================================
# Mapeia cada região para sua respectiva faixa de temperatura base e variação
BIOMAS_ZELDA = {
    "Planicie de Hyrule (Temperado)": {
        "temp_base": 25.0,
        "variacao": 4.0
    },
    "Montanha da Morte (Calor Vulcanico)": {
        "temp_base": 52.0,
        "variacao": 5.0
    },
    "Montanhas de Hebra (Gelado Alpino)": {
        "temp_base": -12.0,
        "variacao": 4.0
    },
    "Deserto Gerudo (Calor Diurno)": {
        "temp_base": 41.0,
        "variacao": 4.5
    },
    "Deserto Gerudo (Gelo Noturno)": {
        "temp_base": -2.0,
        "variacao": 3.0
    },
    "Regiao de Lanayru (Subtropical/Umido)": {
        "temp_base": 22.0,
        "variacao": 2.5
    }
}

# Quantidade de leituras simuladas antes de trocar automaticamente de ambiente
MAX_LEITURAS_POR_BIOMA = 15 

# =========================================================================
# 3. LOOP PRINCIPAL - TRANSIÇÃO SIMULADA ENTRE BIOMAS
# =========================================================================
try:
    while True:  # Loop infinito para manter o monitoramento contínuo
        for nome_bioma, config in BIOMAS_ZELDA.items():
            print("\n" + "="*60)
            print(f"[AMBIENTE] Alterando sensor para o bioma: {nome_bioma}")
            print("="*60)
            
            contador_leituras = 0
            
            # Sub-loop para processar as leituras do bioma atual
            while contador_leituras < MAX_LEITURAS_POR_BIOMA:
                
                # =============================================================
                # GERADOR DINÂMICO DE TELEMETRIA
                # Usa a função seno baseada no tempo + ruído aleatório do sensor
                # =============================================================
                tempo_decorrido = contador_leituras * 0.5
                fator_oscilacao = math.sin(tempo_decorrido) * config["variacao"]
                
                # Adiciona uma pequena margem de erro típica de sensores reais 
                ruido_sensor = random.uniform(-0.4, 0.4) 
                
                temperatura_calculada = round(config["temp_base"] + fator_oscilacao + ruido_sensor, 2)

                # =============================================================
                # ENVIO DOS DADOS FORMATADOS VIA MQTT
                # =============================================================
                # Formato CSV estruturado herdado da base: "valor,bioma"
                payload = f"{temperatura_calculada},{nome_bioma}"
                
                try:
                    cliente_mqtt.publish(TOPICO_TEMPERATURA, payload, qos=1)
                    print(f"[PUBLISHER] Telemetria enviada -> {temperatura_calculada}°C | Origem: {nome_bioma}")
                except Exception as e:
                    print(f"[MQTT ERRO] Falha ao publicar payload: {e}")

                # Incrementa contador do bioma atual
                contador_leituras += 1

                # Intervalo de amostragem de dados estável (2 segundos)
                time.sleep(2)

except KeyboardInterrupt:
    print("\n[SISTEMA] Interrupção manual acionada pelo usuário.")
finally:
    # Garante o encerramento limpo dos recursos de rede
    try:
        cliente_mqtt.loop_stop()
        cliente_mqtt.disconnect()
    except:
        pass
    print("[SISTEMA] Script do Publisher encerrado com sucesso.")
