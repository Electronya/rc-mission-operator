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
    def __init__(self, element: str, range: tuple):
        """
        Constructor.

        Params:
            element:    The element that is not valid.
            range:      The invalid range.
        """
        super().__init__(f"{element} in range: {range} is not valid.")


class ContrelDevicePositionRange(Exception):
    """
    The control device position out of range exception.
    """
    def __init__(self, pos: int, min: int, max: int):
        """
        Contructor.

        Params:
            pos:    The unvalid position.
            min:    The minimal position accepted.
            max:    The maximal position accepted.
        """
        super().__init__(f"position {pos} is not included "
                         f"between {min} and {max}")
