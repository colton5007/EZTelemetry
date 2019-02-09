from threading import Thread
import paho.mqtt.client as mqtt
import copy
import logging
from datetime import datetime
import time
from math import sin
from global_vars import *
import sys
import json
import threading
sys.path.insert(0, "..")

try:
    from IPython import embed
except ImportError:
    import code

    def embed():
        myvars = globals()
        myvars.update(locals())
        shell = code.InteractiveConsole(myvars)
        shell.interact()


from opcua import ua, uamethod, Server

birth_topic = f"EZTelemetry/{org}/{group}/birth"
death_topic = f"EZTelemetry/{org}/{group}/death"
devices = list()


class Device:
    def __init__(self, data):
        self.id = data["meta"]["device_id"]
        self.types = data["data"]
        self.dev = server.nodes.base_object_type.add_object_type(idx, self.id)
        self.vars = dict()
        for key, value in data['data'].items():
            if value == "String":
                v = self.dev.add_variable(idx, key, "")
                self.vars[key] = v
            else:
                v = self.dev.add_variable(idx, key, 0)
                self.vars[key] = v
        self.dev.add_property(0, "device_id", self.id)
        device_folder.add_object(idx, self.id, self.dev)
        client.subscribe(data_topic(self.id))


def data_topic(dd):
    return f"EZTelemetry/{org}/{group}/{dd}/data"


def command_topic(dd):
    return f"EZTelemetry/{org}/{group}/{dd}/command"


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(birth_topic)
    client.subscribe(death_topic)


def on_message(client, userdata, msg):
    topic = msg.topic
    data = json.loads(msg.payload)
    if topic == birth_topic:
        print("Adding device")
        devices.append(Device(data))
    if topic == death_topic:
        pass
    else:
        data = json.loads(msg.payload)
        for device in devices:
            if device.id == data['meta']['device_id']:
                d = data['data']
                for key in d:
                    device.vars[key].set_value(data['data'][key])


def loop():
    while True:
        client.loop()


if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(server_url, server_port, 60)
    time.sleep(.1)
    send_thread = threading.Thread(target=loop)
    send_thread.start()

    server = Server()
    server.set_endpoint(f"opc.tcp://{opc_url}:4840/eztelemetry/server/")
    server.set_server_name("EZTelemetry")
    # set all possible endpoint policies for clients to connect through
    server.set_security_policy([
                ua.SecurityPolicyType.NoSecurity,
                ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
                ua.SecurityPolicyType.Basic256Sha256_Sign])

    # setup our own namespace
    uri = "http://colton.levelops.com"
    idx = server.register_namespace(uri)
    # populating our address space

    # First a folder to organise our nodes
    device_folder = server.nodes.objects.add_folder(idx, "Devices")
    # starting!
    server.start()
