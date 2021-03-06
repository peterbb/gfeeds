import threading
from os import remove
from gettext import gettext as _
from gi.repository import Gtk
from gfeeds.confManager import ConfManager
from gfeeds.download_manager import download_raw
from gfeeds.feeds_manager import FeedsManager


class RowPopover(Gtk.Popover):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        self.feedman = FeedsManager()
        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/gfeeds/ui/article_right_click_popover_content.glade'
        )
        self.container_box = self.builder.get_object('container_box')
        # self.set_size_request(270, 150)
        self.parent = parent

        # self.title_label = self.builder.get_object('title_label')
        # self.title_label.set_text(self.parent.feeditem.title)

        self.read_unread_btn = self.builder.get_object('read_unread_btn')
        self.read_unread_btn.connect('clicked', self.on_read_unread_clicked)
        self.read_unread_img = self.builder.get_object('read_unread_img')
        self.read_unread_label = self.builder.get_object('read_unread_label')

        self.save_btn = self.builder.get_object('save_btn')
        self.save_btn.set_active(
            self.parent.feeditem.link in self.confman.conf['saved_items']
        )
        self.save_btn_handler_id = self.save_btn.connect(
            'toggled', self.on_save_toggled
        )

        self.set_modal(True)
        self.set_relative_to(self.parent)
        self.add(self.container_box)
        if self.parent.feeditem.read:
            self.read_unread_img.set_from_icon_name(
                'eye-not-looking-symbolic',
                Gtk.IconSize.BUTTON
            )
            self.read_unread_label.set_text(_(
                'Mark as unread'
            ))
        else:
            self.read_unread_img.set_from_icon_name(
                'eye-open-negative-filled-symbolic',
                Gtk.IconSize.BUTTON
            )
            self.read_unread_label.set_text(_(
                'Mark as read'
            ))

    def set_read(self, read):
        parent_stack = self.parent.get_parent().get_parent(
        ).get_parent().get_parent()
        other_list = (
            parent_stack.listbox
            if self.parent.get_parent() == parent_stack.saved_items_listbox
            else parent_stack.saved_items_listbox
        )
        other_row = None
        for row in other_list.get_children():
            if row.feeditem.link == self.parent.feeditem.link:
                other_row = row
                break
        rows = [self.parent, ]
        if other_row:
            rows.append(other_row)
        if not read:
            for r in rows:
                r.set_read(False)
                r.popover.read_unread_img.set_from_icon_name(
                    'eye-open-negative-filled-symbolic',
                    Gtk.IconSize.BUTTON
                )
                r.popover.read_unread_label.set_text(_(
                    'Mark as read'
                ))
        else:
            for r in rows:
                r.set_read(True)
                r.popover.read_unread_img.set_from_icon_name(
                    'eye-not-looking-symbolic',
                    Gtk.IconSize.BUTTON
                )
                r.popover.read_unread_label.set_text(_(
                    'Mark as unread'
                ))
        parent_stack.listbox.invalidate_filter()
        other_list.invalidate_filter()

    def on_read_unread_clicked(self, btn):
        self.popdown()
        self.set_read(not self.parent.feeditem.read)

    def on_save_toggled(self, togglebtn):
        self.popdown()
        togglebtn.set_sensitive(False)
        if togglebtn.get_active():
            fi_dict = self.parent.feeditem.to_dict()
            t = threading.Thread(
                group=None,
                target=download_raw,
                name=None,
                args=(
                    fi_dict['link'],
                    self.confman.saved_cache_path + '/' + fi_dict['linkhash']
                )
            )
            t.start()
            self.confman.conf[
                'saved_items'
            ][self.parent.feeditem.link] = fi_dict
        else:
            todel_fi_dict = self.confman.conf['saved_items'].pop(
                self.parent.feeditem.link
            )
            remove(
                self.confman.saved_cache_path + '/' + todel_fi_dict['linkhash']
            )
            # parent.is_saved means "the row that spawned the popover is from
            # the *Saved* section"
            if self.parent.is_saved:
                parent_stack = self.parent.get_parent().get_parent(
                ).get_parent().get_parent()
                parent_stack.on_saved_item_deleted(todel_fi_dict['link'])
        self.confman.save_conf()
        self.feedman.populate_saved_feeds_items()
        togglebtn.set_sensitive(True)
