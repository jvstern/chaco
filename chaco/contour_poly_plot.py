""" Defines the ContourPolyPlot class.
"""

from __future__ import with_statement

# Major library imports
from numpy import array, linspace, meshgrid, transpose

# Enthought library imports
from traits.api import Bool, Dict

# Local relative imports
from base_contour_plot import BaseContourPlot
from contour.contour import Cntr


class ContourPolyPlot(BaseContourPlot):
    """ Contour image plot.  Takes a value data object whose elements are
    scalars, and renders them as a contour plot.
    """

    # TODO: Modify ImageData to explicitly support scalar value arrays
    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    # Are the cached contours valid? If False, new ones need to be computed.
    _poly_cache_valid = Bool(False)

    # Cached collection of traces.
    _cached_polys = Dict

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _render(self, gc):
        """ Actually draws the plot.

        Implements the Base2DPlot interface.
        """

        if not self._level_cache_valid:
            self._update_levels()
        if not self._poly_cache_valid:
            self._update_polys()
        if not self._colors_cache_valid:
            self._update_colors()

        with gc:
            gc.set_antialias(True)
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
            gc.set_line_width(0)
            gc.set_alpha(self.alpha)

            for i in range(len(self._levels)-1):
                gc.set_fill_color(self._colors[i])
                gc.set_stroke_color(self._colors[i])
                key = (self._levels[i], self._levels[i+1])
                for poly in self._cached_polys[key]:
                    if self.orientation == "h":
                        spoly = self.index_mapper.map_screen(poly)
                    else:
                        spoly = array(self.index_mapper.map_screen(poly))[:,::-1]
                    gc.lines(spoly)
                    gc.close_path()
                    gc.draw_path()

    def _update_polys(self):
        """ Updates the cache of contour polygons """
        # x and ydata are "fenceposts" so ignore the last value
        # XXX: this truncation is causing errors in Cntr() as of r13735
        xdata = self.index._xdata.get_data()
        ydata = self.index._ydata.get_data()
        xs = linspace(xdata[0], xdata[-1], len(xdata)-1)
        ys = linspace(ydata[0], ydata[-1], len(ydata)-1)
        xg, yg = meshgrid(xs, ys)
        if self.orientation == "h":
            c = Cntr(xg, yg, self.value.raw_value)
        else:
            c = Cntr(xg, yg, self.value.raw_value.T)
        self._cached_contours = {}
        for i in range(len(self._levels)-1):
            key = (self._levels[i], self._levels[i+1])
            self._cached_polys[key] = []
            polys = c.trace(*key)
            for poly in polys:
                self._cached_polys[key].append(transpose(poly))
        self._poly_cache_valid = True

    def _update_levels(self):
        """ Extends the parent method to also invalidate some other things """
        super(ContourPolyPlot, self)._update_levels()
        self._poly_cache_valid = False

    def _update_colors(self):
        BaseContourPlot._update_colors(self, numcolors = len(self._levels) - 1)


