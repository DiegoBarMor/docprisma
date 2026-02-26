import prismatui as pr

import docprisma as dpr

# //////////////////////////////////////////////////////////////////////////////
class TUIDocPrisma(pr.Terminal):
    NLINES_FAST_SCROLL = 10
    H_GUIDES = 1

    KEY_SCROLL_TOP    = ord('-')
    KEY_SCROLL_BOTTOM = ord('+')

    # --------------------------------------------------------------------------
    def __init__(self, doc: dpr.DocData):
        super().__init__()
        self._doc = doc


    # --------------------------------------------------------------------------
    def on_start(self):
        self.pair_help = pr.init_pair(1, pr.COLOR_BLACK, pr.COLOR_CYAN)

        self.body   = self.root.create_child(-self.H_GUIDES, 1.0,  0, 0)
        self.footer = self.root.create_child( self.H_GUIDES, 1.0, -1, 0)


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


    # --------------------------------------------------------------------------
    def _draw_body(self):
        hdisplay = self.body.h - 2
        self.NLINES_FAST_SCROLL = hdisplay // 2 # dinamically adjust fast scroll based on terminal height

        lines = [line for line in self._doc.iter_lines()] # [WIP]
        self.body.draw_text(1,1,'\n'.join(lines))
        # chars = ['' for _ in lines] # [TODO]
        # attrs = [0  for _ in lines] # [TODO]

        # self.body.draw_matrix(1, 1, chars, attrs)


    # --------------------------------------------------------------------------
    def _draw_footer(self):
        self.footer.draw_text(0, 2, "q: quit", self.pair_help)


    # --------------------------------------------------------------------------
    def _draw_borders(self):
        self.body.draw_border()
        self.body.draw_text(0, 2, f" {self._doc.name} ", pr.A_BOLD)

        self.footer.draw_border(bl = '│', bs = ' ', br = '│')


    # --------------------------------------------------------------------------
    def _scroll_up(self, nlines: int):
        ... # [TODO]
        # current_line = max(0, current_line - nlines)


    # --------------------------------------------------------------------------
    def _scroll_down(self, nlines: int):
        ... # [TODO]
        # nlines_available = count_lines(self._filter_key) - 1 # account for NONE terminator line
        # current_line = min(current_line + nlines, nlines_available - 1)


# //////////////////////////////////////////////////////////////////////////////
