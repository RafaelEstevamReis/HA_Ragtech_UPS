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
cfg_mqtt_interval = config["serial"].get("interval", 5)

# Configuração Serial
cfg_serial_port = config["serial"]["port"]
cfg_serial_interval = config["serial"].get("interval", 5)

# payloads
cmd_req1 = bytes.fromhex("FF FE 00 8E 01 8F")
cmd_req2 = bytes.fromhex("AA 04 00 80 1E 9E")
cmd_get_data = bytes.fromhex("AA 04 00 80 1E 9E")

power_current_kwh_out = 0.0
power_current_kwh_in = 0.0
power_last_update = time.time()

def logData(text, end):
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%d/%b/%Y %H:%M:%S")
    if end:
        print(f"[{formatted_datetime}] {text}", end=" ")
    else:
        print(f"[{formatted_datetime}] {text}")

def linear(val, a, b, decimals = 1):
    return round(b + val * a, decimals)

def processPower(wOut, wIn):
    global power_last_update
    global power_current_kwh_out
    global power_current_kwh_in

    curr = time.time()
    diff = curr - power_last_update # in seconds
    power_last_update = curr

    slice = (wOut / 1000) * (diff / 3600)
    power_current_kwh_out += slice
    
    slice = (wIn / 1000) * (diff / 3600)
    power_current_kwh_in += slice

def build_payload(buffer):
    iOut = linear(buffer[0x0D], 0.1152, 0, 2)

    vOut = linear(buffer[0x1E], 0.555, 0, 2)
    wOut = iOut*vOut

    vIn = linear(buffer[0x0C], 1.06, 0, 2)
    wIn = iOut*vIn # não tem "iIn"

    processPower(wOut, wIn)

    payload = {
        "Power_Out_Percent": {"value": linear(buffer[0x0E], 1, 0), "unit": "%"},
        "Current_Out": {"value": iOut, "unit": "A"},
        "Voltage_Out": {"value": round(vOut, 1), "unit": "V"},
        "Voltage_In": {"value": round(vIn, 1), "unit": "V"},
        "Power_Out": {"value": round(wOut, 1), "unit": "W"},
        "Power_In": {"value": round(wIn, 1), "unit": "W"},
        "Energy_Out": {"value": round(power_current_kwh_out, 2), "unit": "kWh"},
        "Energy_In": {"value": round(power_current_kwh_in, 2), "unit": "kWh"},
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
    logData(f"serial open: {cfg_serial_port}", False)
    serial_port = serial.Serial(cfg_serial_port)
    if serial_port.isOpen():
        logData(serial_port.name + " is open…", False)
    else:
        logData(f"serial fail: {ret}", False)
        time.sleep(10)
        return

    # Configuração do cliente MQTT
    mqtt_client = mqtt.Client("rups2mqtt")

    # Se houver informações de autenticação, configure-as
    if mqtt_username and mqtt_password:
        mqtt_client.username_pw_set(mqtt_username, mqtt_password)
        logData("Using Username+Password", False)

    logData("Connecting to " + mqtt_address + ":" + str(mqtt_port), False)
    ret = mqtt_client.connect(mqtt_address, mqtt_port, 15)
    if ret != 0:
        logData(f"mqtt fail: {ret}", False)
        time.sleep(10)
        return

    # Função para enviar e ignorar resposta
    logData(f"Starting Serial", False)
    send_and_ignore(serial_port, cmd_req1)
    logData(f"Sent CMD1", False)

    send_and_ignore(serial_port, cmd_req2)
    logData(f"Sent CMD2", False)

    while True:
        time.sleep(cfg_serial_interval)

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
                return
        
        logData("MQTT Sent", False)

while True:
    mainLoop()
