from adafruit_servokit import ServoKit
import sys

from controlDevice import ControlDevice
import mqttClient as client
from messages.unitSteeringMsg import UnitSteeringMsg
from messages.unitThrtlBrkMsg import UnitThrtlBrkMsg
from logger import initLogger


PWM_CHAN_CNT = 16
PWM_FREQ = 180
STEERING_TYPE = ControlDevice.TYPE_DIRECT
STEERING_MIN = ControlDevice.MIN_ROTATION
STEERING_MAX = ControlDevice.MAX_ROTATION
STEERING_NEUTRAL = ControlDevice.DEFAULT_CENTER

THROTTLE_TYPE = ControlDevice.TYPE_ESC
THROTTLE_MIN = ControlDevice.MIN_ROTATION
THROTTLE_MAX = ControlDevice.MAX_ROTATION
THROTTLE_NEUTRAL = ControlDevice.DEFAULT_CENTER

CLIENT_ID = 'f1-operator'
CLIENT_PASSWORD = '12345'

steering = None
throttle = None
logger = None


def _onSteeringMsg(client, usrData, msg) -> None:
    """
    The on steering message callback.

    Params:
        client:     The client instance.
        usrData:    The user data.
        msg:        The received message.
    """
    global logger
    global steering
    logger.debug(f"received steering message: {msg}")
    steeringMsg = UnitSteeringMsg(CLIENT_ID)
    steeringMsg.fromJson(msg)
    steering.modifyPosition(steeringMsg.getAngle())


def _onThrottleMsg(client, usrData, msg) -> None:
    """
    The on throttle message callback.

    Params:
        client:     The client instance.
        usrData:    The user data.
        msg:        The received message.
    """
    global logger
    global throttle
    logger.debug(f"received throttle message: {msg}")
    throttleMsg = UnitThrtlBrkMsg(CLIENT_ID)
    throttleMsg.fromJson(msg)
    throttle.modifyPosition(throttleMsg.getAmplitude())


def _initControlDevices(appLogger) -> None:
    """
    Initialize the control devices.

    Params:
        appLogger:  The appLogger.
    """
    global logger
    global steering
    global throttle
    logger.info('initializing control devices')
    ControlDevice.initServoKit(ServoKit, chanCount=PWM_CHAN_CNT,
                               frequency=PWM_FREQ)
    steering = ControlDevice(appLogger, STEERING_TYPE,
                             (STEERING_MIN, STEERING_NEUTRAL, STEERING_MAX))
    throttle = ControlDevice(appLogger, THROTTLE_TYPE,
                             (THROTTLE_MIN, THROTTLE_NEUTRAL, THROTTLE_MAX))
    logger.info('control devices initialized')


def _initMqttClient(appLogger) -> None:
    """
    Initialize the MQTT client.
    """
    subs = (UnitSteeringMsg(CLIENT_ID).getTopic(),
            UnitThrtlBrkMsg(CLIENT_ID).getTopic())
    logger.info('initialize the MQTT client')
    client.init(appLogger, CLIENT_ID, CLIENT_PASSWORD)
    client.subscribe(subs)
    client.registerMsgCallback(subs[0], _onSteeringMsg)
    client.registerMsgCallback(subs[1], _onThrottleMsg)
    logger.info('MQTT client initialized')


def init() -> None:
    """
    App initialization.
    """
    global logger
    global steering
    global throttle

    appLogger = initLogger()
    logger = appLogger.getLogger('APP')
    _initControlDevices(appLogger)
    _initMqttClient(appLogger)


def run() -> None:
    """
    Run the application.
    """
    global logger
    global steering
    global throttle
    logger.info('starting RC control mission operator')
    init()
    while True:
        pass


def stop():
    """
    Stop the application.
    """
    global logger
    global steering
    global throttle
    logger.info('stopping RC control mission operator')
    steering.stop_pulse()
    throttle.stop_pulse()
    client.disconnect()


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        stop()
        sys.exit(0)
