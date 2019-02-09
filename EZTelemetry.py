import paho.mqtt.client as mqtt
from global_vars import *
import datetime
import json, re
import os, time
import serial
import threading
import logging
import copy

channels = list()
types = list()

birth_topic = f"EZTelemetry/{org}/{group}/birth"
death_topic = f"EZTelemetry/{org}/{group}/death"
command_topic = f"EZTelemetry/{org}/{group}/{device_id}/command"
data_topic = f"EZTelemetry/{org}/{group}/{device_id}/data"

payload_base = None
ser = None


def load_channels():
	file = open("channels").readlines()
	for line in file:
		split = line.replace('\n', '').split(',')
		channels.append(split[0].replace(' ', '_'))
		types.append(split[1].replace(' ', ''))


def on_connect(client2, userdata, flags, rc):
	logging.info("Connected with result code " + str(rc))
	client.subscribe(birth_topic)
	client.subscribe(command_topic)
	client.subscribe(data_topic)


def on_message(client2, userdata, msg):
	topic = msg.topic
	if topic == command_topic:
		command = json.loads(msg.payload)


def add_data(payload, var_name, var_data):
	payload["data"][var_name] = var_data
	return payload


def publish_birth():
	global payload_base
	print("Publishing Birth")
	payload = {
		"meta": {
			"device_id": device_id,
			"group": group,
			"org": org
		},
		"data": {

		}
	}
	payload_base = copy.deepcopy(payload)
	for i in range(len(channels)):
		payload['data'][channels[i]] = types[i]
	total_byte_array = json.dumps(payload)
	client.publish(birth_topic, total_byte_array, 0, False)
	print(f"Sent birth packet {total_byte_array}")


def send_data(msg):
	try:
		dt = str(datetime.datetime.utcnow().isoformat())+'Z'
		client.publish(data_topic, msg, 0, False)
		logging.info(" [i] Data sent to the cloud \n")
	except Exception as e:
		print(e)
		logging.info(" [!] Can't send data to the cloud \n")
		fl = open(cache_file, "a+")
		fl.write(dt + " " + msg + "\n\n")
		fl.close()


def upload_cache():
	while True:
		try:
			os.system("find /tmp -name 'sed*' | xargs rm")
			dt = str(datetime.datetime.utcnow().isoformat())
			with open(cache_file) as read:
				for line in read:
					if line and len(line.strip()) != 0:
						ts = str(line.split(' ', 1)[0])
						line = line.split(' ', 1)[1]
						dt = str(datetime.datetime.utcnow().isoformat())
						byte_array = bytes(line, encoding="UTF-8")
						client.publish(data_topic, byte_array, 0, False)
						logging.info(" [i] Cached data sent !")
						os.system("sed -i '/" + ts + "/d' " + cache_file)
						time.sleep(1)
			time.sleep(1800)
		except Exception as e:
			logging.info(e)
			logging.info(" [i] Failed to send cached data")


def get_data():
	global ser
	publish_birth()
	while True:
		client.loop()
		try:
			# Get timestamp
			dt = str(datetime.datetime.utcnow().isoformat())+'Z'
			if not ser:
				if IP_enabled:
					ser = serial.serial_for_url("socket://" + str(IP) + ":" + str(Port) + "/logging=debug",
												timeout=int(IP_timeout))
				elif Serial_enabled:
					ser = serial.Serial(
						port=Address,
						baudrate=Baud,
						parity=serial.PARITY_NONE,
						stopbits=serial.STOPBITS_ONE,
						bytesize=serial.EIGHTBITS,
						timeout=Serial_timeout,
						write_timeout=10)
			data = ser.readline()
			logging.info("\n Data received")
			logging.info(data)
			encode = str(data, encoding='utf8').rstrip()
			encode = encode.replace(' ', '')

			if encode:
				tf = open('/var/log/ez-telemetry.log', "a+")
				tf.write(encode + '\n')
				tf.close()
				logging.info('Attempting to encode data')

				data_prep = re.split(r'[,|;"\t]+', encode)
				data_prep = [item.strip() for item in data_prep if item]

				serial_payload = copy.deepcopy(payload_base)
				for i in range(len(data_prep)):
					if types[i] == 'String':
						serial_payload['data'][channels[i]] = data_prep[i]
					elif types[i] == 'Double':
						serial_payload['data'][channels[i]] = float(data_prep[i])

				msg = json.dumps(serial_payload)
				logging.info(msg + "\n")
				if len(data_prep) == len(channels):
					send_thread = threading.Thread(target=send_data(msg), args=(msg,))
					send_thread.start()
				else:
					logging.info('Wrong data stream format - have ' + str(len(data_prep)) + ' channels')
			else:
				logging.info(" [!] Empty data received !")
		except serial.SerialException as e:
			logging.info(e)
			ser = None
			logging.info(" [!] No data was received .. Retrying in 10 seconds")
			time.sleep(10)


load_channels()
logging.info(channels)

# MQTT initialization
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

death_byte_array = bytearray(json.dumps(payload_base), encoding="UTF-8")
client.will_set(death_topic, death_byte_array, 0, False)
client.connect(server_url, server_port, 60)
time.sleep(.1)
get_data()
