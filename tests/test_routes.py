#!/usr/bin/env python3
import json
import sys
import base64

import cloudinary
import cloudinary.uploader
import cloudinary.api

import unittest
from unittest.mock import patch

import app.routes
from app.jwt_check import JWT
import app.setup
import tests.config as config

JWT.setup('testsecret')


class TestRoutes(unittest.TestCase):

    jwt = json.load(open('tests/jwt.json'))
    urls = json.load(open('tests/urls.json'))
    sys.argv = ['', '--name', config.CLOUD_NAME, '--api_key', config.API_KEY, '--api_secret', config.API_SECRET,
                '--jwt_secret', config.JWT_SECRET, '--folder', config.FOLDER, '--cors']
    flaskapp, _ = app.setup.setup()
    client = flaskapp.test_client()

    @patch.object(JWT, 'jwt_check', return_value=True)
    def testParseHeader(self, jwt_check):
        self.client.get('/auth', headers={'Authorization': 'Bearer abc'})
        jwt_check.assert_called_with('abc', ['admin'])

    def testNonBearerAuth(self):
        resp = self.client.get('/auth', headers={'Authorization': 'Beehive {}'.format(self.jwt['admin'])})
        self.assertEqual(resp.status_code, 401)

    def testMissingAuth(self):
        resp = self.client.get('/auth')
        self.assertEqual(resp.status_code, 401)

    def testCorrectAuth(self):
        resp = self.client.get('/auth', headers={'Authorization': 'Bearer {}'.format(self.jwt['admin'])})
        self.assertEqual(resp.status_code, 200)

    def testBadAuth(self):
        resp = self.client.get('/auth', headers={'Authorization': 'Bearer {}'.format(self.jwt['not-admin'])})
        self.assertEqual(resp.status_code, 401)

    def testURLTransform(self):
        url = app.routes.get_transform(self.urls['tansform_format_auto_quality_eco']['from'], 'f_auto,q_auto:eco')
        self.assertEqual(url, self.urls['tansform_format_auto_quality_eco']['to'])

    def testURLThumbnail(self):
        url = app.routes.get_thumb(self.urls['tansform_thumb_w100_h100']['from'], 100, 100)
        self.assertEqual(url, self.urls['tansform_thumb_w100_h100']['to'])

    def testRemovePrefix(self):
        base64_data = app.routes.remove_prefix('data:image/png;base64,iVBORw')
        self.assertEqual(base64_data, 'iVBORw')

    def testRemovePrefixInvalidBadData(self):
        base64_data = app.routes.remove_prefix(':image/png;base64,iVBORw')
        self.assertEqual(base64_data, None)

    def testRemovePrefixInvalidNoComma(self):
        base64_data = app.routes.remove_prefix('data:image/png;base64iVBORw')
        self.assertEqual(base64_data, None)

    def testRemovePrefixInvalidTwoCommas(self):
        base64_data = app.routes.remove_prefix('data:image/png;base64,iV,BORw')
        self.assertEqual(base64_data, None)

    def testRemovePrefixInvalidNotString(self):
        base64_data = app.routes.remove_prefix(None)
        self.assertEqual(base64_data, None)

    def testHelloWorld(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.decode('utf-8'), 'Hello World!')

    def testNoAuthOrContentForOptions(self):
        resp = self.client.options('/list/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {'result': 'OK'})

    @patch.object(cloudinary.api, 'resources', return_value={'resources': []})
    def testList(self, resources):
        res = self.client.get('/list/', headers={'Authorization': 'Bearer {}'.format(self.jwt['admin'])})
        resources.assert_called_with(prefix='{}/'.format(config.FOLDER), type='upload')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json, {'files': [], 'result': 'OK'})

    def testBadAuthList(self):
        resp = self.client.get('/list/', headers={'Authorization': 'Bearer {}'.format(self.jwt['not-admin'])})
        self.assertEqual(resp.status_code, 401)

    @patch.object(cloudinary, 'config', return_value=[])
    def testSetupCloudinary(self, cloudinary_config):
        app.setup.setup()
        cloudinary_config.assert_called_with(
            api_key=config.API_KEY, api_secret=config.API_SECRET, cloud_name=config.CLOUD_NAME)

    @patch.object(cloudinary.uploader, 'upload', return_value={'public_id': config.PUBLIC_ID})
    @patch.object(cloudinary.utils, 'cloudinary_url', return_value=(config.IMAGE_URL, ''))
    def testUploadFile(self, cloudinary_url, upload):
        response = self.client.post(
            '/upload',
            headers={'Authorization': 'Bearer {}'.format(self.jwt['admin'])},
            json={'image': config.IMAGE_BASE64}
        )
        upload.assert_called_with(base64.decodebytes(config.IMAGE_BASE64_BYTES), folder=config.FOLDER)
        cloudinary_url.assert_called_with(config.PUBLIC_ID, fetch_format='auto', quality='auto:eco', secure=True)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {'result': 'OK', 'url': config.IMAGE_URL})

    @patch.object(cloudinary.uploader, 'upload', return_value={'public_id': config.PUBLIC_ID})
    @patch.object(cloudinary.utils, 'cloudinary_url', return_value=[])
    def testUploadFileBadCloudinaryResponse(self, cloudinary_url, upload):
        response = self.client.post(
            '/upload',
            headers={'Authorization': 'Bearer {}'.format(self.jwt['admin'])},
            json={'image': config.IMAGE_BASE64}
        )
        upload.assert_called_with(base64.decodebytes(config.IMAGE_BASE64_BYTES), folder=config.FOLDER)
        cloudinary_url.assert_called_with(config.PUBLIC_ID, fetch_format='auto', quality='auto:eco', secure=True)
        self.assertEqual(response.status_code, 500)

    @patch.object(cloudinary.uploader, 'upload', return_value={})
    @patch.object(cloudinary.utils, 'cloudinary_url', return_value={})
    def testUploadBadFile(self, cloudinary_url, upload):
        response = self.client.post(
            '/upload',
            headers={'Authorization': 'Bearer {}'.format(self.jwt['admin'])},
            json={'image': 'abcdef'}
        )
        upload.assert_not_called()
        cloudinary_url.assert_not_called()
        self.assertEqual(response.status_code, 400)

    def testBadAuthUpload(self):
        resp = self.client.post('/upload', headers={'Authorization': 'Bearer {}'.format(self.jwt['not-admin'])})
        self.assertEqual(resp.status_code, 401)

    def testNoAuthOrContentForOptionsUpload(self):
        resp = self.client.options('/upload')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {'result': 'OK'})
