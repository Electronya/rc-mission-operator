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
        self.testSubs = (app.UnitWhldCmdMsg(app.CLIENT_ID).getTopic())

    def test_onCommandMsgSteering(self):
        """
        The _onCommandMsg function must modify the steering position
        based on the received message.
        """
        expectedModifier = 0.25
        commandMsg = json.dumps({'unit id': 'test unit',
                                 'payload': {'steering': expectedModifier,
                                             'throttle': -0.45}})
        app._onCommandMsg(None, None, commandMsg)
        app.steering.modifyPosition.assert_called_once_with(expectedModifier)

    def test_onCommandMsgThrottle(self):
        """
        The _onCommandMsg function must modify the throttle position
        based on the received message.
        """
        expectedModifier = -0.90
        throttleMsg = json.dumps({'unit id': 'test unit',
                                  'payload': {'steering': -0.23,
                                              'throttle': expectedModifier}})
        app._onCommandMsg(None, None, throttleMsg)
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
        expectedCalls = [call(self.testSubs[0], app._onCommandMsg)]
        app.client.registerMsgCallback.assert_has_calls(expectedCalls)

    def test__sendCxnState(self):
        """
        The _sendCxnState function must send the online connection state.
        """
        app._sendCxnState()
        cxnStateMsg, = app.client.publish.call_args.args
        self.assertEqual(cxnStateMsg.getUnit(), app.CLIENT_ID)
        self.assertTrue(cxnStateMsg.isOnline())

    def test__sendUnitState(self):
        """
        The _sendUnitState function must send the current unit state.
        """
        expectedSteeringMod = 0.45
        expectedThrottleMod = -0.97
        app.steering.getModifier.return_value = expectedSteeringMod
        app.throttle.getModifier.return_value = expectedThrottleMod
        app._sendUnitState()
        unitStateMsg, = app.client.publish.call_args.args
        self.assertEqual(unitStateMsg.getUnit(), app.CLIENT_ID)
        self.assertEqual(unitStateMsg.getSteering(), expectedSteeringMod)
        self.assertEqual(unitStateMsg.getThrottle(), expectedThrottleMod)

    def test_initControlDevices(self):
        """
        The init function must initialize the control devices.
        """
        with patch('app.initLogger') as mockedInitLogger, \
                patch('app._initControlDevices') as mockedInitCtrlDev, \
                patch('app._initMqttClient'), \
                patch('app._sendCxnState'):
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
                patch('app._initMqttClient') as mockedInitMqttClient, \
                patch('app._sendCxnState'):
            mockedAppLogger = Mock()
            mockedInitLogger.return_value = mockedAppLogger
            app.init()
            mockedInitMqttClient.assert_called_once_with(mockedAppLogger)

    def test_initStartLoop(self):
        """
        The init function must start the client network loop.
        """
        with patch('app.initLogger') as mockedInitLogger, \
                patch('app._initControlDevices'), \
                patch('app._initMqttClient'), \
                patch('app._sendCxnState'):
            mockedAppLogger = Mock()
            mockedInitLogger.return_value = mockedAppLogger
            app.init()
            app.client.startLoop.assert_called_once()

    def test_initSendCxnStateMsg(self):
        """
        The init function must notify its connection state.
        """
        with patch('app.initLogger') as mockedInitLogger, \
                patch('app._initControlDevices'), \
                patch('app._initMqttClient'), \
                patch('app._sendCxnState') as mockedSendCxnState:
            mockedAppLogger = Mock()
            mockedInitLogger.return_value = mockedAppLogger
            app.init()
            mockedSendCxnState.assert_called_once()

    def test_runSendUnitState(self):
        """
        The run function must send the unit current state.
        """
        with patch('app.time') as mockedTime, \
                patch('app._sendUnitState') as mockedSendUnitState:
            mockedTime.sleep.side_effect = Exception
            try:
                app.run()
            except Exception:
                mockedSendUnitState.assert_called_once()

    def test_runLoopPeriod(self):
        """
        The run function must loop based on the state update period.
        """
        with patch('app.time') as mockedTime:
            mockedTime.sleep.side_effect = Exception
            try:
                app.run()
            except Exception:
                mockedTime.sleep.assert_called_once_with(app.STATE_UPDATE_PERIOD)   # noqa: E501

    def test_stopSetControlDevicesToNeutral(self):
        """
        The stop function must set to neutral the control devices.
        """
        app.stop()
        app.steering.setToNeutral.assert_called_once()
        app.throttle.setToNeutral.assert_called_once()

    def test_stopDisconnectClient(self):
        """
        The stop function must disconnect the MQTT client.
        """
        app.stop()
        app.client.disconnect.assert_called_once()
