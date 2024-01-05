import serial
import time
import datetime
import paho.mqtt.client as mqtt
import yaml
import json

## Carrega informações
# Carrega as configurações do arquivo YAML
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

## Prepara globais 
# Configuração MQTT
device_id = config["mqtt"]["device_id"]
mqtt_address = config["mqtt"]["host"]
mqtt_port = config["mqtt"]["port"]
mqtt_username = config["mqtt"].get("user", None)
mqtt_password = config["mqtt"].get("password", None)

# Configuração Serial
cfg_serial_port = config["serial"]["port"]

# payloads
cmd_req1 = bytes.fromhex("FF FE 00 8E 01 8F")
cmd_req2 = bytes.fromhex("AA 04 00 80 1E 9E")
cmd_get_data = bytes.fromhex("AA 04 00 80 1E 9E")

def logData(text, end):
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%d/%b/%Y %H:%M:%S")
    if end:
        print(f"[{formatted_datetime}] {text}", end=" ")
    else:
        print(f"[{formatted_datetime}] {text}")

def linear(val, a, b):
    return round(b + val * a, 1)

def build_payload(buffer):
    iOut = linear(buffer[0x0D], 0.1152, 0)
    vOut = linear(buffer[0x1E], 0.555, 0)
    payload = {
        "Power_Out_Percent": {"value": linear(buffer[0x0E], 1, 0), "unit": "%"},
        "Current_Out": {"value": iOut, "unit": "A"},
        "Voltage_Out": {"value": vOut, "unit": "V"},
        "Voltage_In": {"value": linear(buffer[0x0C], 1.06, 0), "unit": "V"},
        "Power_Out": {"value": round(iOut*vOut, 1), "unit": "W"},
        "Temperature": {"value": linear(buffer[0x0F], 1, 0), "unit": "C"},
        "Battery_State": {"value": linear(buffer[0x08], 0.392, 0), "unit": "%"},
        "Battery_Voltage": {"value": linear(buffer[0x0B], 0.0671, 0), "unit": "V"},
        "Frequency": {"value": linear(buffer[0x18], -0.1152, 65), "unit": "Hz"},
    }

    return payload

def send_and_ignore(serial_port, command, wait_time=0.1):
    while True:
        serial_port.write(command)
        time.sleep(wait_time)
        if serial_port.in_waiting > 0:
            logData(str(serial_port.in_waiting)+" Available", False)
            serial_port.read()
            return
        logData("No response ...", False)

def mainLoop():
    # Configuração da porta serial
    serial_port = serial.Serial(cfg_serial_port)
    if serial_port.isOpen():
        logData(serial_port.name + " is open…", False)

    # Configuração do cliente MQTT
    mqtt_client = mqtt.Client("rups2mqtt")

    # Se houver informações de autenticação, configure-as
    if mqtt_username and mqtt_password:
        mqtt_client.username_pw_set(mqtt_username, mqtt_password)
        logData("Using Username+Password", False)

    logData("Connecting to " + mqtt_address + ":" + str(mqtt_port), False)
    mqtt_client.connect(mqtt_address, mqtt_port, 15)

    # Função para enviar e ignorar resposta
    logData(f"Starting Serial", False)
    send_and_ignore(serial_port, cmd_req1)
    logData(f"Sent CMD1", False)

    send_and_ignore(serial_port, cmd_req2)
    logData(f"Sent CMD2", False)

    while True:
        time.sleep(4.9)

        # Limpa
        while serial_port.in_waiting > 0:
            serial_port.read()

        serial_port.write(cmd_get_data)
        logData(f"Requesting Data... ", True)

        wait = 100
        while serial_port.in_waiting < 31:
            time.sleep(0.1)
            print(serial_port.in_waiting, end=" ")
            wait-=1
            if(wait <= 0):
                break
        print()

        if(wait <= 0):
            logData(f"STOPPED", False)
            continue

        time.sleep(0.1)
        buffer = serial_port.read(serial_port.in_waiting)

        # Monta o payload
        payload = build_payload(buffer)

        strPayload = json.dumps(payload)
        logData(strPayload, False)
        
        for key, value in payload.items():
            topic = f"home/ups/{device_id}/{key}"
            ret = mqtt_client.publish(topic, json.dumps(value))
            if ret[0] != 0:
                logData(f"mqtt err: {ret}", False)
        
        logData("MQTT Sent", False)

while True:
    mainLoop()
