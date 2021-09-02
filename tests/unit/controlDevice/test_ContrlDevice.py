import logging
from unittest import TestCase
from unittest.mock import Mock, patch

import os
import sys

sys.path.append(os.path.abspath('./src'))
mockedServoKit = Mock()
sys.modules['adafruit_servokit'] = mockedServoKit

from controlDevice import ControlDevice           # noqa: E402
from exceptions import ServoKitUninitialized, ControlDeviceType, \
    ControlDeviceMotionRangeInvalid  # noqa: E402


class TestControlDevice(TestCase):
    """
    Control Device class test cases.
    """
    def setUp(self):
        """
        Test cases setup.
        """
        mockedServoKit.return_value = []
        ControlDevice.initServoKit()
        self.ctrlDev = ControlDevice()

    def test_initServoKit(self):
        """
        The initServoKit class method must initialize the servi kit
        library with good number of servo channels and frequency.
        """
        expectedChan = 8
        expectedFreq = 90
        ControlDevice.initServoKit()
        mockedServoKit.ServoKit.assert_called_with(channels=expectedChan,
                                                   frequency=expectedFreq)
        expectedChan = 16
        expectedFreq = 50
        ControlDevice.initServoKit(chanCount=expectedChan,
                                   frequency=expectedFreq)
        mockedServoKit.ServoKit.assert_called_with(channels=expectedChan,
                                                   frequency=expectedFreq)

    def test_constructorServoUninitialized(self):
        """
        The constructor must raise a ServoKitUninitialized exception
        if the servo kit is not initialized.
        """
        ControlDevice.servos = None
        with self.assertRaises(ServoKitUninitialized) as context:
            ctlrDev = ControlDevice()                   # noqa: F841
            self.assertTrue(isinstance(context.exception,
                                       ServoKitUninitialized))

    def test_constructorUnsupportedType(self):
        """
        The constructor must raise an ControlDeviceType exception
        if the control device type is unsupported.
        """
        devType = 'PROUT'
        with self.assertRaises(ControlDeviceType) as context:
            ctlrDev = ControlDevice(type=devType)       # noqa: F841
            self.assertTrue(isinstance(context.exception, ControlDeviceType))

    def test_constructorMotionRange(self):
        """
        The constructor must validate the motion range.
        """
        expected = (ControlDevice.MIN_ROTATION,
                    ControlDevice.DEFAULT_CENTER,
                    ControlDevice.MAX_ROTATION)
        with patch.object(ControlDevice, '_validateMotionRange') \
                as mockedValidateMotion:
            ctlrDev = ControlDevice()       # noqa: F841
            mockedValidateMotion.assert_called_once_with(expected)

    def test_validateMotionRangeMin(self):
        """
        The _validateMotionRange method must raise a
        ControlDeviceMotionRangeInvalid exception only if:
            - min < MIN_ROTATION
            - min < max
        """
        nonValidMins = [ControlDevice.MIN_ROTATION - 1,
                        ControlDevice.MIN_ROTATION - 10,
                        ControlDevice.MAX_ROTATION]
        validMins = [ControlDevice.MIN_ROTATION,
                     ControlDevice.MIN_ROTATION + 1,
                     ControlDevice.MIN_ROTATION + 10]
        for nonValidMin in nonValidMins:
            testRange = (nonValidMin,
                         ControlDevice.DEFAULT_CENTER,
                         ControlDevice.MAX_ROTATION)
            with self.assertRaises(ControlDeviceMotionRangeInvalid) as context:
                self.ctrlDev._validateMotionRange(testRange)
                self.assertTrue(isinstance(context.exception,
                                           ControlDeviceMotionRangeInvalid))
        for validMin in validMins:
            testRange = (validMin,
                         ControlDevice.DEFAULT_CENTER,
                         ControlDevice.MAX_ROTATION)
            try:
                self.ctrlDev._validateMotionRange(testRange)
            except Exception:
                self.fail('The _validateMotionRange failed to raise '
                          'an exception only if min < MIN_MOTION / '
                          'min >= max.')

    def test_validateMotionRangeMax(self):
        """
        The _validateMotionRange method must raise a
        ControlDeviceMotionRangeInvalid exception only if:
            - max > MAX_ROTATION
            - max < min
        """
        nonValidMaxes = [ControlDevice.MAX_ROTATION + 1,
                         ControlDevice.MAX_ROTATION + 10,
                         ControlDevice.MIN_ROTATION]
        validMaxes = [ControlDevice.MAX_ROTATION,
                      ControlDevice.MAX_ROTATION - 1,
                      ControlDevice.MAX_ROTATION - 10]
        for nonValidMax in nonValidMaxes:
            testRange = (ControlDevice.MIN_ROTATION,
                         ControlDevice.DEFAULT_CENTER,
                         nonValidMax)
            with self.assertRaises(ControlDeviceMotionRangeInvalid) as context:
                self.ctrlDev._validateMotionRange(testRange)
                self.assertTrue(isinstance(context.exception,
                                           ControlDeviceMotionRangeInvalid))
        for validMax in validMaxes:
            testRange = (ControlDevice.MIN_ROTATION,
                         ControlDevice.DEFAULT_CENTER,
                         validMax)
            try:
                self.ctrlDev._validateMotionRange(testRange)
            except Exception:
                self.fail('The _validateMotionRange failed to raise '
                          'an exception only if max > MAX_MOTION / '
                          'max <= min.')

    def test_validateMotionRangeCenter(self):
        """
        The _validateMotionRange method must raise a
        ControlDeviceMotionRangeInvalid exception only if:
            - center <= min
            - center >= max
        """
        nonValidCenters = [ControlDevice.MIN_ROTATION,
                           ControlDevice.MIN_ROTATION - 1,
                           ControlDevice.MAX_ROTATION,
                           ControlDevice.MAX_ROTATION + 1]
        validCenters = [ControlDevice.MIN_ROTATION + 1,
                        ControlDevice.MAX_ROTATION - 1,
                        ControlDevice.DEFAULT_CENTER]
        for nonValidCenter in nonValidCenters:
            testRange = (ControlDevice.MIN_ROTATION,
                         nonValidCenter,
                         ControlDevice.MAX_ROTATION)
            with self.assertRaises(ControlDeviceMotionRangeInvalid) as context:
                self.ctrlDev._validateMotionRange(testRange)
                self.assertTrue(isinstance(context.exception,
                                           ControlDeviceMotionRangeInvalid))
        for validCenter in validCenters:
            testRange = (ControlDevice.MIN_ROTATION,
                         validCenter, ControlDevice.MAX_ROTATION)
            try:
                self.ctrlDev._validateMotionRange(testRange)
            except Exception:
                self.fail('The _validateMotionRange failed to raise '
                          'an exception only if center <= min / '
                          'center >= max.')

    def test_validatePosition(self):
        """
        The _validatePosition method must raise a ControlDevicePositionRange
        exception only if the tested position is out of the min/max range.
        """
        testRange = (ControlDevice.MIN_ROTATION, ControlDevice.MAX_ROTATION)
        nonValidValues = [ControlDevice.MIN_ROTATION - 1,
                          ControlDevice.MAX_ROTATION + 1]
        validValues = [ControlDevice.MIN_ROTATION,
                       ControlDevice.MAX_ROTATION,
                       ControlDevice.DEFAULT_CENTER]
        for nonValidValue in nonValidValues:
            with self.assertRaises(ControlDeviceMotionRangeInvalid) as context:
                self.ctrlDev._validatePosition(nonValidValue, testRange)
                self.assertTrue(isinstance(context.exception,
                                ControlDeviceMotionRangeInvalid))
        for validValue in validValues:
            try:
                self.ctrlDev._validatePosition(validValue, testRange)
            except ControlDeviceMotionRangeInvalid:
                self.fail('The DeviceControl _validatePosition failed to '
                          'raise an exception only if the position is out '
                          'of range.')