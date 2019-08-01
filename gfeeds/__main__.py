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
from gi.repository import Gtk, Gio
from .confManager import ConfManager
from .app_window import GFeedsAppWindow
from .settings_window import GFeedsSettingsWindow
from .opml_manager import opml_to_rss_list, feeds_list_to_opml
from .opml_file_chooser import (
    GFeedsOpmlFileChooserDialog,
    GFeedsOpmlSavePathChooserDialog
)
from .manage_feeds_window import GFeedsManageFeedsWindow
import threading

def test():
    from .download_manager import download
    from .rss_parser import Feed
    confman = ConfManager()
    feeds = []
    for f in confman.conf['feeds']:
        feeds.append(Feed(download(f)))

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
        self.window = GFeedsAppWindow()
        self.window.connect('destroy', self.on_destroy_window)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        actions = [
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

    def manage_feeds(self, *args):
        mf_win = GFeedsManageFeedsWindow(
            self.window,
            self.window.feeds
        )
        mf_win.present()

    def import_opml(self, *args):
        dialog = GFeedsOpmlFileChooserDialog(self.window)
        res = dialog.run()
        # dialog.close()
        if res == Gtk.ResponseType.ACCEPT:
            n_feeds_urls_l = opml_to_rss_list(dialog.get_filename())
            self.window.headerbar.refresh_btn.set_spinning(True)
            self.window.headerbar.add_popover.confirm_btn.set_sensitive(False)

            for url in n_feeds_urls_l:
                t = threading.Thread(
                    group = None,
                    target = self.window.add_new_feed_async_worker,
                    name = None,
                    args = (url,)
                )
                t.start()
                while t.is_alive():
                    while Gtk.events_pending():
                        Gtk.main_iteration()

            self.window.headerbar.refresh_btn.set_spinning(False)
            self.window.headerbar.add_popover.confirm_btn.set_sensitive(True)

    def export_opml(self, *args):
        dialog = GFeedsOpmlSavePathChooserDialog(self.window)
        res = dialog.run()
        # dialog.close()
        if res == Gtk.ResponseType.ACCEPT:
            save_path = dialog.get_filename()
            if save_path[-5:].lower() != '.opml':
                save_path += '.opml'
            opml_out = feeds_list_to_opml(self.window.feeds)
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
        if self.args:
            pass
        self.window.present()
        self.window.show_all()
        self.window.refresh_feeds()

    def do_command_line(self, args):
        """
        GTK.Application command line handler
        called if Gio.ApplicationFlags.HANDLES_COMMAND_LINE is set.
        must call the self.do_activate() to get the application up and running.
        """
        Gtk.Application.do_command_line(self, args)  # call the default commandline handler
        # make a command line parser
        parser = argparse.ArgumentParser()
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
