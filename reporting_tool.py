import json
from collections import defaultdict, OrderedDict
import paho.mqtt.client as mqtt
import ssl
import sched
import time
from humanfriendly import format_timespan

from creds import API_KEY, TENANT_ID

TIMESPANS_FOR_CALC_IN_SEC = [5 * 60, 60 * 60]
TIMESPANS_TO_PRINT_NAME = {t: format_timespan(t) for t in
                           TIMESPANS_FOR_CALC_IN_SEC}  # see: https://stackoverflow.com/a/43261109

SECONDS_BETWEEN_REFRESH = 5
tenant_id = TENANT_ID
api_key = API_KEY

host = "mqtt.cloud.pozyxlabs.com"
port = 443
topic = f"{tenant_id}/tags"
username = tenant_id
password = api_key

tagid_to_epoch_timestamps = defaultdict(list)


def on_connect(cur_client, userdata, flags, rc):
    print(mqtt.connack_string(rc))
    cur_client.subscribe(topic)


# Callback triggered by a new Pozyx data packet
def on_message(cur_client, userdata, msg):
    # print("Positioning update:", msg.payload.decode())
    tags_infos_list = json.loads(msg.payload.decode())
    for tag_info in tags_infos_list:
        if bool(tag_info['success']):
            tagid_to_epoch_timestamps[tag_info["tagId"]].append(tag_info["timestamp"])


def on_subscribe(cur_client, userdata, mid, granted_qos):
    print("Subscribed to topic!")


def print_dict_to_table(d, timespan):
    d = OrderedDict(sorted(d.items()))
    print("{:<8} {:<15}".format('tagid',
                                f'Avg rate in last {TIMESPANS_TO_PRINT_NAME[timespan]} (in Hz)'))  # I took it from: https://stackoverflow.com/a/17330263
    for t_id, freq in d.items():
        print("{:<8} {:<15}".format(t_id, round(freq, 2)))


def filter_list_by_cutoff(l, min_cutoff_val):
    return list(filter(lambda i: i >= min_cutoff_val, l))


def update_and_show_stats():
    earliest_cutoff = time.time() - max(TIMESPANS_FOR_CALC_IN_SEC)
    global tagid_to_epoch_timestamps
    tagid_to_epoch_timestamps = defaultdict(list, {t_id: filter_list_by_cutoff(timestamps, earliest_cutoff) for
                                                   t_id, timestamps in tagid_to_epoch_timestamps.items()})

    for timespan in TIMESPANS_FOR_CALC_IN_SEC:
        if timespan != max(TIMESPANS_FOR_CALC_IN_SEC):
            filtered_tagid_to_epoch_timestamps = {t_id: filter_list_by_cutoff(timestamps, timespan) for t_id, timestamps
                                                  in tagid_to_epoch_timestamps.items()}
        tagid_to_freq = {t_id: len(timestamps) / timespan for t_id, timestamps in
                         filtered_tagid_to_epoch_timestamps.items()}
        print_dict_to_table(tagid_to_freq, timespan)


client = mqtt.Client(transport="websockets")
client.username_pw_set(username, password=password)

# sets the secure context, enabling the WSS protocol
client.tls_set_context(context=ssl.create_default_context())

# set callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.connect(host, port=port)

client.loop_start()

while True:
    update_and_show_stats()
    time.sleep(SECONDS_BETWEEN_REFRESH)
