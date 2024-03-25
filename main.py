import paho.mqtt.client as mqtt
from solax.inverters import X1HybridGen5
import asyncio
import time
import json

async def read_solax(inverter):
    return await inverter.get_data()

def send_discovery_msgs():
    grid_pwr_disc = json.dumps({'device_class': 'power', 'name': 'Grid Power', 'device': {'name': 'solax', 'identifiers': ['solax']}, 'state_topic': 'homeassistant/sensor/solax_grid/state', 'unit_of_measurement': 'W', 'state_class': 'measurement', 'unique_id': 'solax_grid'})
    pv1_pwr_disc = json.dumps({'device_class': 'power', 'name': 'Panel Power', 'device': {'name': 'solax', 'identifiers': ['solax']}, 'state_topic': 'homeassistant/sensor/solax_panel/state', 'unit_of_measurement': 'W', 'state_class': 'measurement', 'unique_id': 'solax_pv1'})
    bat_pwr_disc = json.dumps({'device_class': 'power', 'name': 'Battery Power', 'device': {'name': 'solax', 'identifiers': ['solax']}, 'state_topic': 'homeassistant/sensor/solax_battery/state', 'unit_of_measurement': 'W', 'state_class': 'measurement', 'unique_id': 'solax_bat'})
    bat_chrg_disc = json.dumps({'device_class': 'battery', 'name': 'Battery Charge', 'device': {'name': 'solax', 'identifiers': ['solax']}, 'state_topic': 'homeassistant/sensor/solax_battery_charge/state', 'unit_of_measurement': '%', 'state_class': 'measurement', 'unique_id': 'solax_chrg'})
    total_feedin_disc = json.dumps({'device_class': 'energy', 'name': 'Fed Into Grid', 'device': {'name': 'solax', 'identifiers': ['solax']}, 'state_topic': 'homeassistant/sensor/solax_total_feedin/state', 'unit_of_measurement': 'kWh', 'state_class': 'total_increasing', 'unique_id': 'solax_feedin'})
    total_consumed_disc = json.dumps({'device_class': 'energy', 'name': 'Consumed From Grid', 'device': {'name': 'solax', 'identifiers': ['solax']}, 'state_topic': 'homeassistant/sensor/solax_total_consumed/state', 'unit_of_measurement': 'kWh', 'state_class': 'total_increasing', 'unique_id': 'solax_consumed'})
    total_produced_disc = json.dumps({'device_class': 'energy', 'name': 'Produced From PV', 'device': {'name': 'solax', 'identifiers': ['solax']}, 'state_topic': 'homeassistant/sensor/solax_total_produced/state', 'unit_of_measurement': 'kWh', 'state_class': 'total_increasing', 'unique_id': 'solax_produced'})
    client.publish('homeassistant/sensor/solax_grid/config', grid_pwr_disc, 0, retain=True)
    client.publish('homeassistant/sensor/solax_pv1/config', pv1_pwr_disc, 0, retain=True)
    client.publish('homeassistant/sensor/solax_bat/config', bat_pwr_disc, 0, retain=True)
    client.publish('homeassistant/sensor/solax_bat_chrg/config', bat_chrg_disc, 0, retain=True)
    client.publish('homeassistant/sensor/solax_total_feedin/config', total_feedin_disc, 0, retain=True)
    client.publish('homeassistant/sensor/solax_total_consumed/config', total_consumed_disc, 0, retain=True)
    client.publish('homeassistant/sensor/solax_total_produced/config', total_produced_disc, 0, retain=True)


def onConnect(client, userdata, flags, rc):
    print("Connected: " + str(rc))
    send_discovery_msgs()

def onDisconnect(client, userdata):
    print('Disconnected')

solax_ip = '192.168.1.127'
solax_sn = 'SR68FZRZGP'

inverter = X1HybridGen5.build_all_variants(solax_ip, 80, solax_sn)[0]

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

client = mqtt.Client()
client.on_connect = onConnect
client.on_disconnect = onDisconnect

client.connect("192.168.1.201", 1883)
client.loop_start()

while True:
    data = loop.run_until_complete(read_solax(inverter))
    print(data)

    grid_pwr = data.data['Grid power']
    client.publish('homeassistant/sensor/solax_grid/state', grid_pwr)
    print(grid_pwr)

    pv1_pwr = data.data['PV1 power']
    client.publish('homeassistant/sensor/solax_panel/state', pv1_pwr)
    print(pv1_pwr)

    bat_pwr = data.data['Battery power']
    adj_bat_pwr = bat_pwr - 65536 if bat_pwr > 32767 else bat_pwr
    client.publish('homeassistant/sensor/solax_battery/state', adj_bat_pwr)
    print(adj_bat_pwr)

    bat_charge = data.data['Battery SoC']
    client.publish('homeassistant/sensor/solax_battery_charge/state', bat_charge)
    print(bat_charge)

    total_feedin = data.data['Total feed-in energy']
    client.publish('homeassistant/sensor/solax_total_feedin/state', total_feedin)
    print(total_feedin)

    total_consumed = data.data['Total consumption']
    client.publish('homeassistant/sensor/solax_total_consumed/state', total_consumed)
    print(total_consumed)

    total_produced = data.data['On-grid total yield']
    client.publish('homeassistant/sensor/solax_total_produced/state', total_produced)
    print(total_produced)

    time.sleep(1)
