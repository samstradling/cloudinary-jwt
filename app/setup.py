#!/usr/bin/env python3
import sys
import os
import logging
import argparse

from flask_cors import CORS
import cloudinary

from app.config import DEFAULT_PORT, DEFAULT_HOST, DEFAULT_FOLDER
from app.jwt_check import JWT
from app.routes import flaskapp

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--name', '-n', help='"Cloud name" from cloudinary console',
        required=True, dest='cloud_name'
    )
    parser.add_argument(
        '--api_key', '-k', help='"API Key" from cloudinary console',
        required=True, dest='api_key'
    )
    parser.add_argument(
        '--api_secret', '-s', help='"API Secret" from cloudinary console',
        required=True, dest='api_secret'
    )
    parser.add_argument(
        '--jwt_secret', '-j', help='JWT Secret used to decrypt tokens.',
        required=True, dest='jwt_secret'
    )
    parser.add_argument(
        '--port', '-p', required=False, dest='port',
        default=DEFAULT_PORT, type=int,
        help='Port to run the app on (default: {}).'.format(DEFAULT_PORT)
    )
    parser.add_argument(
        '--host', required=False, dest='host', default=DEFAULT_HOST,
        help='Host to run the app on (default {}).'.format(DEFAULT_HOST)
    )
    parser.add_argument(
        '--cors', required=False, dest='cors', action='store_true',
        help='Enable Cross-Origin Resource Sharing (CORS)'
    )
    parser.add_argument(
        '--folder', default=DEFAULT_FOLDER, dest='default_folder',
        help='Cloudinary folder to upload to and list files in.'
    )
    return vars(parser.parse_args())


def parse_env():
    try:
        return {
            'cloud_name': os.environ['CLOUD_NAME'],
            'api_key': os.environ['CLOUD_APIKEY'],
            'api_secret': os.environ['CLOUD_SECRET'],
            'jwt_secret': os.environ['CLOUD_JWT_SECRET'],
            'port': int(os.getenv('CLOUD_PORT', DEFAULT_PORT)),
            'host': os.getenv('CLOUD_HOST', DEFAULT_HOST),
            'cors': bool(os.getenv('CLOUD_CORS', "False").lower() == 'true'),
            'default_folder': os.getenv('CLOUD_DEFAULT_FOLDER', DEFAULT_FOLDER),
        }
    except KeyError as e:
        logger.error('Missing environment variable(s): %s', e)
        sys.exit(1)


def setup():

    if len(sys.argv) > 1:
        config = dict(parse_args())
    else:
        logger.info('env')
        config = parse_env()

    logger.error(config)
    cloudinary.config(
        cloud_name=config['cloud_name'],
        api_key=config['api_key'],
        api_secret=config['api_secret'],
    )
    flaskapp.config['CUSTOM'] = {
        'default_folder': config['default_folder'],
    }
    JWT.setup(config['jwt_secret'])
    if config['cors']:
        CORS(flaskapp, resources={'/upload': {'origins': '*'}})
    return flaskapp, config
