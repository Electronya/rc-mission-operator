class ServoKitUninitialized(Exception):
    """
    The ServoKit uninitialize exception.
    """
    def __init__(self):
        """
        Constructor.
        """
        super().__init__('SevoKit is not initialized.')


class ControlDeviceType(Exception):
    """
    The unsupported control device type exception.
    """
    def __init__(self, devType: str) -> None:
        """
        Constructor.

        Params:
            devType:    The device type.
            channel:    The device channel ID.
        """
        super().__init__(f"device {devType} is unsupported.")


class ControlDeviceMotionRangeInvalid(Exception):
    """
    The control device motion range exception.
    """
    def __init__(self, pos, min, max):
        """
        Constructor.

        Params:
            pos:        The requested position.
            min:        The minimal position accepted.
            max:        The maximal position accepted.
        """
        super().__init__(f"position {pos} is not included "
                         f"between {min} and {max}")
