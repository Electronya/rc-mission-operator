import logging
from unittest import TestCase
from unittest.mock import patch

import os
import sys

sys.path.append(os.path.abspath('./src'))

from logger import initLogger       # noqa: E402


class TestLogger(TestCase):
    """
    The logger test cases.
    """
    def setUp(self):
        """
        Test cases setup.
        """
        if 'APP_ENV' in os.environ:
            del os.environ['APP_ENV']

    def test_defaultLevel(self):
        """
        The initLogger function must set the logger level to info
        if no APP_ENV is defined.
        """
        with patch('logger.logging.basicConfig') as mockedBasicCfg:
            initLogger()
            mockedBasicCfg.assert_called_once_with(level=logging.INFO,
                                                   format='%(asctime)s'
                                                   ' %(levelname)s:'
                                                   '%(name)s:%(message)s')

    def test_devLevel(self):
        """
        The initLogger function must set the logger level to debug
        if the APP_ENV is defined as dev.
        """
        with patch('logger.logging.basicConfig') as mockedBasicCfg:
            os.environ['APP_ENV'] = 'dev'
            initLogger()
            mockedBasicCfg.assert_called_once_with(level=logging.DEBUG,
                                                   format='%(asctime)s'
                                                   ' %(levelname)s:'
                                                   '%(name)s:%(message)s')
