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
        self._doc_focused = self._ldoc
        self._synced_mode = False

        if not isinstance(self._ldoc, dpr.DocJson): return
        if not isinstance(self._rdoc, dpr.DocJson): return
        self._ldoc.link_comparison_partner(self._rdoc)


    # --------------------------------------------------------------------------
    def on_start(self):
        self.pair_help = pr.init_pair(1, pr.COLOR_BLACK, pr.COLOR_CYAN)
        self.pair_highlight_section = pr.init_pair(2, pr.COLOR_GREEN, pr.COLOR_BLACK)

        dpr.COLOR_PAIR_UNMATCHED = pr.init_pair(3, pr.COLOR_RED    , pr.COLOR_BLACK, )
        dpr.COLOR_PAIR_DIFFERENT = pr.init_pair(4, pr.COLOR_YELLOW , pr.COLOR_BLACK, )
        dpr.COLOR_PAIR_EQUAL     = pr.init_pair(5, pr.COLOR_GREEN  , pr.COLOR_BLACK, )


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
    def on_resize(self):
        self._ldoc.update_idx_row_top(self.body_left.h - 2)
        self._rdoc.update_idx_row_top(self.body_left.h - 2)


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
            case pr.KEY_S_LOWER: self._synced_mode = not self._synced_mode
            case pr.KEY_S_UPPER: self._synced_mode = not self._synced_mode
            case pr.KEY_F_LOWER: self._switch_focus()
            case pr.KEY_F_UPPER: self._switch_focus()
            case pr.KEY_LEFT:  self._prev_node()
            case pr.KEY_RIGHT: self._next_node()


    # --------------------------------------------------------------------------
    def _draw_body(self):
        hdisplay = self.body_left.h - 2
        self.NLINES_FAST_SCROLL = hdisplay // 2 # dinamically adjust fast scroll based on terminal height

        self._ldoc.section_width = self.body_left.w - 2
        self._rdoc.section_width = self.body_right.w - 2

        chars, attrs = self._ldoc.get_chars_attrs(hdisplay)
        self.body_left.draw_matrix(1, 1, chars, attrs)

        chars, attrs = self._rdoc.get_chars_attrs(hdisplay)
        self.body_right.draw_matrix(1, 1, chars, attrs)


    # --------------------------------------------------------------------------
    def _draw_footer(self):
        self.footer.draw_text(0, 2, "q: quit", self.pair_help)


    # --------------------------------------------------------------------------
    def _draw_borders(self):
        attr_lborder = pr.A_BOLD | self.pair_highlight_section \
            if (self._synced_mode or self._ldoc is self._doc_focused) else pr.A_NORMAL

        attr_rborder = pr.A_BOLD | self.pair_highlight_section \
            if (self._synced_mode or self._rdoc is self._doc_focused) else pr.A_NORMAL

        self.body_left.draw_border(attr = attr_lborder)
        self.body_left.draw_text(0, 2, f" {self._ldoc.name}:{self._ldoc.get_nodes_path()} ", pr.A_BOLD)

        self.body_right.draw_border(attr = attr_rborder)
        self.body_right.draw_text(0, 2, f" {self._rdoc.name}:{self._rdoc.get_nodes_path()} ", pr.A_BOLD)

        self.footer.draw_border(bl = '│', bs = ' ', br = '│')


    # --------------------------------------------------------------------------
    def _scroll_up(self, nlines: int):
        for d in self._iter_active_docs(): d.scroll_up(nlines, self.body.h - 2)


    # --------------------------------------------------------------------------
    def _scroll_down(self, nlines: int):
        for d in self._iter_active_docs(): d.scroll_down(nlines, self.body.h - 2)


    # ------------------------------------------------------------------------------
    def _switch_focus(self):
        self._doc_focused = self._rdoc if self._doc_focused is self._ldoc else self._ldoc


    # ------------------------------------------------------------------------------
    def _prev_node(self):
        for d in self._iter_active_docs(): d.prev_node()
        for d in self._iter_active_docs(): d.update_idx_row_top(self.body.h - 2)
        self._ldoc.update_comparison_states()
        self._rdoc.update_comparison_states()


    # ------------------------------------------------------------------------------
    def _next_node(self):
        for d in self._iter_active_docs(): d.next_node()
        for d in self._iter_active_docs(): d.reset_idx_row_top()
        self._ldoc.update_comparison_states()
        self._rdoc.update_comparison_states()


    # ------------------------------------------------------------------------------
    def _safe_load_doc(self, idx: int) -> dpr.DocData:
        if not (0 <= idx < len(self._docs)):
            return dpr.DocData()
        return self._docs[idx]


    # ------------------------------------------------------------------------------
    def _iter_active_docs(self):
        if self._synced_mode:
            yield self._ldoc
            yield self._rdoc
        else:
            yield self._doc_focused


# //////////////////////////////////////////////////////////////////////////////
