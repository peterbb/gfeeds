from gi.repository import Gtk, Handy

class GFeedsLeaflet(Handy.Leaflet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # base leaflet behavior options
        self.set_mode_transition_type(Handy.LeafletModeTransitionType.SLIDE)
        self.set_child_transition_type(Handy.LeafletModeTransitionType.SLIDE)
        self.set_interpolate_size(True)
        self.set_homogeneous(Handy.Fold.FOLDED, Gtk.Orientation.HORIZONTAL, False)
        self.set_homogeneous(Handy.Fold.UNFOLDED, Gtk.Orientation.HORIZONTAL, True)

    @property
    def folded(self):
        return self.get_fold() == Handy.Fold.FOLDED
