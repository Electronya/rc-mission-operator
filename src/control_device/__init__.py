import logging
import time

import pigpio

class ControlDevice:
    """
    RC control device base class.
    """

    CHANNEL_0 = 12
    CHANNEL_1 = 13
    TYPE_SERVO = 0
    TYPE_ESC = 1
    FULL_DUTY = 1000000

    UNSUPPORTED_DEV_ERR_MSG = 'Unsupported device type.'
    GPIO_UNABLE_ERR_MSG1 = 'Unable to used gpio: '
    GPIO_UNABLE_ERR_MSG2 = 'as PWM channel.'
    CONNECTION_ERR_MSG = 'Unable to connected to PIGPIO service.'
    PWM_OP_FAILED_MSG = 'PWM operation failed, err: '

    def __init__(self, type=0, gpio=12, frequency=90,
        min_pulse=1.0, max_pulse=2, neutral=1.5):
        """
        Constructor.

        Params:
            type:       The type of device (servo or ESC). Default servo.
            gpio:       The PIGPIO number used for the PWM control signal. Default GPIO12.
            frequency:  The PWM signal frequency in Hz. Default 90 Hz.
            min_pulse:  The minimal pulse width in ms. Default: 1 ms.
            max_pulse:  The maximal pulse width in ms. Default: 2 ms.
            neutral:    The neutral position of the control device in ms. Default: 1.5 ms.
        """
        if type != self.TYPE_SERVO and type != self.TYPE_ESC:
            raise Exception(self.UNSUPPORTED_DEV_ERR_MSG)

        if gpio != self.CHANNEL_0 and gpio != self.CHANNEL_1:
            raise Exception(f"{self.GPIO_UNABLE_ERR_MSG1}{gpio}{self.GPIO_UNABLE_ERR_MSG2}")

        self._type = type
        self._freq = frequency
        self._min_pulse = self._pulse_length_to_duty(min_pulse, self._freq)
        self._max_pulse = self._pulse_length_to_duty(max_pulse, self._freq)
        self._neutral = self._pulse_length_to_duty(neutral, self._freq)
        self._range_min = self._neutral - self._min_pulse
        self._range_max = self._max_pulse - self._neutral
        self._modifier = 0.0

        self._gpio = gpio
        self._gpio_client = pigpio.pi()
        if not self._gpio_client.connected:
            raise Exception(self.CONNECTION_ERR_MSG)

        self._log_info()
        try:
            self._init_sequence()
        except Exception as err:
            raise err

    def _log_info(self):
        """
        Log the device information.
        """
        logging.info('created device:')
        logging.info(f"  - type: {self._type}")
        logging.info(f"  - GPIO: {self._gpio}")
        logging.info(f"  - freq: {self._freq}")
        logging.info(f"  - min pulse: {self._min_pulse}")
        logging.info(f"  - max pluse: {self._max_pulse}")
        logging.info(f"  - neutral: {self._neutral}")

    def _pulse_length_to_duty(self, pulse_length, frequency):
        """
        Convert a pulse length in ms to duty cycle in 1000000th.

        Params:
            pulse_length:   The pulse length in ms to convert.
            frequency:      The PWM frequency.

        Return:
            The duty cycle in 1000000th.
        """
        period = 1 / frequency * 1e3
        return int(round(self.FULL_DUTY * (pulse_length / period)))

    def _init_sequence(self):
        """
        Run the device initialization sequence.
        """
        if self._type == self.TYPE_ESC:
            rc = self._gpio_client.hardware_PWM(self._gpio, self._freq,
                self.FULL_DUTY)
            if rc != 0:
                raise Exception(f"{self.PWM_OP_FAILED_MSG}{rc}")

            time.sleep(1.4)

        rc = self._gpio_client.hardware_PWM(self._gpio, self._freq,
            self._neutral)
        if rc != 0:
            raise Exception(f"{self.PWM_OP_FAILED_MSG}{rc}")

    def get_pulse_info(self):
        """
        Get the control device pulse width limit and neutral value

        Return:
            A tuple containing the control device pulse information.
            (min_pluse, neutral, max_pulse).
        """
        return (self._min_pulse, self._neutral, self._max_pulse)

    def set_pulse(self, modifier=0.0):
        """
        Set the control device pulse width.

        Params:
            modifier:       The pulse modifier. This is a signed float representing
                            the amount of modification from the neutral pulse.
                            Default 0.0
        """
        self._modifier = modifier
        used_range = self._range_min
        if modifier > 0:
            used_range = self._range_max

        new_pulse = int(round(self._neutral + (used_range * modifier)))

        logging.debug(f"setting new pulse: {new_pulse}")

        self._gpio_client.set_servo_pulsewidth(self._gpio, new_pulse)

    def get_pulse(self):
        """
        Get the control device pulse width.

        Return:
            The current pulse modifier. This is a signed float representing
            the amount of modification from the neutral pulse.
        """
        return self._modifier

    def stop_pulse(self):
        """
        Stop the control device pulse.
        """
        rc = self._gpio_client.hardware_PWM(self._gpio, self._freq, 0)
        if rc != 0:
            raise Exception(f"{self.PWM_OP_FAILED_MSG}{rc}")
