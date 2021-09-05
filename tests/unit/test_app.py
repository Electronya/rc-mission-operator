import json
import logging
from unittest import TestCase
from unittest.mock import Mock, patch

import os
import sys

sys.path.append(os.path.abspath('./src'))
mockedServoKit = Mock()
sys.modules['adafruit_servokit'] = mockedServoKit

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
