#!/usr/bin/env python3
import json
import sys

import unittest

from app.jwt_check import JWT
import app.setup
import tests.config as config


class TestJWTCheck(unittest.TestCase):

    sys.argv = ['', '--name', config.CLOUD_NAME, '--api_key', config.API_KEY, '--api_secret',
                config.API_SECRET, '--jwt_secret', config.JWT_SECRET, '--folder', config.FOLDER]
    app.setup.setup()
    jwt = json.load(open('tests/jwt.json'))

    def TestExpiredJWTToken(self):
        self.assertEqual(JWT.jwt_check(self.jwt['expired'], ['admin']), False)

    def TestWrongAudienceJWTToken(self):
        self.assertEqual(JWT.jwt_check(self.jwt['not-admin'], ['admin']), False)

    def TestValidJWTToken(self):
        self.assertEqual(JWT.jwt_check(self.jwt['admin'], ['admin']), True)

    def TestInvalidSecretJWTToken(self):
        self.assertEqual(JWT.jwt_check(self.jwt['wrong-secret'], ['admin']), False)

    def TestMultipleAudJWTToken(self):
        self.assertEqual(JWT.jwt_check(self.jwt['admin'], ['something-else', 'admin']), True)

    def TestWrongAlgo(self):
        self.assertEqual(JWT.jwt_check(self.jwt['wrong-algo'], ['admin']), False)
