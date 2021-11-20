from adafruit_servokit import ServoKit
import sys
import time

from pkgs.controlDevice import ControlDevice
from pkgs.messages import UnitCxnStateMsg
from pkgs.messages import UnitWhldCmdMsg
from pkgs.messages import UnitWhldStateMsg
import pkgs.mqttClient as client
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

STATE_UPDATE_PERIOD = 0.025

steering = None
throttle = None
logger = None


def _onCommandMsg(client, usrData, msg) -> None:
    """
    The on command message callback.

    Params:
        client:     The client instance.
        usrData:    The user data.
        msg:        The received message.
    """
    global logger
    global steering
    global throttle
    logger.debug(f"received command message: {msg}")
    commandMsg = UnitWhldCmdMsg(CLIENT_ID)
    commandMsg.fromJson(msg)
    steering.modifyPosition(commandMsg.getSteering())
    throttle.modifyPosition(commandMsg.getThrottle())


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
    global logger
    subs = (UnitWhldCmdMsg(CLIENT_ID).getTopic())
    logger.info('initialize the MQTT client')
    client.init(appLogger, CLIENT_ID, CLIENT_PASSWORD)
    client.subscribe(subs)
    client.registerMsgCallback(subs[0], _onCommandMsg)
    logger.info('MQTT client initialized')


def _sendCxnState() -> None:
    """
    Send the connection state message.
    """
    global logger
    cxnStateMsg = UnitCxnStateMsg(CLIENT_ID)
    cxnStateMsg.setAsOnline()
    client.publish(cxnStateMsg)


def _sendUnitState() -> None:
    """
    Send the unit state.
    """
    global logger
    global steering
    global throttle
    unitStateMsg = UnitWhldStateMsg(CLIENT_ID)
    unitStateMsg.setSteering(steering.getModifier())
    unitStateMsg.setThrottle(throttle.getModifier())
    logger.debug(f"sending unit state: {unitStateMsg.getPayload()}")
    client.publish(unitStateMsg)


def init() -> None:
    """
    App initialization.
    """
    global logger
    appLogger = initLogger()
    logger = appLogger.getLogger('APP')
    _initControlDevices(appLogger)
    _initMqttClient(appLogger)
    client.startLoop()
    _sendCxnState()


def run() -> None:
    """
    Run the application.
    """
    global logger
    global steering
    global throttle
    logger.info('starting RC control mission operator')
    while True:
        _sendUnitState()
        time.sleep(STATE_UPDATE_PERIOD)


def stop():
    """
    Stop the application.
    """
    global logger
    global steering
    global throttle
    logger.info('stopping RC control mission operator')
    steering.setToNeutral()
    throttle.setToNeutral()
    client.disconnect()


if __name__ == '__main__':
    try:
        init()
        run()
    except Exception as e:
        logger.error(e)
        stop()
        sys.exit(0)
