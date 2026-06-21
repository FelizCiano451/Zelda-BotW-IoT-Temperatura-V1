import time
import math
import random
import paho.mqtt.client as mqtt

# =========================================================================
# 1. CONFIGURAÇÕES DO PROTOCOLO MQTT (BROKER HIVEMQ COM AUTENTICAÇÃO)
# =========================================================================
BROKER_MQTT = "6be44a2810bc469cb87c7054389b42e7.s1.eu.hivemq.cloud"
PORTA_MQTT = 8883                  
TOPICO_TEMPERATURA = "hyrule/monitoramento/temperatura"
KEEPALIVE_MQTT = 60

# INSIRA SUAS CREDENCIAIS DO HIVEMQ AQUI:
USUARIO_HIVEMQ = "Zelda"
SENHA_HIVEMQ = "Tloz19862026"

print("[MQTT] Inicializando cliente...")
cliente_mqtt = mqtt.Client()

# Configurando a autenticação de usuário e senha
if USUARIO_HIVEMQ and SENHA_HIVEMQ:
    cliente_mqtt.username_pw_set(USUARIO_HIVEMQ, SENHA_HIVEMQ)
    print("[MQTT] Credenciais de autenticação configuradas.")

try:
    print(f"[MQTT] Tentando conectar ao broker em nuvem ({BROKER_MQTT})...")
    cliente_mqtt.connect(BROKER_MQTT, PORTA_MQTT, KEEPALIVE_MQTT)
    cliente_mqtt.loop_start()
    print("[MQTT] Conectado com sucesso ao broker HiveMQ!")
except Exception as e:
    print(f"[MQTT] AVISO: Não foi possível conectar ao broker ({e}).")
    print("[MQTT] O script continuará rodando em modo offline.\n")

# =========================================================================
# 2. DICIONÁRIO DE BIOMAS (Configurações Térmicas)
# =========================================================================
BIOMAS_ZELDA = {
    "Planicie de Hyrule (Temperado)": {
        "temp_base": 25.0,
        "variacao": 4.0
    },
    "Montanha da Morte (Quente)": {
        "temp_base": 50.0,
        "variacao": 6.0
    },
    "Montanhas de Hebra (Gelado)": {
        "temp_base": -10.0,
        "variacao": 5.0
    }
}

# Quantidade de leituras simuladas antes de trocar automaticamente de ambiente
MAX_LEITURAS_POR_BIOMA = 15 

# =========================================================================
# 3. LOOP PRINCIPAL - TRANSIÇÃO SIMULADA ENTRE BIOMAS
# =========================================================================
try:
    while True:
        for nome_bioma, config in BIOMAS_ZELDA.items():
            print("\n" + "="*60)
            print(f"[AMBIENTE] Alterando sensor para o bioma: {nome_bioma}")
            print("="*60)
            
            contador_leituras = 0
            
            # Sub-loop para processar as leituras do bioma atual
            while contador_leituras < MAX_LEITURAS_POR_BIOMA:
                
                # =============================================================
                # GERADOR DINÂMICO DE TELEMETRIA
                # =============================================================
                tempo_decorrido = contador_leituras * 0.5
                fator_oscilacao = math.sin(tempo_decorrido) * config["variacao"]
                ruido_sensor = random.uniform(-0.4, 0.4) 
                
                temperatura_calculada = round(config["temp_base"] + fator_oscilacao + ruido_sensor, 2)

                # =============================================================
                # ENVIO DOS DADOS FORMATADOS VIA MQTT
                # =============================================================
                payload = f"{temperatura_calculada},{nome_bioma}"
                
                try:
                    cliente_mqtt.publish(TOPICO_TEMPERATURA, payload, qos=1)
                    print(f"[PUBLISHER] Telemetria enviada -> {temperatura_calculada}°C | Origem: {nome_bioma}")
                except Exception as e:
                    print(f"[MQTT ERRO] Falha ao publicar payload: {e}")

                contador_leituras += 1
                time.sleep(2)

except KeyboardInterrupt:
    print("\n[SISTEMA] Interrupção manual acionada pelo usuário.")
finally:
    try:
        cliente_mqtt.loop_stop()
        cliente_mqtt.disconnect()
    except:
        pass
    print("[SISTEMA] Script do Publisher encerrado com sucesso.")
