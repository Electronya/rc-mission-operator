from adafruit_servokit import ServoKit
from exceptions import ContrelDevicePositionRange, \
    ControlDeviceMotionRangeInvalid, \
    ControlDeviceType, \
    ServoKitUninitialized


class ControlDevice:
    """
    RC control device base class.
    """
    TYPE_DIRECT = 'direction'
    TYPE_ESC = 'esc'
    CHANNELS = {'direction': 0, 'esc': 1}
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

    def __init__(self, logger: object,
                 servoType: str = TYPE_DIRECT,
                 motionRange: tuple = (MIN_ROTATION,
                                       DEFAULT_CENTER,
                                       MAX_ROTATION)):
        """
        Constructor.

        Params:
            servoType:      The type of device (servo or ESC). Default servo.
            motionRange:    The motion range of the device.
                            Default: (0, 90, 180).
        """
        self._logger = logger.getLogger(f"{servoType.upper()}")
        if self.servos is None:
            raise ServoKitUninitialized()
        if servoType != self.TYPE_DIRECT and servoType != self.TYPE_ESC:
            raise ControlDeviceType(servoType)

        self._validateMotionRange(motionRange)
        self._logger.info(f"creating device with motion range: {motionRange}")
        self._type = servoType
        self._min, self._center, self._max = motionRange
        self.servos[self.CHANNELS[self._type]].angle = self._center

    def _validateMotionRange(self, motionRange: tuple) -> None:
        """
        Validate the motion range.

        Params:
            motionRange:    The motion range to validate.
        """
        minPos, center, maxPos = motionRange
        if minPos < self.MIN_ROTATION or minPos >= maxPos:
            raise ControlDeviceMotionRangeInvalid('min', motionRange)
        if maxPos > self.MAX_ROTATION or maxPos <= minPos:
            raise ControlDeviceMotionRangeInvalid('max', motionRange)
        if center <= minPos or center >= maxPos:
            raise ControlDeviceMotionRangeInvalid('center', motionRange)

    def _validatePosition(self, position: int) -> None:
        """
        Check if a position is valid. min >= position >= max.

        Params:
            position:   The position to validate.
        """
        if position < self._min or position > self._max:
            raise ContrelDevicePositionRange(position, self._min, self._max)

    def setMotionRange(self, motionRange: tuple) -> None:
        """
        Set the device motion range.

        Params:
            motionRange:    The new motion range.
        """
        self._validateMotionRange(motionRange)
        self._logger.debug(f"updating motion range to: {motionRange}")
        self._min, self._center, self._max = motionRange

    def getMotionRange(self) -> tuple:
        """
        Get the current motion range.

        Return:
            The current motion range.
        """
        return (self._min, self._center, self._max)

    def setPosition(self, pos: int) -> None:
        """
        Set a new position.

        Params:
            pos:    The new position.
        """
        self._validatePosition(pos)
        self._logger.debug(f"updatingposition to: {pos}")
        self.servos[self.CHANNELS[self._type]].angle = pos

    def getPosition(self) -> int:
        """
        Get the current position.

        Return
            The current position.
        """
        return self.servos[self.CHANNELS[self._type]].angle
