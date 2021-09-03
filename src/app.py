import sys

from controlDevice import ControlDevice
from client import Client
from logger import initLogger


class App:
    """
    RC Mission Operator application.
    """
    PWM_FREQ = 180
    STEERING_TYPE = ControlDevice.TYPE_DIRECT
    STEERING_MIN = ControlDevice.MIN_ROTATION
    STEERING_MAX = ControlDevice.MAX_ROTATION
    STEERING_NEUTRAL = ControlDevice.DEFAULT_CENTER

    THROTTLE_TYPE = ControlDevice.TYPE_ESC
    THROTTLE_MIN = ControlDevice.MIN_ROTATION
    THROTTLE_MAX = ControlDevice.MAX_ROTATION
    THROTTLE_NEUTRAL = ControlDevice.DEFAULT_CENTER

    def __init__(self):
        """
        Constructor.
        """
        logger = initLogger()
        self._logger = logger.getLogger('APP')

        ControlDevice.initServoKit()
        self._steering = ControlDevice(logger, self.STEERING_TYPE,
                                       (self.STEERING_MIN,
                                        self.STEERING_NEUTRAL,
                                        self.STEERING_MAX))
        self._throttle = ControlDevice(logger, self.THROTTLE_TYPE,
                                       (self.THROTTLE_MIN,
                                        self.THROTTLE_MAX,
                                        self.THROTTLE_NEUTRAL))

        self._client = Client('12345')

    def run(self):
        """
        Main application loop.
        """
        self._logger.info('starting RC control mission operator')
        while True:
            pass

    def stop(self):
        """
        Stop the application.
        """
        self._logger.info('stopping RC control mission operator')
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
