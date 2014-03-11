#
# client.py - Juju api client
#
# Copyright 2014 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from ws4py.client.threadedclient import WebSocketClient
import json

"""
Example parameters passed to juju:

params = {}
params['Type'] = "Admin"
params['Request'] = 'Login'
params['RequestId'] = 1
params['Params'] = {'AuthTag': 'user-admin',
                    'Password': 'f0d44f279b47cc8b5f7ea291f5e3b30a'}
"""

class JujuWS(WebSocketClient):
    def opened(self):
        self.send(json.dumps(params))

    def closed(self, code, reason):
        print(("Closed", code, reason))

    def received_message(self, m):
        print(("Message", json.loads(m.data.decode('utf-8'))))


class JujuClient:
    """ Juju client class """
    def __init__(self, params, url='juju-bootstrap.master:17070', protocols=['https-only']):
        self.params = params
        self.conn = JujuWS(self.url, protocols=self.protocols)

    def login(self):
        self.conn.connect()

    def close(self):
        self.conn.close()

    def get(self, params):
        """ Get json data from juju api daemon """
        self.conn.send(json.dumps(params))
