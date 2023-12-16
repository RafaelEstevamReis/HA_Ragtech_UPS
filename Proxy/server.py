import serial
import time
import paho.mqtt.client as mqtt
import yaml
import json

def linear(val, a, b):
    return round(b + val * a, 1)

def read_config():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config

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
            print(str(serial_port.in_waiting)+" Available")
            serial_port.read()
            return
        print("No response ...")

# Carrega as configurações do arquivo YAML
config = read_config()

# Configuração da porta serial
serial_port = serial.Serial(config["serial"]["port"])
if serial_port.isOpen():
    print(serial_port.name + " is open…")

# Configuração MQTT
device_id = config["mqtt"]["device_id"]
mqtt_address = config["mqtt"]["host"]
mqtt_port = config["mqtt"]["port"]
mqtt_username = config["mqtt"].get("user", None)
mqtt_password = config["mqtt"].get("password", None)

# Configuração do cliente MQTT
mqtt_client = mqtt.Client("rups2mqtt")

# Se houver informações de autenticação, configure-as
if mqtt_username and mqtt_password:
    mqtt_client.username_pw_set(mqtt_username, mqtt_password)
    print("Using Username+Password")

print("Connecting to " + mqtt_address + ":" + str(mqtt_port))
mqtt_client.connect(mqtt_address, mqtt_port, 15)

cmd_req1 = bytes.fromhex("FF FE 00 8E 01 8F")
cmd_req2 = bytes.fromhex("AA 04 00 80 1E 9E")
cmd_get_data = bytes.fromhex("AA 04 00 80 1E 9E")

# Função para enviar e ignorar resposta
print("Starting Serial")
send_and_ignore(serial_port, cmd_req1)
print("Sent CMD1")

send_and_ignore(serial_port, cmd_req2)
print("Sent CMD2")

while True:
    time.sleep(0.9)

    # Limpa
    while serial_port.in_waiting > 0:
        serial_port.read()

    serial_port.write(cmd_get_data)
    print("\nRequesting Data... ", end=" ")

    wait = 100
    while serial_port.in_waiting < 31:
        time.sleep(0.1)
        print(serial_port.in_waiting, end=" ")
        wait-=1
        if(wait <= 0):
            break
    if(wait <= 0):
        print("STOPPED")
        continue

    print()
    time.sleep(0.1)
    buffer = serial_port.read(serial_port.in_waiting)

    # Monta o payload
    payload = build_payload(buffer)

    device_name = "Nobreak Ragtech"
    for key, value in payload.items():
        topic = f"home/ups/{device_id}/{key}"
        mqtt_client.publish(topic, json.dumps(value))

    print(json.dumps(payload))

