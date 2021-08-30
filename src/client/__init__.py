import logging

import paho.mqtt.client as mqtt

from .messages import UnitConnectionState


class Client(mqtt.Client):
    """
    The mission commander mqtt client class.
    """
    CLIENT_ID = 'operator-f1'

    def __init__(self, password):
        """
        The mission commander mqtt client constructor.

        Params:
            password:       The client password creds.
        """
        logging.debug('initializing mqtt client')
        super().__init__(client_id=self.CLIENT_ID, transport='tcp')
        stateMsgPayload = \
            {UnitConnectionState.STATE_KEY: UnitConnectionState.OFFLINE_STATE}
        self._stateMsg = \
            UnitConnectionState(unit=self.CLIENT_ID, payload=stateMsgPayload)
        self.will_set(self._stateMsg.get_topic(),
                      self._stateMsg.to_json(),
                      qos=self._stateMsg.get_qos(), retain=True)
        self.username_pw_set(self.CLIENT_ID, password)

        logging.info('trying to connect to mission broker')
        self.connect('192.168.1.132', 1883)
        self.loop_start()

    def on_connect(self, client, usrData, flags, rc):
        """
        On connect event callback.

        Params:
            client:         The mqtt client.
            usrData:        Private user data if set.
            flags:          The response flags from the broker.
            rc:             The connection results.
        """
        logging.info('connected to mission broker.')
        payload = \
            {UnitConnectionState.STATE_KEY: UnitConnectionState.ONLINE_STATE}
        self._stateMsg.set_payload(payload)
        self.publish(self._stateMsg.get_topic(),
                     self._stateMsg.to_json(),
                     qos=self._stateMsg.get_qos(), retain=True)

    def on_disconnect(self, client, usrData, rc):
        """
        On disconnect event callback.

        Params:
            client:         The mqtt client.
            usrData:        Private user data if set.
            rc:             The connection results.
        """
        logging.info('disconnected from mission broker.')
        self.loop_stop()

    def on_message(self, client, usrData, msg):
        """
        On message event callback.

        Params:
            client:         The mqtt client.
            usrData         Private user data if set.
            msg:            The message recived.
        """
        receivedMsg = msg.payload.decode('utf-8')
        logging.info(f"message received: {receivedMsg}")
        # TODO: handle messages.

    def on_publish(self, client, usrData, mid):
        """
        On publish event callback.

        Params:
            client:         The mqtt client.
            usrData         Private user data if set.
            mid:            The message ID.
        """
        logging.debug(f"message published: mid {mid}")

    def on_subscribe(self, client, usrData, mid, granted_qos):
        """
        On publish event callback.

        Params:
            client:         The mqtt client.
            usrData         Private user data if set.
            mid:            The message ID.
            granted_qos:    The granted quality of service.
        """
        logging.debug(f"subscription done with mid: "
                      f"{mid}; and qos: {granted_qos}")

    def disconnect(self):
        """
        Disconnect the client from the broker.
        """
        logging.info('disconnecting from mission broker.')
        payload = \
            {UnitConnectionState.STATE_KEY: UnitConnectionState.OFFLINE_STATE}
        self._stateMsg.set_payload(payload)
        self.publish(self._stateMsg.get_topic(),
                     self._stateMsg.to_json(),
                     self._stateMsg.get_qos(), retain=True)
        super().disconnect()
