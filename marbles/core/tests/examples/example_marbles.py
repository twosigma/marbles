#
#       Copyright (c) 2017 Two Sigma Investments, LP
#       All Rights Reserved
#
#       THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE OF
#       Two Sigma Investments, LP.
#
#       The copyright notice above does not evidence any
#       actual or intended publication of such source code.
#

'''Example marbles suite.'''

import marbles.core


class Response:

    def __init__(self, json):
        self._json = json

    def json(self):
        return self._json


class requests:

    @classmethod
    def put(cls, endpoint, data=None):
        return Response({
            'code': 409,
            'status': 'Conflict',
            'details': 'Resource with id {} already exists'.format(data['id'])
        })


class ResponseTestCase(marbles.core.TestCase):
    '''Test application responses.'''

    def test_create_resource(self):
        endpoint = 'http://example.com/api/v1/resource'
        data = {'id': '1', 'name': 'Jane'}
        self.assertEqual(
            requests.put(endpoint, data=data).json()['code'],
            201)


if __name__ == '__main__':
    marbles.core.main()
