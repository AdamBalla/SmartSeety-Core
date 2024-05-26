from flags import Flags


class DeviceFlags(Flags):
    #NONE = 0
    GYROSCOPE = 1
    ACCELEROMETER = 2
    MAGNETOMETER = 4
    TEMPERATURE = 8
    BAROMETRIC_PRESSURE = 16
    HUMIDITY = 32
    JOYSTICK = 64
    CAMERA = 128
    DISPLAY = 256
