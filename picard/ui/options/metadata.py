# -*- coding: utf-8 -*-
#
# Picard, the next-generation MusicBrainz tagger
# Copyright (C) 2006 Lukáš Lalinský
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

from PyQt4 import QtCore, QtGui
from picard.config import BoolOption, TextOption
from picard.ui.options import OptionsPage, OptionsCheckError, register_options_page
from picard.ui.ui_options_metadata import Ui_MetadataOptionsPage
import operator
import locale


class MetadataOptionsPage(OptionsPage):

    NAME = "metadata"
    TITLE = N_("Metadata")
    PARENT = None
    SORT_ORDER = 20
    ACTIVE = True

    options = [
        TextOption("setting", "va_name", u"Various Artists"),
        TextOption("setting", "nat_name", u"[non-album tracks]"),
        BoolOption("setting", "translate_artist_names", False),
        BoolOption("setting", "release_ars", True),
        BoolOption("setting", "track_ars", False),
        BoolOption("setting", "folksonomy_tags", False),
        BoolOption("setting", "convert_punctuation", False),
        BoolOption("setting", "standardize_tracks", False),
        BoolOption("setting", "standardize_releases", False),
        BoolOption("setting", "standardize_artists", False),
    ]

    def __init__(self, parent=None):
        super(MetadataOptionsPage, self).__init__(parent)
        self.ui = Ui_MetadataOptionsPage()
        self.ui.setupUi(self)
        self.connect(self.ui.va_name_default, QtCore.SIGNAL("clicked()"), self.set_va_name_default)
        self.connect(self.ui.nat_name_default, QtCore.SIGNAL("clicked()"), self.set_nat_name_default)

    def load(self):
        self.ui.translate_artist_names.setChecked(self.config.setting["translate_artist_names"])
        self.ui.convert_punctuation.setChecked(self.config.setting["convert_punctuation"])
        self.ui.release_ars.setChecked(self.config.setting["release_ars"])
        self.ui.track_ars.setChecked(self.config.setting["track_ars"])
        self.ui.folksonomy_tags.setChecked(self.config.setting["folksonomy_tags"])
        self.ui.va_name.setText(self.config.setting["va_name"])
        self.ui.nat_name.setText(self.config.setting["nat_name"])
        self.ui.standardize_tracks.setChecked(self.config.setting["standardize_tracks"])
        self.ui.standardize_releases.setChecked(self.config.setting["standardize_releases"])
        self.ui.standardize_artists.setChecked(self.config.setting["standardize_artists"])

    def save(self):
        self.config.setting["translate_artist_names"] = self.ui.translate_artist_names.isChecked()
        self.config.setting["convert_punctuation"] = self.ui.convert_punctuation.isChecked()
        self.config.setting["release_ars"] = self.ui.release_ars.isChecked()
        self.config.setting["track_ars"] = self.ui.track_ars.isChecked()
        self.config.setting["folksonomy_tags"] = self.ui.folksonomy_tags.isChecked()
        self.config.setting["va_name"] = self.ui.va_name.text()
        self.config.setting["nat_name"] = self.ui.nat_name.text()
        self.config.setting["standardize_tracks"] = self.ui.standardize_tracks.isChecked()
        self.config.setting["standardize_releases"] = self.ui.standardize_releases.isChecked()
        self.config.setting["standardize_artists"] = self.ui.standardize_artists.isChecked()

    def set_va_name_default(self):
        self.ui.va_name.setText(self.options[0].default)
        self.ui.va_name.setCursorPosition(0)

    def set_nat_name_default(self):
        self.ui.nat_name.setText(self.options[1].default)
        self.ui.nat_name.setCursorPosition(0)


register_options_page(MetadataOptionsPage)
