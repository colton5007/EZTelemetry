import configparser
import logging
import time

config = configparser.ConfigParser()
config.read("/etc/config.ini")

logging.Formatter.converter = time.gmtime
logging.basicConfig(filename = "/var/log/stream.log", level=logging.INFO, format='%(asctime)s:%(message)s')
# Creating cache file
cache_file = "/tmp/json.cache"

IP_enabled = config.get('TCP', 'Enabled')
IP = config.get('TCP', 'IP')
Port = config.get('TCP', 'Port')
IP_timeout = config.get('TCP', 'Timeout')

Serial_enabled = config.get('Serial', 'Enabled')
Address = config.get('Serial', 'Location')
Baud = config.get('Serial', 'Baud')
Serial_timeout = config.get('Serial', 'Timeout')

server_url = config.get("MQTT", "Broker")
server_port = config.get("MQTT", "Port")
org = config.get("MQTT", "Org")
group = config.get("MQTT", "Group")
device_id = config.get("MQTT", "DeviceID")
