#!/usr/bin/env python3
import json
import sys
import os

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
    # client = app.routes.flaskapp.test_client()
    sys.argv = ['']
    os.environ["CLOUD_NAME"] = config.CLOUD_NAME
    os.environ["CLOUD_APIKEY"] = config.API_KEY
    os.environ["CLOUD_SECRET"] = config.API_SECRET
    os.environ["CLOUD_JWT_SECRET"] = config.JWT_SECRET
    os.environ["CLOUD_DEFAULT_FOLDER"] = config.FOLDER
    os.environ["CLOUD_CORS"] = "false"

    flaskapp, config = app.setup.setup()
    client = flaskapp.test_client()

    @patch.object(cloudinary, 'config', return_value=[])
    def testSetupCloudinary(self, cloudinary_config):
        app.setup.setup()
        cloudinary_config.assert_called_with(
            api_key=config.API_KEY, api_secret=config.API_SECRET, cloud_name=config.CLOUD_NAME)

    def TestWrongAudienceJWTToken(self):
        self.assertEqual(JWT.jwt_check(self.jwt['not-admin'], ['admin']), False)

    def TestValidJWTToken(self):
        self.assertEqual(JWT.jwt_check(self.jwt['admin'], ['admin']), True)

    @patch.object(cloudinary.api, 'resources', return_value={'resources': []})
    def testList(self, resources):
        res = self.client.get('/list/', headers={'Authorization': 'Bearer {}'.format(self.jwt['admin'])})
        resources.assert_called_with(prefix='{}/'.format(config.FOLDER), type='upload')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json, {'files': [], 'result': 'OK'})

    def TestMissingEnvironmentVariable(self):
        del os.environ['CLOUD_APIKEY']
        sys.argv = ['']
        with self.assertRaises(SystemExit):
            app.setup.setup()
        os.environ['CLOUD_APIKEY'] = config.API_KEY
        app.setup.setup()
