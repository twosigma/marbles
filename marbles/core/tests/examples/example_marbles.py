#
#  Copyright (c) 2018-2023 Two Sigma Open Source, LLC
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.
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
        data = {'id': '1', 'name': 'Little Bobby Tables'}
        self.assertEqual(
            requests.put(endpoint, data=data).json()['code'],
            201)


if __name__ == '__main__':
    marbles.core.main()
