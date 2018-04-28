#!/usr/bin/env python3
import base64
import logging

from flask import Flask
from flask import request, jsonify

import cloudinary
import cloudinary.uploader
import cloudinary.api

from app.jwt_check import JWT

flaskapp = Flask(__name__)
flaskapp.config['UPLOAD_FOLDER'] = 'uploads/'
flaskapp.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


def check_jwt(request):
    auth = request.headers.get('Authorization', '').split(' ')
    token = auth[1] if len(auth) > 1 and auth[0].lower() == 'bearer' else ''
    return JWT.jwt_check(token, ['admin'])


def get_transform(url, transform='f_auto,q_auto:eco'):
    return url.replace('image/upload/', 'image/upload/{}/'.format(transform))


def get_thumb(url, width=200, height=200):
    return get_transform(url, 'c_thumb,f_auto,h_{},w_{},q_auto:eco'.format(width, height))


def remove_prefix(data_uri):
    if type(data_uri) is not str:
        return None
    parts = data_uri.split(',')
    if len(parts) == 2 and parts[0][0:5] == 'data:':
        return parts[1]
    return None


@flaskapp.route('/')
def hello():
    return "Hello World!"


@flaskapp.route('/auth', methods=['GET', 'OPTIONS'])
def auth():
    try:
        if not check_jwt(request):
            return jsonify({
                'result': 'NOT AUTHORISED',
            }), 401

        return jsonify({
            'result': 'OK'
        }), 200
    except Exception as e:
        logger.error('Unable to authenticate: {}'.format(e))
        return jsonify({
            'result': 'SERVER ERROR',
            'url': ''
        }), 500


@flaskapp.route('/list/', defaults={'path': ''}, methods=['GET', 'OPTIONS'])
@flaskapp.route('/list/<path:path>', methods=['GET', 'OPTIONS'])
def listfiles(path):
    try:
        if request.method == 'GET':
            if not check_jwt(request):
                return jsonify({
                    'result': 'NOT AUTHORISED',
                }), 401

            default_folder = flaskapp.config['CUSTOM']['default_folder']
            full_path = (default_folder + '/' if default_folder != '' else '') + path
            logger.info('listing files in dir \'%s\'', full_path)
            files = cloudinary.api.resources(prefix=full_path, type='upload')

            return jsonify({
                'result': 'OK',
                'files': [
                    {
                        'thumb': get_thumb(f['secure_url']),
                        'image': get_transform(f['secure_url'])
                    } for f in files['resources']
                ]
            }), 200
        return jsonify({
            'result': 'OK'
        }), 200
    except Exception as e:
        logger.error('Unable to list Cloudinary files: {}'.format(e))
        return jsonify({
            'result': 'SERVER ERROR',
            'url': ''
        }), 500


@flaskapp.route('/upload', methods=['POST', 'OPTIONS'])
def upload():
    try:
        if request.method == 'POST':

            if not check_jwt(request):
                return jsonify({
                    'result': 'NOT AUTHORISED',
                }), 401

            base64_data = remove_prefix(request.get_json()['image'])

            if base64_data is None:
                logger.error('Payload was malformed')
                return jsonify({
                    'result': 'BAD REQUEST'
                }), 400

            result = cloudinary.uploader.upload(
                base64.decodebytes(base64_data.encode()),
                folder=flaskapp.config['CUSTOM']['default_folder']
            )
            url = cloudinary.utils.cloudinary_url(
                result['public_id'],
                fetch_format='auto',
                quality='auto:eco',
                secure=True
            )
            if type(url) == tuple:
                url = url[0]
            if type(url) != str:
                logger.error('Reponse from Cloudinary was not a url.')
                return jsonify({
                    'result': 'SERVER ERROR',
                    'url': ''
                }), 500
            return jsonify({
                'result': 'OK',
                'url': url
            }), 201
        return jsonify({
            'result': 'OK'
        }), 200
    except Exception as e:
        logger.error('Unable to upload image to Cloudinary: {}'.format(e))
        return jsonify({
            'result': 'SERVER ERROR',
            'url': ''
        }), 500
