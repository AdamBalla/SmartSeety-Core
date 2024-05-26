from db import DB
from core.device import Device


class DeviceList:

    def __init__(self):
        self.devices = self.get_devices()

    def get_devices(self):
        devices = []

        for device in DB.child('devices').get().each():
            val = device.val()
            if val['name'][0] != '@':
                devices.append(Device(val['name'], val['sensors']))
        
        devices.sort(key=lambda x: x.name)

        return devices
