# __main__.py
#
# Copyright (C) 2019 GabMus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gettext import gettext as _

import sys
import argparse
from gi.repository import Gtk, Gdk, Gio
from .confManager import ConfManager
from .feeds_manager import FeedsManager
from .app_window import GFeedsAppWindow
from .settings_window import GFeedsSettingsWindow
from .opml_manager import opml_to_rss_list, feeds_list_to_opml
from .opml_file_chooser import (
    GFeedsOpmlFileChooserDialog,
    GFeedsOpmlSavePathChooserDialog
)
from .manage_feeds_window import GFeedsManageFeedsWindow
import threading
from os.path import isfile
from .confirm_add_dialog import GFeedsConfirmAddDialog

def test():
    from .download_manager import download
    from .rss_parser import Feed
    confman = ConfManager()
    feeds = []
    for f in confman.conf['feeds']:
        feeds.append(Feed(download_feed(f)))

    for f in feeds:
        print(f)

    exit(0)

class GFeedsApplication(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(
            application_id = 'org.gabmus.gnome-feeds',
            flags = Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs
        )
        self.confman = ConfManager()
        self.feedman = FeedsManager()
        self.window = GFeedsAppWindow()
        self.window.connect('destroy', self.on_destroy_window)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        actions = [
            {
                'name': 'set_all_read',
                'func': self.set_all_read
            },
            {
                'name': 'set_all_unread',
                'func': self.set_all_unread
            },
            {
                'name': 'manage_feeds',
                'func': self.manage_feeds
            },
            {
                'name': 'import_opml',
                'func': self.import_opml
            },
            {
                'name': 'export_opml',
                'func': self.export_opml
            },
            {
                'name': 'settings',
                'func': self.show_settings_window
            },
            {
                'name': 'shortcuts',
                'func': self.show_shortcuts_window
            },
            {
                'name': 'about',
                'func': self.show_about_dialog
            },
            {
                'name': 'quit',
                'func': self.on_destroy_window
            }
        ]

        for a in actions:
            c_action = Gio.SimpleAction.new(a['name'], None)
            c_action.connect('activate', a['func'])
            self.add_action(c_action)

    def set_all_read(self, *args):
        for row in self.window.sidebar.listbox.get_children():
            row.popover.set_read(True)

    def set_all_unread(self, *args):
        for row in self.window.sidebar.listbox.get_children():
            row.popover.set_read(False)

    def manage_feeds(self, *args):
        mf_win = GFeedsManageFeedsWindow(
            self.window
        )
        mf_win.present()

    def add_opml_feeds(self, f_path):
        n_feeds_urls_l = opml_to_rss_list(f_path)
        for url in n_feeds_urls_l:
            self.feedman.add_feed(url)

    def import_opml(self, *args):
        dialog = GFeedsOpmlFileChooserDialog(self.window)
        res = dialog.run()
        # dialog.close()
        if res == Gtk.ResponseType.ACCEPT:
            self.add_opml_feeds(dialog.get_filename())

    def export_opml(self, *args):
        dialog = GFeedsOpmlSavePathChooserDialog(self.window)
        res = dialog.run()
        # dialog.close()
        if res == Gtk.ResponseType.ACCEPT:
            save_path = dialog.get_filename()
            if save_path[-5:].lower() != '.opml':
                save_path += '.opml'
            opml_out = feeds_list_to_opml(self.feedman.feeds)
            with open(save_path, 'w') as fd:
                fd.write(opml_out)
                fd.close()

    def show_about_dialog(self, *args):
        about_builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/gnome-feeds/aboutdialog.glade'
        )
        dialog = about_builder.get_object('aboutdialog')
        dialog.set_modal(True)
        dialog.set_transient_for(self.window)
        dialog.present()

    def on_destroy_window(self, *args):
        self.window.on_destroy()
        self.quit()

    def show_shortcuts_window(self, *args):
        shortcuts_win = Gtk.Builder.new_from_resource(
            '/org/gabmus/gnome-feeds/ui/shortcutsWindow.xml'
        ).get_object('shortcuts-gnome-feeds')
        shortcuts_win.props.section_name = 'shortcuts'
        shortcuts_win.set_transient_for(self.window)
        shortcuts_win.set_attached_to(self.window)
        shortcuts_win.set_modal(True)
        shortcuts_win.present()
        shortcuts_win.show_all()

    def show_settings_window(self, *args):
        settings_win = GFeedsSettingsWindow()
        settings_win.set_transient_for(self.window)
        settings_win.set_attached_to(self.window)
        settings_win.set_modal(True)
        settings_win.present()

    def do_activate(self):
        self.add_window(self.window)
        stylecontext = Gtk.StyleContext()
        provider = Gtk.CssProvider()
        provider.load_from_data('''
            .notheaderbar {
                border-radius: 0px;
            }
        '''.encode())
        stylecontext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.window.present()
        self.window.show_all()
        self.feedman.refresh()
        if self.args:
            if self.args.argurl:
                if self.args.argurl[:8] == 'file:///':
                    abspath = self.args.argurl[7:]
                    if isfile(abspath):
                        dialog = GFeedsConfirmAddDialog(self.window, abspath)
                        res = dialog.run()
                        dialog.close()
                        if res == Gtk.ResponseType.YES:
                            self.add_opml_feeds(abspath)

    def do_command_line(self, args):
        """
        GTK.Application command line handler
        called if Gio.ApplicationFlags.HANDLES_COMMAND_LINE is set.
        must call the self.do_activate() to get the application up and running.
        """
        Gtk.Application.do_command_line(self, args)  # call the default commandline handler
        # make a command line parser
        parser = argparse.ArgumentParser()
        parser.add_argument(
            'argurl',
            metavar = _('url'),
            type = str,
            nargs = '?',
            help = _('opml file local url or rss remote url to import')
        )
        #parser.add_argument('-c', '--cli', dest='wallpaper_path', nargs='+', action='append', help=_('set wallpapers from command line'))
        #parser.add_argument('-r', '--random', dest='set_random', action='store_true', help=_('set wallpapers randomly'))
        # parse the command line stored in args, but skip the first element (the filename)
        self.args = parser.parse_args(args.get_arguments()[1:])
        # call the main program do_activate() to start up the app
        self.do_activate()
        return 0


def main():

    application = GFeedsApplication()

    try:
        ret = application.run(sys.argv)
    except SystemExit as e:
        ret = e.code

    sys.exit(ret)


if __name__ == '__main__':
    main()
