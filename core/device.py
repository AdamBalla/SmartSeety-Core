import base64
import io
import random
from db import DB

from core.device_flags import DeviceFlags

class Device:
    def __init__(self, name, flags):
        self.name = name
        self.flags = DeviceFlags(flags)
        self.joystick_state = {
            'up': False,
            'left': False,
            'down': False,
            'right': False,
            'middle': False
        }
        self.messages = []

    def __str__(self):
        return self.name

    def close(self):
        if self.stream is not None:
            try:
                self.stream.close()
            except AttributeError:
                print('Thread died!')

    def final_init(self, sensehat):
        self.sensehat = sensehat
        self.stream = DB.child('devices').child(self.name).child('status').stream(self.stream_handler)

    def stream_handler(self, message):
        if message['event'] in ('put', 'patch'):
            self.display_status(self.sensehat, message['data'])

    def display_status(self, sensehat, data):
        if data == None:
            return

        if sensehat:
            sensehat.show_message(text_string=data['message'], text_colour=[int(data['color']['r'] * 255),
                                                                            int(data['color']['g'] * 255),
                                                                            int(data['color']['b'] * 255)])
        else:
            print(data['message'])

    def serialize(self, sensehat, camera):
        message = {}

        if self.flags & DeviceFlags.TEMPERATURE:
            message['temperature'] = {
                'sensor': {
                    'value': sensehat.get_temperature() if sensehat is not None else random.uniform(20, 40)
                }
            }

        if self.flags & DeviceFlags.ACCELEROMETER:
            message['accelerometer'] = {
                'sensor': {
                    'value': sensehat.get_accelerometer_raw() if sensehat is not None else { 'x': random.uniform(-2, 2), 'y': random.uniform(-2, 2), 'z': random.uniform(-2, 2) }
                }
            }

        if self.flags & DeviceFlags.HUMIDITY:
            message['humidity'] = {
                'sensor': {
                    'value': sensehat.get_humidity() if sensehat is not None else random.uniform(30, 50)
                }
            }

        if self.flags & DeviceFlags.GYROSCOPE:
            if sensehat is not None:
                gyroscope = sensehat.get_orientation()
            
            message['gyroscope'] = {
                'sensor': {
                    'value': { 'x': gyroscope['pitch'], 'y': gyroscope['roll'], 'z': gyroscope['yaw'] } if sensehat is not None else { 'x': random.uniform(0, 360), 'y': random.uniform(0, 360), 'z': random.uniform(0, 360) }
                }
            }

        if self.flags & DeviceFlags.JOYSTICK:
            if sensehat is not None:
                for event in sensehat.stick.get_events():
                    self.joystick_state[event.direction] = event.action != 'released'
            else:
                directions = ['up', 'left', 'down', 'right', 'middle']
                actions = ['released', 'pressed']
                directionRand = random.choice(directions)
                actionRand = random.choice(actions)
                self.joystick_state[directionRand] = actionRand != 'released'

            message['joystick'] = self.joystick_state

        if self.flags & DeviceFlags.MAGNETOMETER:
            message['magnetometer'] = {
                'sensor': {
                    'value': sensehat.get_compass() if sensehat is not None else random.uniform(0, 360)
                }
            }

        if self.flags & DeviceFlags.BAROMETRIC_PRESSURE:
            message['barometricPressure'] = {
                'sensor': {
                    'value': sensehat.get_pressure() if sensehat is not None else random.uniform(950, 1050)
                }
            }

        if self.flags & DeviceFlags.DISPLAY:
            picture = ''

            if camera is not None:
                # TODO: test it with real device
                stream = io.BytesIO()
                #import picamera
                #with picamera.PiCamera() as camera:
                camera.resolution = (320, 240)
                camera.framerate = 24
                #time.sleep(1)
                camera.capture(stream, 'jpeg')
                picture = str(base64.b64encode(stream.getvalue()))
            else:
                import numpy
                from PIL import Image as Img
                imgByteArr = io.BytesIO()
                a = numpy.random.rand(320,240,3) * 255
                im_out = Img.fromarray(a.astype('uint8'))
                im_out.save(imgByteArr, format='jpeg')
                picture = str(base64.b64encode(imgByteArr.getvalue()))
                #with open('mock/borat.jpg', 'rb') as mock_image_file:
                #    picture = str(base64.b64encode(mock_image_file.read()))

            message['display'] = {
                'picture': picture
            }

        return message
