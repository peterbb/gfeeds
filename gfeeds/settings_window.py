from gettext import gettext as _
from gi.repository import Gtk, Gdk, Handy
from .confManager import ConfManager
from os.path import isfile, abspath, join
from os import remove, listdir

class PreferencesButtonRow(Handy.ActionRow):
    """
    A preferences row with a title and a button
    title: the title shown
    button_label: a label to show inside the button
    onclick: the function that will be called when the button is pressed
    button_style_class: the style class of the button. Common options: `suggested-action`, `destructive-action`
    signal: an optional signal to let ConfManager emit when the button is pressed
    """
    def __init__(self, title, button_label, onclick, button_style_class=None, signal=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.button_label = button_label
        self.confman = ConfManager()
        self.set_title(self.title)
        self.signal = signal
        self.onclick = onclick

        self.button = Gtk.Button()
        self.button.set_label(self.button_label)
        self.button.set_valign(Gtk.Align.CENTER)
        if button_style_class:
            self.button.get_style_context().add_class(button_style_class)
        self.button.connect('clicked', self.on_button_clicked)
        self.add_action(self.button)
        # You need to press the actual button
        # Avoids accidental presses
        # self.set_activatable_widget(self.button)

    def on_button_clicked(self, button):
        self.onclick(self.confman)
        if self.signal:
            self.confman.emit(self.signal, '')
        self.confman.save_conf()


class PreferencesToggleRow(Handy.ActionRow):
    """
    A preferences row with a title and a toggle
    title: the title shown
    conf_key: the key of the configuration dictionary/json in ConfManager
    signal: an optional signal to let ConfManager emit when the configuration is set
    """
    def __init__(self, title, conf_key, signal=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.confman = ConfManager()
        self.set_title(self.title)
        self.conf_key = conf_key
        self.signal = signal

        self.toggle = Gtk.Switch()
        self.toggle.set_valign(Gtk.Align.CENTER)
        if self.conf_key == 'selection_mode':
            self.toggle.set_active(self.confman.conf[self.conf_key] == 'double')
        else:
            self.toggle.set_active(self.confman.conf[self.conf_key])
        self.toggle.connect('state-set', self.on_toggle_state_set)
        self.add_action(self.toggle)
        self.set_activatable_widget(self.toggle)

    def on_toggle_state_set(self, toggle, state):
        self.confman.conf[self.conf_key] = state
        self.confman.save_conf()
        if self.signal:
            self.confman.emit(self.signal, '')


class GeneralPreferencesPage(Handy.PreferencesPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title(_('General'))
        self.set_icon_name('preferences-other-symbolic')

        
        self.general_preferences_group = Handy.PreferencesGroup()
        self.general_preferences_group.set_title(_('General Settings'))
        toggle_settings = [
            {
                'title': _('Show newer articles first'),
                'conf_key': 'new_first',
                'signal': 'gfeeds_new_first_changed'
            }
        ]
        for s in toggle_settings:
            row = PreferencesToggleRow(s['title'], s['conf_key'], s['signal'])
            self.general_preferences_group.add(row)
        self.add(self.general_preferences_group)

        self.cache_preferences_group = Handy.PreferencesGroup()
        self.cache_preferences_group.set_title(_('Cache')) 
        button_settings = [
            {
                'title': _('Clear all caches'),
                'button_label': _('Clear caches'),
                'onclick': self.clear_caches,
                'button_style_class': 'destructive-action',
                'signal': None # TODO: add signal
            }
        ]
        for s in button_settings:
            row = PreferencesButtonRow(
                s['title'],
                s['button_label'],
                s['onclick'],
                s['button_style_class'],
                s['signal']
            )
            self.cache_preferences_group.add(row)
        self.add(self.cache_preferences_group)

        self.show_all()

    def clear_caches(self, confman, *args):
        for p in [confman.cache_path, confman.thumbs_cache_path]:
            files = [
                abspath(join(p, f)) for f in listdir(p)
            ]
            for f in files:
                if isfile(f):
                    remove(f)


class ViewPreferencesPage(Handy.PreferencesPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title(_('View'))
        self.set_icon_name('applications-graphics-symbolic')

        
        self.view_preferences_group = Handy.PreferencesGroup()
        self.view_preferences_group.set_title(_('View Settings'))
        toggle_settings = [
            {
                'title': _('Use dark theme for reader mode'),
                'conf_key': 'dark_reader',
                'signal': None
            }
        ]
        for s in toggle_settings:
            row = PreferencesToggleRow(s['title'], s['conf_key'], s['signal'])
            self.view_preferences_group.add(row)
        self.add(self.view_preferences_group)

        self.show_all()


class GFeedsSettingsWindow(Handy.PreferencesWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pages = [
            GeneralPreferencesPage(),
            ViewPreferencesPage()
        ]
        for p in self.pages:
            self.add(p)
        # values copied from libhandy demo
        # https://source.puri.sm/Librem5/libhandy/blob/master/examples/hdy-demo-preferences-window.ui
        self.set_default_size(640, 700)