import configparser
import logging
import time

config = configparser.ConfigParser()
config.read("config.ini")

logging.Formatter.converter = time.gmtime
logging.basicConfig(filename="/var/log/stream.log", level=logging.INFO, format='%(asctime)s:%(message)s')
# Creating cache file
cache_file = "/tmp/json.cache"

IP_enabled = config.get('TCP', 'Enabled') == "True"
IP = config.get('TCP', 'IP')
Port = int(config.get('TCP', 'Port'))
IP_timeout = int(config.get('TCP', 'Timeout'))

Serial_enabled = config.get('Serial', 'Enabled') == "True"
Address = config.get('Serial', 'Address')
Baud = int(config.get('Serial', 'Baud'))
Serial_timeout = int(config.get('Serial', 'Timeout'))

server_url = config.get("MQTT", "Broker")
server_port = int(config.get("MQTT", "Port"))
org = config.get("MQTT", "Org").replace('/','').replace('"', '')
group = config.get("MQTT", "Group").replace('/','').replace('"', '')
device_id = config.get("MQTT", "DeviceID").replace('/','').replace('"', '')

opc_url = config.get("Server", "IP")
