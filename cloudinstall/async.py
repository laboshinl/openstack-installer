# Copyright 2015 Canonical, Ltd.
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

""" Async Handler
Provides async operations for various api calls and other non-blocking
work.

The way this works is you create your IO/CPU bound thread:
.. code::
    def my_async_method(self):
        pool.submit(func, *args)

    # In your controller you would then call
    @coroutine
    def do_something():
        try:
           yield my_async_method()
        except:
           print("Error in threaded code")
        return
"""

from concurrent.futures import ThreadPoolExecutor


class Async:
    pool = ThreadPoolExecutor(4)
