#!/usr/bin/env python3
import logging

import app.setup

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    flaskapp, config = app.setup.setup()
    flaskapp.run(host=config['host'], port=config['port'])
