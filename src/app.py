import logging
import sys

from controlDevice import ControlDevice
from client import Client

logging.basicConfig(level=logging.DEBUG)


class App:
    """
    RC Mission Operator application.
    """

    STEERING_TYPE = ControlDevice.TYPE_SERVO
    STEERING_FREQ = 180
    STEERING_GPIO = ControlDevice.CHANNEL_0
    STEERING_MIN = 1.0
    STEERING_MAX = 2.0
    STEERING_NEUTRAL = 1.5

    THROTTLE_TYPE = ControlDevice.TYPE_ESC
    THROTTLE_FREQ = 90
    THROTTLE_GPIO = ControlDevice.CHANNEL_1
    THROTTLE_MIN = 1.1
    THROTTLE_MAX = 4.9
    THROTTLE_NEUTRAL = 1.5

    def __init__(self):
        """
        Constructor.
        """
        self._steering = ControlDevice(self.STEERING_TYPE, self.STEERING_GPIO,
                                       self.STEERING_FREQ, self.STEERING_MIN,
                                       self.STEERING_MAX,  self.STEERING_NEUTRAL)   # noqa: E501

        self._throttle = ControlDevice(self.THROTTLE_TYPE, self.THROTTLE_GPIO,
                                       self.THROTTLE_FREQ, self.THROTTLE_MIN,
                                       self.THROTTLE_MAX,  self.THROTTLE_NEUTRAL)   # noqa: E501

        self._client = Client('12345')

    def run(self):
        """
        Main application loop.
        """
        logging.info('starting RC control mission operator')
        while True:
            pass

    def stop(self):
        """
        Stop the application.
        """
        logging.info('stopping RC control mission operator')
        self._steering.stop_pulse()
        self._throttle.stop_pulse()
        self._client.disconnect()


if __name__ == '__main__':
    app = App()
    try:
        app.run()
    except KeyboardInterrupt:
        app.stop()
        sys.exit(0)
