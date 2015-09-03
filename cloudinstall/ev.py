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

import urwid
import sys
from cloudinstall.state import ControllerState
from cloudinstall.ui.palette import STYLES

import logging
import threading

log = logging.getLogger('cloudinstall.ev')


class EventLoop:

    """ Abstracts out event loops in different scenarios

    TODO: finish asyncio implementation when urwid 1.3.0
    becomes available.
    """

    def __init__(self, ui, config, log):
        self.ui = ui
        self.config = config
        self.log = log
        self.error_code = 0
        self._callback_map = {}

        self.loop = None

        if not self.config.getopt('headless'):
            self.loop = self._build_loop()
            self.loop.set_alarm_in(2, self.check_thread_exit_event)
            self._loop_thread = threading.current_thread()
            self._thread_exit_event = threading.Event()

    def register_callback(self, key, val):
        """ Registers some additional callbacks that didn't make sense
        to be added as part of its initial creation

        TODO: Doubt this is the best way as its more of a band-aid
        to core.py/add_charm and hotkeys in the gui.
        """
        self._callback_map[key] = val

    def _build_loop(self):
        """ Returns event loop configured with color palette """
        additional_opts = {
            'screen': urwid.raw_display.Screen(),
            'unhandled_input': self.header_hotkeys,
            'handle_mouse': False
        }
        additional_opts['screen'].set_terminal_properties(colors=256)
        additional_opts['screen'].reset_default_terminal_palette()
        loop = urwid.MainLoop(self.ui, STYLES, **additional_opts)
        return loop

    def header_hotkeys(self, key):
        if not self.config.getopt('headless'):
            if key in ['j', 'down']:
                self.ui.focus_next()
            if key in ['k', 'up']:
                self.ui.focus_previous()
            if key == 'esc':
                self.ui.hide_widget_on_top()
            if key in ['h', 'H', '?']:
                self.ui.show_help_info()
            if key in ['a', 'A', 'f6']:
                if self.config.getopt('current_state') != \
                   ControllerState.SERVICES:
                    return
                self.config.setopt('current_state',
                                   ControllerState.ADD_SERVICES.value)
            if key in ['q', 'Q']:
                self.exit(0)
            if key in ['r', 'R', 'f5']:
                self.ui.status_info_message("View was refreshed")
                self._callback_map['refresh_display']()

    def exit(self, err=0):
        self.error_code = err
        self.log.info("Stopping eventloop")
        if self.config.getopt('headless'):
            sys.exit(err)

        if threading.current_thread() == self._loop_thread:
            raise urwid.ExitMainLoop()
        else:
            self._thread_exit_event.set()
            log.debug("{} exiting, deferred UI exit "
                      "to main thread.".format(
                          threading.current_thread().name))

    def check_thread_exit_event(self, *args, **kwargs):
        if self._thread_exit_event.is_set():
            raise urwid.ExitMainLoop()
        self.loop.set_alarm_in(2, self.check_thread_exit_event)

    def close(self):
        pass

    def redraw_screen(self):
        if not self.config.getopt('headless'):
            try:
                self.loop.draw_screen()
            except AssertionError as e:
                self.log.exception("exception failure in redraw_screen")
                raise e

    def set_alarm_in(self, interval, cb):
        if not self.config.getopt('headless'):
            self.loop.set_alarm_in(interval, cb)
        return

    def run(self, cb=None):
        """ Run eventloop

        :param func cb: (optional) callback
        """
        if not self.config.getopt('headless'):
            try:
                self.loop.run()
            except:
                log.exception("Exception in ev.run():")
                raise
        return

    def __repr__(self):
        if self.config.getopt('headless'):
            return "<eventloop disabled>"
        else:
            return "<eventloop urwid based on select()>"
