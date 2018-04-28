#!/usr/bin/env python3
import logging
import time

import jwt

logger = logging.getLogger(__name__)


class JWTCheck:

    def setup(self, secret):
        self.secret = secret

    def from_epoch(self, epoch):
        return time.strftime("%a, %d %b %Y %H:%M:%S %z", time.localtime(epoch))

    def jwt_check(self, token, audiences):
        try:
            for aud in audiences:
                try:
                    payload = jwt.decode(token, self.secret, audience=aud, algorithms=['HS512', 'HS256'])
                    if payload:
                        logger.info('JWT Token Authorisation Accepted')
                        logger.info(
                            'aud: %s, expires: %s, email: %s',
                            payload['aud'],
                            self.from_epoch(payload.get('exp')),
                            payload['sub']
                        )
                        return True
                except (
                    jwt.exceptions.ExpiredSignatureError,
                    jwt.exceptions.InvalidAudienceError,
                    jwt.exceptions.InvalidSignatureError,
                    jwt.exceptions.DecodeError
                ) as e:
                    logger.info('JWT Check for aud `%s` not passed: %s', aud, e)
                    continue
            logger.info('JWT token not accepted')
        except Exception as e:
            logger.error('JWT Check raised unhandled exception: %s', e)
        return False


JWT = JWTCheck()
