from config import USE_MOCK_SENSORS, MQTT_HOST, MQTT_PORT, USE_MOCK_MQTT, USE_MOCK_CAMERA, \
    AZURE_IOT_HUB_NAME, AZURE_IOT_HUB_PATH_TO_ROOT_CERT, AZURE_IOT_HUB_SAS_TOKEN
import paho.mqtt.client as mqtt
import ssl

class SensorManager:

    def __init__(self, device, screen):
        self.device = device

        if USE_MOCK_MQTT:
            self.client = None
        else:
            self.client = mqtt.Client(client_id=self.device.name, protocol=mqtt.MQTTv311)
            self.client.user_data_set(screen)
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_publish = self.on_publish

            self.client.username_pw_set(username=MQTT_HOST + '/' + self.device.name + "/?api-version=2018-06-30", password=AZURE_IOT_HUB_SAS_TOKEN)

            self.client.tls_set(ca_certs=AZURE_IOT_HUB_PATH_TO_ROOT_CERT, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)
            self.client.tls_insecure_set(True)

            self.client.connect(MQTT_HOST, MQTT_PORT, 60)

        if USE_MOCK_SENSORS:
            self.sensehat = None
            self.device.final_init(None)
        else:
            from sense_hat import SenseHat
            self.sensehat = SenseHat()
            self.device.final_init(self.sensehat)

        if USE_MOCK_CAMERA:
            self.camera = None
        else:
            import picamera
            self.camera = picamera.PiCamera()
#            self.camera.start_preview()
#            self.camera = None
    def disconnect(self):
        if not USE_MOCK_MQTT:
            self.client.disconnect()

    def close_camera(self):
        if self.camera is not None:
            self.camera.close()

    def on_connect(self, client, userdata, flags, rc):
        print ("Device connected with result code: " + str(rc))

    def on_disconnect(self, client, userdata, rc):
        print("Device disconnected with result code: " + str(rc))
        if rc == 1:
            userdata.on_kicked()
        else:
            userdata.on_manual_disconnect()

    def on_publish(self, client, userdata, mid):
        print ("Device sent message")

    def on_message(self, mqttc, obj, msg):
        print(msg)

    def publish(self):
        message = self.device.serialize(self.sensehat, self.camera)

        if USE_MOCK_MQTT:
            print(message)
        else:
            self.client.publish('devices/' + self.device.name + "/messages/events/", payload=str(message))

    def display(self):
        #self.device.display_status(self.sensehat)
        pass
