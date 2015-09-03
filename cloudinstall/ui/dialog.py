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

from __future__ import unicode_literals
from urwid import (LineBox, ListBox,
                   BoxAdapter, WidgetWrap,
                   RadioButton, Divider, Button,
                   signals, emit_signal, connect_signal)
from collections import OrderedDict
from cloudinstall.ui.input import EditInput
from cloudinstall.ui.lists import SimpleList
from cloudinstall.ui.utils import Color, Padding

import logging

log = logging.getLogger('cloudinstall.ui.dialog')


""" re-usable dialog widgets """


class Dialog(WidgetWrap):

    __metaclass__ = signals.MetaSignals
    signals = ['done']
    key_conversion_map = {'tab': 'down', 'shift tab': 'up'}

    def __init__(self, title, cb):
        self.title = title
        self.cb = cb
        self.input_items = OrderedDict()
        self.input_lbox = []
        self.btn_pile = None
        self.btn_confirm = Color.button_primary(
            Button("Confirm", self.submit),
            focus_map='button_primary focus')
        self.btn_cancel = Color.button_secondary(
            Button("Cancel", self.cancel),
            focus_map='button_secondary focus')

    def show(self):
        w = self._build_widget()
        w = Color.dialog(w)

        connect_signal(self, 'done', self.cb)
        super().__init__(ListBox(w))

    def keypress(self, size, key):
        key = self.key_conversion_map.get(key, key)
        return super().keypress(size, key)

    def add_input(self, key, caption, **kwargs):
        """ Adds input boxes while setting their label attributes for
        easy retrieval of data

        :param str caption: viewable label of input
        :param dict **kwargs: additional Edit attributes
        """
        self.input_items[key] = EditInput(caption=caption, **kwargs)

    def add_radio(self, item, group=[]):
        """ Adds radio selections
        """
        self.input_items[item] = RadioButton(group, item)

    def _build_widget(self, **kwargs):
        log.debug("DIALOG build widget")
        total_items = []
        for _item in self.input_items.keys():
            total_items.append(Color.string_input(
                self.input_items[_item], focus_map='string_input focus'))

        body = [
            total_items,
            Divider(),
            Padding.center_20(self.btn_confirm),
            Padding.center_20(self.btn_cancel)
        ]
        container_lbox = SimpleList(body)
        log.debug(container_lbox)
        container_adapter = BoxAdapter(container_lbox,
                                       height=len(body))
        log.debug(container_adapter)
        return LineBox(container_adapter, title=self.title)

    def submit(self, button):
        self.emit_done_signal(self.input_items)

    def cancel(self, button):
        raise SystemExit("Installation cancelled.")

    def emit_done_signal(self, *args):
        emit_signal(self, 'done', *args)
