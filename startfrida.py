import os
import sys
import subprocess
from contextlib import suppress
import json

from ppadb.client import Client as AdbClient

with open("config/config.json") as f:
    config = json.load(f)

if os.path.isfile("C:\\ProgramData\\BlueStacks_nxt\\bluestacks.conf"):
    with open("C:\\ProgramData\\BlueStacks_nxt\\bluestacks.conf", encoding="utf-8") as f:
        s = f.read()
    t = s
    t = t.replace('bst.feature.rooting="0"', 'bst.feature.rooting="1"')
    t = t.replace('.enable_root_access="0"', '.enable_root_access="1"')
    if t != s:
        with open("C:\\ProgramData\\BlueStacks_nxt\\bluestacks.conf", "w", encoding="utf-8") as f:
            f.write(t)

server_port = config["server"]["port"]
default_ports = [16384, 7555, 5555]
ADB_PATH = "platform-tools\\adb.exe"

def get_device():
    devices = client.devices()
    if len(devices) == 0:
        for port in default_ports:
            with suppress(Exception):
                client.remote_connect("127.0.0.1", port)
                devices = client.devices()
                if len(devices) == 1:
                    return devices[0]
        
        print("No emulator found.\nEnter the adb connection url with port manually or type q to exit or press enter to wait for a device: ")
        result = input()
        if result.lower() == "q":
            sys.exit(0)
        
        if result:
            result = result.split(":")
            client.remote_connect(result[0], int(result[1]))

    devices = client.devices()
    if len(devices) == 1:
        return devices[0]

os.system('cls')
# subprocess.run(f'"{ADB_PATH}" kill-server')
subprocess.run(f'"{ADB_PATH}" start-server')
    
client = AdbClient(host="127.0.0.1", port=5037)
device = None

print("Trying to connect to currently opened emulator")
device = get_device()

print("Check the emulator and accept if it asks for root permission.")
with suppress(RuntimeError):
    device.root()
device = get_device()
os.system(f'"{ADB_PATH}" wait-for-device')

print("\nRunning frida\nNow you can start fridahook\n")
os.system(f'"{ADB_PATH}" reverse tcp:{server_port} tcp:{server_port}')
if config["server"]["useSu"]:
    os.system(f'"{ADB_PATH}"' + " shell su -c /data/local/tmp/frida-server")
else:
    os.system(f'"{ADB_PATH}"' + " shell /data/local/tmp/frida-server")
