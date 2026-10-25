import json, os, random, time
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

HOST = os.getenv('MQTT_HOST', 'localhost')
PORT = int(os.getenv('MQTT_PORT', '1883'))
INTERVAL = int(os.getenv('PUBLISH_INTERVAL', '5'))
ROOMS = ['coldroom1', 'coldroom2', 'coldroom3']

def on_connect(client, userdata, flags, reason_code, properties):
    print(f'Connected to MQTT {HOST}:{PORT}; result={reason_code}', flush=True)

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id='cold-storage-simulator')
    client.on_connect = on_connect
    client.connect(HOST, PORT, 60)
    client.loop_start()
    temps = {'coldroom1': 4.2, 'coldroom2': 4.8, 'coldroom3': 3.9}
    door_open_until = {room: 0 for room in ROOMS}
    cycle = 0
    try:
        while True:
            now = datetime.now(timezone.utc).isoformat()
            cycle += 1
            for i, room in enumerate(ROOMS):
                temps[room] += random.uniform(-0.18, 0.18)
                temps[room] = max(2.0, min(8.8, temps[room]))
                if cycle % 24 == 0 and i == (cycle // 24) % 3:
                    door_open_until[room] = time.time() + 20
                door = time.time() < door_open_until[room]
                payload = {
                    'timestamp': now,
                    'room': room,
                    'temperature_c': round(temps[room], 2),
                    'door_open': door,
                    'power_ok': True,
                    'compressor_on': temps[room] > 5.5,
                    'alarm': temps[room] > 8 or door,
                }
                topic = f'warehouse/{room}/telemetry'
                client.publish(topic, json.dumps(payload), qos=1, retain=True)
                client.publish(f'warehouse/{room}/status', json.dumps({'online': True, 'timestamp': now}), qos=1, retain=True)
                print(f'{topic} {json.dumps(payload)}', flush=True)
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as exc:
            print(f'MQTT connection/runtime error: {exc}; retrying in 5s', flush=True)
            time.sleep(5)
