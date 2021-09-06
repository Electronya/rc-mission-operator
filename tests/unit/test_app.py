import json
from unittest import TestCase
from unittest.mock import Mock, call, patch

import os
import sys

sys.path.append(os.path.abspath('./src'))
mockedAdafruitSrvoKit = Mock()
sys.modules['adafruit_servokit'] = mockedAdafruitSrvoKit

import app      # noqa: E402


class TestApp(TestCase):
    """
    The app module test cases.
    """
    def setUp(self):
        """
        The test cases setup.
        """
        app.client = Mock()
        app.logger = Mock()
        app.steering = Mock()
        app.throttle = Mock()
        app.ControlDevice.servos = [Mock(), Mock()]
        self.testSubs = (app.UnitSteeringMsg(app.CLIENT_ID).getTopic(),
                         app.UnitThrtlBrkMsg(app.CLIENT_ID).getTopic())

    def test_onSteeringMsg(self):
        """
        The _onSteeringMsg function must modify the steering position
        based on the received message.
        """
        expectedModifier = 0.25
        steeringMsg = json.dumps({'unit id': 'test unit',
                                  'payload': {'angle': expectedModifier}})
        app._onSteeringMsg(None, None, steeringMsg)
        app.steering.modifyPosition.assert_called_once_with(expectedModifier)

    def test_onThrottleMsg(self):
        """
        The _onThrottleMsg function must modify the throttle position
        based on the received message.
        """
        expectedModifier = -0.90
        throttleMsg = json.dumps({'unit id': 'test unit',
                                  'payload': {'amplitude': expectedModifier}})
        app._onThrottleMsg(None, None, throttleMsg)
        app.throttle.modifyPosition.assert_called_once_with(expectedModifier)

    def test__initControlDevice(self):
        """
        The _initControlDevice function must create the two control device.
        """
        with patch('app.ControlDevice') as mockedControlDevice, \
                patch('app.ServoKit') as mockedServoKit:
            mockedControlDevice.side_effect = [Mock(), Mock()]
            mockedAppLogger = Mock()
            app._initControlDevices(mockedAppLogger)
            expectedCalls = [call.initServoKit(mockedServoKit,
                                               chanCount=app.PWM_CHAN_CNT,
                                               frequency=app.PWM_FREQ),
                             call(mockedAppLogger, app.STEERING_TYPE,
                                  (app.STEERING_MIN, app.STEERING_NEUTRAL, app.STEERING_MAX)),  # noqa: E501
                             call(mockedAppLogger, app.THROTTLE_TYPE,
                                  (app.THROTTLE_MIN, app.THROTTLE_NEUTRAL, app.THROTTLE_MAX))]  # noqa: E501
            mockedControlDevice.assert_has_calls(expectedCalls)

    def test__initMqttClientInit(self):
        """
        The _initMqttClient function must initialize the MQTT client.
        """
        mockedAppLogger = Mock()
        app._initMqttClient(mockedAppLogger)
        app.client.init.assert_called_once_with(mockedAppLogger,
                                                app.CLIENT_ID,
                                                app.CLIENT_PASSWORD)

    def test__initMqttClientSubscribe(self):
        """
        The _initMqttClient function must subscribe to the relevant topics.
        """
        mockedAppLogger = Mock()
        app._initMqttClient(mockedAppLogger)
        app.client.subscribe.assert_called_once_with(self.testSubs)

    def test__initMqttClientRegisterMsgCallbacks(self):
        """
        The _initMqttClient function must register the message callbacks.
        """
        mockedAppLogger = Mock()
        app._initMqttClient(mockedAppLogger)
        expectedCalls = [call(self.testSubs[0], app._onSteeringMsg),
                         call(self.testSubs[1], app._onThrottleMsg)]
        app.client.registerMsgCallback.assert_has_calls(expectedCalls)

    def test_initControlDevices(self):
        """
        The init function must initialize the control devices.
        """
        with patch('app.initLogger') as mockedInitLogger, \
                patch('app._initControlDevices') as mockedInitCtrlDev, \
                patch('app._initMqttClient'):
            mockedAppLogger = Mock()
            mockedInitLogger.return_value = mockedAppLogger
            app.init()
            mockedInitCtrlDev.assert_called_once_with(mockedAppLogger)

    def test_initMqttClient(self):
        """
        The init function must initialize the control devices.
        """
        with patch('app.initLogger') as mockedInitLogger, \
                patch('app._initControlDevices'), \
                patch('app._initMqttClient') as mockedInitMqttClient:
            mockedAppLogger = Mock()
            mockedInitLogger.return_value = mockedAppLogger
            app.init()
            mockedInitMqttClient.assert_called_once_with(mockedAppLogger)