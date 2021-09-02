from adafruit_servokit import ServoKit
from exceptions import ControlDeviceMotionRangeInvalid, ControlDeviceType, \
    ServoKitUninitialized


class ControlDevice:
    """
    RC control device base class.
    """
    TYPE_SERVO = 'servo'
    TYPE_ESC = 'esc'
    CHANNELS = {'servo': 0, 'esc': 1}
    MIN_ROTATION = 0
    DEFAULT_CENTER = 90
    MAX_ROTATION = 180
    SUPPORTED_CHAN_CNT = [8, 16]
    DEFAULT_FREQ = 90

    UNSUPPORTED_DEV_ERR_MSG = 'Unsupported device type.'
    GPIO_UNABLE_ERR_MSG1 = 'Unable to used gpio: '
    GPIO_UNABLE_ERR_MSG2 = 'as PWM channel.'
    CONNECTION_ERR_MSG = 'Unable to connected to PIGPIO service.'
    PWM_OP_FAILED_MSG = 'PWM operation failed, err: '

    servos = None

    @classmethod
    def initServoKit(cls, chanCount=SUPPORTED_CHAN_CNT[0],
                     frequency=DEFAULT_FREQ) -> None:
        """
        Intialize the servo kit.

        Params:
            chanCount:  The number of channel in the servo kit. Default 8.
            frequency:  The desired frequency.
        """
        cls.servos = ServoKit(channels=chanCount, frequency=frequency)

    def __init__(self, type='servo', motionRange=(MIN_ROTATION,
                                                  DEFAULT_CENTER,
                                                  MAX_ROTATION)):
        """
        Constructor.

        Params:
            type:           The type of device (servo or ESC). Default servo.
            motionRange:    The motion range of the device.
                            Default: (0, 90, 180).
        """
        if self.servos is None:
            raise ServoKitUninitialized()
        if type != self.TYPE_SERVO and type != self.TYPE_ESC:
            raise ControlDeviceType(type)

        self._validateMotionRange(motionRange)
        self._min, self._center, self._max = motionRange

    def _validateMotionRange(self, motionRange: tuple) -> None:
        """
        Validate the motion range.

        Params:
            motionRange:    The motion range to validate.
        """
        minPos, center, maxPos = motionRange
        if minPos < self.MIN_ROTATION or minPos >= maxPos:
            raise ControlDeviceMotionRangeInvalid(minPos,
                                                  self.MIN_ROTATION,
                                                  self.MAX_ROTATION)
        if maxPos > self.MAX_ROTATION or maxPos <= minPos:
            raise ControlDeviceMotionRangeInvalid(maxPos,
                                                  self.MIN_ROTATION,
                                                  self.MAX_ROTATION)
        if center <= minPos or center >= maxPos:
            raise ControlDeviceMotionRangeInvalid(center, minPos, maxPos)

    def _validatePosition(self, position: int,
                          posRange=(MIN_ROTATION, MAX_ROTATION)) -> None:
        """
        Check if a position is valid.

        Params:
            position:   The position to validate.
            posRange:   The range used for validation.
        """
        minPos, maxPos = posRange
        if position < minPos or position > maxPos:
            raise ControlDeviceMotionRangeInvalid(position, minPos, maxPos)
