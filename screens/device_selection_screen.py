import asyncio
from db import DB
from uuid import getnode
import tkinter as tk
from tkinter import ttk
from core.device import Device
from config import BACKGROUND_COLOR, TEXT_COLOR_PRIMARY, BUTTON_BACKGROUND_COLOR, BUTTON_TEXT_COLOR, \
    BUTTON_ONCLICK_BACKGROUND_COLOR, MQTT_HOST, MQTT_PORT, NUMBER_OF_MESSAGE_UPDATES_PER_SECOND, \
    AZURE_IOT_HUB_CONNECTION_STRING, TOAST_DURATION_IN_SECONDS, NUMBER_OF_STATUS_UPDATES_PER_SECOND

from core.device_list import DeviceList
from core.sensor_manager import SensorManager
from core.device_manager import DeviceManager
from tkinter import font


class DeviceSelectionScreen(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.protocol('WM_DELETE_WINDOW', self.on_close)

        combostyle = ttk.Style()

        combostyle.theme_create('combostyle', parent='alt',
                                settings={'TCombobox':
                                              {'configure':
                                                   {'selectforeground': 'black',
                                                    'selectbackground': 'white',
                                                    'fieldbackground': 'white',
                                                    'background': '#0032b1'
                                                    }}}
                                )

        combostyle.theme_use('combostyle')

        self.background_image = tk.PhotoImage(file='assets/selection_bg.png')
        self.background_label = tk.Label(parent, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.device_list = DeviceList().devices
        self.device_list_ui = ttk.Combobox(self.parent, values=self.device_list, width=40)
        self.device_list_ui.bind("<<ComboboxSelected>>", self.on_device_selected, "+")
        self.device_list_ui.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.device_manager = DeviceManager(AZURE_IOT_HUB_CONNECTION_STRING)

        self.connect_button_text = tk.StringVar()
        self.connect_button_text.set('Connect')
        self.connect_button = tk.Button(self.parent, textvariable=self.connect_button_text, command=self.on_connect_button_click, bg=BUTTON_BACKGROUND_COLOR, fg=BUTTON_TEXT_COLOR, activebackground=BUTTON_ONCLICK_BACKGROUND_COLOR, activeforeground=BUTTON_TEXT_COLOR)
        self.connect_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)
        self.connect_button.config(height=3, width=60)

        self.message = None

        self.pack()

        self.device = None
        self.sensor_manager = None
        self.parent.tasks.append(self.parent.loop.create_task(self.update_messages(1 / NUMBER_OF_MESSAGE_UPDATES_PER_SECOND)))
        self.parent.tasks.append(self.parent.loop.create_task(self.update_status(1 / NUMBER_OF_STATUS_UPDATES_PER_SECOND)))

    def on_connect_button_click(self):
        if self.device is not None:
            if self.device.name.startswith('--') and self.device.name.endswith('--'):
                oldData = DB.child('devices').child(self.device.name).get().pyres
                newName =  '@' + self.device.name[2:-2] + '-' + str(getnode())
                newData = {newName: { d.item[0]: d.item[1] for d in oldData }}
                newData[newName]['name'] = newName
                self.device = Device(newName, newData[newName]['sensors'])
                DB.child('devices').update(newData)

            errorMessage, errorCode = self.device_manager.retrieveDeviceId(self.device)
            if errorCode == 404:
                self.device_manager.createDeviceId(self.device)

            if self.connect_button_text.get() == 'Connect':
                self.connect_button_text.set('Disconnect')
                self.device_list_ui.config(state='disabled')
                self.sensor_manager = SensorManager(self.device, self)
            else:
                self.on_disconnect(True)

    def on_disconnect(self, remove_device):
        print('UI on disconnected was called')
        self.connect_button_text.set('Connect')
        self.device_list_ui.config(state='normal')
        if self.sensor_manager is not None:
            self.sensor_manager.disconnect()

            if remove_device:
                if self.device is not None:
                    self.device_manager.deleteDeviceId(self.device.name)
        
        if self.sensor_manager is not None:
            self.sensor_manager.close_camera()

        self.device.close()
        self.sensor_manager = None

    def on_kicked(self):
        self.on_disconnect(False)

        self.message = tk.Message(self.parent, text='You have been kicked out by another device.', width=1000)
        self.message.place(relx=0.5, rely=0.925, anchor=tk.CENTER)

        self.after(TOAST_DURATION_IN_SECONDS * 1000, self.remove_toast)

    def remove_toast(self):
        self.message.destroy()

    def on_manual_disconnect(self):
        self.on_disconnect(True)

    def on_device_selected(self, a):
        self.device = self.device_list[self.device_list_ui.current()]

    def on_close(self):
        if self.device is not None:
            self.device_manager.deleteDeviceId(self.device.name)

        self.parent.close()

    async def update_messages(self, interval):
        while True:
            if self.sensor_manager is not None:
                self.sensor_manager.publish()

            await asyncio.sleep(interval)

    async def update_status(self, interval):
        while True:
            if self.sensor_manager is not None:
                self.sensor_manager.display()

            await asyncio.sleep(interval)