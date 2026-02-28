from pathlib import Path

import prismatui as pr

import docprisma as dpr


# //////////////////////////////////////////////////////////////////////////////
class TUIDocPrisma(pr.Terminal):
    NLINES_FAST_SCROLL = 10
    H_GUIDES = 1

    KEY_SCROLL_TOP    = ord('-')
    KEY_SCROLL_BOTTOM = ord('+')

    # --------------------------------------------------------------------------
    def __init__(self, *paths_doc: Path):
        super().__init__()
        self._docs = [dpr.DocData.load_doc(p) for p in paths_doc]
        self._ldoc = self._safe_load_doc(0) # pointer to currently loaded doc (body_left)
        self._rdoc = self._safe_load_doc(1) # pointer to currently loaded doc (body_right)


    # --------------------------------------------------------------------------
    def on_start(self):
        self.pair_help = pr.init_pair(1, pr.COLOR_BLACK, pr.COLOR_CYAN)

        self.body   = self.root.create_child(-self.H_GUIDES, 1.0,  0, 0)
        self.footer = self.root.create_child( self.H_GUIDES, 1.0, -1, 0)

        self.body_left  = self.body.create_child(1.0, 0.5, 0, 0.0)
        self.body_right = self.body.create_child(1.0, 0.5, 0, 0.5)

    # --------------------------------------------------------------------------
    def on_update(self):
        self._handle_key_press()
        self._draw_body()
        self._draw_borders()
        self._draw_footer()


    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.key == pr.KEY_Q_LOWER or self.key == pr.KEY_Q_UPPER


    # --------------------------------------------------------------------------
    def _handle_key_press(self):
        match self.key:
            case pr.KEY_UP:      self._scroll_up(1)
            case pr.KEY_DOWN:    self._scroll_down(1)
            case pr.KEY_PPAGE:   self._scroll_up(self.NLINES_FAST_SCROLL)
            case pr.KEY_NPAGE:   self._scroll_down(self.NLINES_FAST_SCROLL)
            case self.KEY_SCROLL_TOP:    self._scroll_up(float("inf"))
            case self.KEY_SCROLL_BOTTOM: self._scroll_down(float("inf"))
            case pr.KEY_LEFT:  self._ldoc.prev_node()
            case pr.KEY_RIGHT: self._ldoc.next_node()



    # --------------------------------------------------------------------------
    def _draw_body(self):
        hdisplay = self.body_left.h - 2
        self.NLINES_FAST_SCROLL = hdisplay // 2 # dinamically adjust fast scroll based on terminal height

        self._ldoc.section_width = self.body_left.w - 2

        chars, attrs = self._ldoc.get_chars_attrs(hdisplay)
        self.body_left.draw_matrix(1, 1, chars, attrs)


    # --------------------------------------------------------------------------
    def _draw_footer(self):
        self.footer.draw_text(0, 2, "q: quit", self.pair_help)


    # --------------------------------------------------------------------------
    def _draw_borders(self):
        self.body_left.draw_border()
        self.body_left.draw_text(0, 2, f" {self._ldoc.name}:{self._ldoc.get_nodes_path()} ", pr.A_BOLD)

        self.body_right.draw_border()
        self.body_right.draw_text(0, 2, f" {self._rdoc.name}:{self._rdoc.get_nodes_path()} ", pr.A_BOLD)

        self.footer.draw_border(bl = '│', bs = ' ', br = '│')


    # --------------------------------------------------------------------------
    def _scroll_up(self, nlines: int):
        self._ldoc.idx = max(0, self._ldoc.idx - nlines)


    # --------------------------------------------------------------------------
    def _scroll_down(self, nlines: int):
        self._ldoc.idx = min(self._ldoc.idx + nlines, len(self._ldoc.data) - 1)

    # ------------------------------------------------------------------------------
    def _safe_load_doc(self, idx: int) -> dpr.DocData:
        if not (0 <= idx < len(self._docs)):
            return dpr.DocData()
        return self._docs[idx]


# //////////////////////////////////////////////////////////////////////////////
