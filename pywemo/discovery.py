"""
Module to discover WeMo devices.
"""
from netdisco import ssdp
import requests

from .ouimeaux_device.bridge import Bridge
from .ouimeaux_device.insight import Insight
from .ouimeaux_device.lightswitch import LightSwitch
from .ouimeaux_device.motion import Motion
from .ouimeaux_device.switch import Switch
from .ouimeaux_device.maker import Maker
from .ouimeaux_device.api.xsd import device as deviceParser


def discover_devices(st=None, max_devices=None, match_mac=None):
    """ Finds WeMo devices on the local network. """
    st = st or ssdp.ST_ROOTDEVICE

    entries = ssdp.scan(st)
    wemos = []

    description = dict(manufacture='Belkin International Inc.')
    if match_mac is not None:
        description['macAddress'] = match_mac

    for entry in entries:
        if not entry.match_device_description(description):
            continue

        mac = entry.description.get('device').get('macAddress')
        device = device_from_description(entry.location, mac)
        if not device:
            continue

        wemos.append(device)
        if max_devices and len(wemos) == max_devices:
            break

    return wemos


def device_from_description(description_url, mac):
    """ Returns object representing WeMo device running at host, else None. """
    try:
        xml = requests.get(description_url, timeout=10)

        uuid = deviceParser.parseString(xml.content).device.UDN

        return device_from_uuid_and_location(uuid, mac, description_url)

    except Exception:  # pylint: disable=broad-except
        return None


def device_from_uuid_and_location(uuid, mac, location):
    """ Tries to determine which device it is based on the uuid. """
    if uuid.startswith('uuid:Socket'):
        return Switch(location, mac)
    elif uuid.startswith('uuid:Lightswitch'):
        return LightSwitch(location, mac)
    elif uuid.startswith('uuid:Insight'):
        return Insight(location, mac)
    elif uuid.startswith('uuid:Sensor'):
        return Motion(location, mac)
    elif uuid.startswith('uuid:Maker'):
        return Maker(location, mac)
    elif uuid.startswith('uuid:Bridge'):
        return Bridge(location, mac)
    else:
        return None
