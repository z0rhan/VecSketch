# Helper library for COMP.CS.400 Principles of programming languages
# programming project 2026
# © 2026 Matti Rintala and Jyke Savia

# Some global configuration constants and variables
# You can tweak these if you want (but don't have to)
class Conf:
    precision = 0.0001 # To what precision should we simplify Shapely shapes
    W = 500            # Width of the drawing window
    marginX = 10       # Horizontal margin between the window and the drawn shapes
    H = W              # Height of the drawing window
    marginY = 10       # Vertical margin between the window and the drawn shapes
    POINTSIZE = 3      # Size of drawn points
    LINEWIDTH = 2      # Width of drawn lines
    DEFCOLOR='#4e008e' # Default drawing color ("Tuni violet")
    # Don't touch the variables before they are for library's internal use
    scale = None
    xOffset = None
    yOffset = None
    root = None
    canvas = None
    button = None
    wait_var = None

import shapely as sh
import tkinter as tk
import time
import sys


#
# Operations to be used in the interpreter:
#
def create_point( x, y ):
    """Creates a point shape in the given (x,y) coordinates"""
    return prec(sh.Point(x, y))


def create_linestring( coordlist ):
    """Creates a linestring shape that connects the given (x,y) coordinates"""
    return prec(sh.LineString(coordlist))


def create_polygon( coordlist ):
    """Creates a polygon shape whose corners are the given (x,y) coordinates"""
    return prec(sh.Polygon(coordlist))


def shape_xcoord( shape ):
    """Returns the x-coordinate of the centroid (the 'geometric center') of the shape"""
    centx,centy = shape.centroid.coords[0]
    return centx


def shape_ycoord( shape ):
    """Returns the y-coordinate of the centroid (the 'geometric center') of the shape"""
    centx,centy = shape.centroid.coords[0]
    return centy


def shape_bounds (shape ):
    """Returns a tuple (xmin, ymin, xmax, ymax) defining the 'bounding box' of the shape"""
    if shape.is_empty:
        return (0,0,0,0)
    else:
        return shape.bounds


def shape_union( shape1, shape2 ):
    """Returns the union of two shapes"""
    return prec(shape1.union(shape2))


def shape_intersection( shape1, shape2 ):
    """Returns the intersection of two shapes"""
    return prec(shape1.intersection(shape2))


def shape_difference( shape1, shape2 ):
    """Returns the difference of two shapes (shape2 is 'carved out' from shape1)"""
    return prec(shape1.difference(shape2))


def shape_move( shape, deltax, deltay ):
    """Returns the shape moved deltax to the right and deltay up (left/down for negative values)"""
    return prec(sh.affinity.translate(shape, deltax, deltay))


def shape_scale( shape, scale ):
    """Returns the shape scaled by the given factor (scaling is done with respect to origin (0,0))"""
    return prec(sh.affinity.scale(shape, xfact=scale, yfact=scale, origin=(0,0)))


def shape_rotate( shape, degrees ):
    """Returns the shape rotated counterclockwise by the given angle in degrees
       (rotating is done with respect to origin (0,0))"""
    return prec(sh.affinity.rotate(shape, degrees, origin=(0,0)))


def shape_equals( shape1, shape2 ):
    """Returns whether two shapes are equal to each other"""
    return shape1.equals(shape2)


def shape_covered_by( shape1, shape2 ):
    """Returns whether shape1 is covered by shape2"""
    return shape1.covered_by(shape2)


def shape_downgrade( shape ):
    """Returns a 'downgraded' version of the shape (its 'boundary'),
       where polygons become their outline, linestrings become their points,
       and points remain points"""
    shtype = shape.geom_type
    if shtype == 'Point':
        return shape
    elif shtype == 'MultiPoint':
        return shape
    elif shtype == 'LineString':
        return prec(sh.MultiPoint(shape.coords))
    elif shtype == 'MultiLineString':
        return prec(sh.MultiPoint(sum([ list(s.coords) for s in shape.geoms ],[])))
    elif shtype == 'Polygon' or shtype == 'MultiPolygon':
        return prec(shape.boundary)
    elif hasattr( shape, 'geoms' ):  # multiple shapely items
        return prec(sh.GeometryCollection([ shape_downgrade(s) for s in shape.geoms ]))
    else:
        print('Unknown shape type',shtype,'for shape_downgrade(), doing nothing.')
        return shape # Do nothing, if we don't know what this is


def shape_polygonize( shape ):
    """Returns a 'polygonized' version of the shape, where polygons remain polygons,
       linestrings become polygons whose perimeter is the linestring,
       and a collection of points becomes a polygon that contains all the points"""
    shtype = shape.geom_type
    if shtype == 'Point':
        return shape
    elif shtype == 'MultiPoint':
        return prec(shape.convex_hull)
    elif shtype == 'LineString':
        return prec(sh.MultiPolygon(sh.polygonize([shape])))
    elif shtype == 'MultiLineString':
        # return sh.MultiPolygon(sh.polygonize([sh.line_merge(shape)]))
        # return sh.MultiPolygon(sh.polygonize(list(shape.geoms)))
        result, cuts, dangles, invalids = sh.polygonize_full(shape.geoms)
        return prec(sh.unary_union([result, cuts, dangles, invalids]))
    elif shtype == 'Polygon' or shtype == 'MultiPolygon':
        return shape
    # elif hasattr( shape, 'geoms' ):  # multiple shapely items
    #     return [ shape_polygonize(s) for s in shape.geoms ]
    else:
        print('Unknown shape type',shtype,'for shape_polygonize(), doing nothing.')
        return shape # Do nothing, if we don't know what this is


def shape_tostring( shape ):
    """Returns a printable string representing the shape"""
    if hasattr( shape, 'geoms' ):
        return str(list(shape.geoms))
    else:
        return str(shape)


# Drawing operations
def window_open( width=Conf.W, height=Conf.H ):
    """Opens a window, either with default or given width and height"""
    Conf.W = width
    Conf.H = height
    root = tk.Tk()
    Conf.root = root
    root.protocol("WM_DELETE_WINDOW", lambda: Conf.wait_var.set(2))
    canvas = tk.Canvas(root,bg="white", width=Conf.W+2*Conf.marginX,
                       height=2*Conf.marginY+Conf.H)
    canvas.pack()
    Conf.canvas = canvas
    Conf.wait_var = tk.IntVar()
    button = tk.Button(root,text='Continue',command=lambda: Conf.wait_var.set(1))
    button.pack()
    button.config(state=tk.DISABLED)
    Conf.button = button
    Conf.scale = None
    Conf.xOffset = None
    Conf.yOffset = None


def window_clear( ):
    """Clears the window, resets scaling and offset"""
    Conf.canvas.delete( *(Conf.canvas.find_all()) )
    Conf.scale = None
    Conf.xOffset = None
    Conf.yOffset = None


def window_draw( item, red=None, green=None, blue=None ):
    """Draws the given shape either with the given color or the default color.
       NOTE: The FIRST window_draw() on the window determines is scale and offset so
       that the drawn shape just fits the window. The same happens on the
       first window_draw() after the window_clear()"""
    if red is None or green is None or blue is None:
        color = Conf.DEFCOLOR
    else:
        red = max(0,min(255,int(red)))
        green = max(0,min(255,int(green)))
        blue = max(0,min(255,int(blue)))
        color = '#'+('%02x' % red)+('%02x' % green)+('%02x' % blue)
        # color = '#'+hex(red)[2:]+hex(green)[2:]+hex(blue)[2:]
    assert isinstance(item, sh.Geometry), f"Can't draw type {type(item)}"

    # -- draw shapely
    if Conf.scale == None:
        assert Conf.xOffset == None and Conf.yOffset == None, f"Conf offsets not reset"
        minx,miny,maxx,maxy = item.bounds

        if maxx != minx:
            if maxy != miny:
                xScale = Conf.W / (maxx - minx)
                yScale = Conf.H / (maxy - miny)
                Conf.scale = min(xScale, yScale)
            else:
                Conf.scale = Conf.W / (maxx - minx)
        else:
            if maxy != miny:
                Conf.scale = Conf.W / (maxy - miny)
            else:
                Conf.scale = 1

        Conf.xOffset = minx
        Conf.yOffset = miny

    if hasattr( item, 'geoms' ):  # multiple shapely items
        for s in item.geoms:
            dispatch[ s.geom_type ]( s, color )
    else:
        dispatch[ item.geom_type ]( item, color )


def window_wait( secs ):
    """Waits the given number of seconds"""
    Conf.root.update()
    time.sleep(secs)
    Conf.root.update()
    if Conf.wait_var.get() == 2:
        Conf.root.destroy()
        sys.exit()


def window_pause( ):
    """Pauses until the user presses the continue button"""
    Conf.wait_var.set(0)
    Conf.button.config(state=tk.NORMAL)
    Conf.root.wait_variable(Conf.wait_var)
    Conf.button.config(state=tk.DISABLED)
    Conf.root.update()
    if Conf.wait_var.get() == 2:
        Conf.root.destroy()
        sys.exit()


def window_close( ):
    """Waits for the user to press the "Close" button, then closes the drawing window"""
    Conf.wait_var.set(0)
    Conf.button.config(text="Close")
    Conf.button.config(state=tk.NORMAL)
    Conf.root.wait_variable(Conf.wait_var)
    # Quit
    Conf.root.destroy()
    if Conf.wait_var.get() == 2:
        sys.exit()
    Conf.root = None
    Conf.canvas = None
    Conf.button = None
    Conf.wait_var = None


#
# Internal helper functions, do not use these
#
def prec(shape):
    """Internal function to simplify resulting Shapely shapes"""
    return shape.simplify(Conf.precision)


def scale_coords( coords ):
    """Internal function for scaling shape coordinates to window coordinates"""
    ret = list()
    for x,y in coords:
        ret.append( (Conf.scale*(x-Conf.xOffset)+Conf.marginX,
                     Conf.marginY+Conf.H - Conf.scale*(y-Conf.yOffset)) )
    return ret


def draw_point( s, color ):
    """Internal function for drawing a point with the given color"""
    if not s.is_empty:
        sx,sy = scale_coords([(s.x,s.y)])[0]
        Conf.canvas.create_oval( (sx-Conf.POINTSIZE, sy-Conf.POINTSIZE, sx+Conf.POINTSIZE, sy+Conf.POINTSIZE), fill=color, outline=color )


def draw_linestring( s, color ):
    """Internal function for drawing a linestring with the given color"""
    if not s.is_empty:
        coords = s.coords
        Conf.canvas.create_line( *scale_coords(coords), fill=color, width=Conf.LINEWIDTH )


def draw_linearring( s, color ):
    """Internal function for drawing a linear ring with the given color"""
    if not s.is_empty:
        coords = s.coords
        Conf.canvas.create_linestring( *scale_coords(coords), fill=color, width=Conf.LINEWIDTH )


def draw_polygon( s, color ):
    """Internal function for drawing a polygon with the given color"""
    if not s.is_empty:
        coords = s.exterior.coords
        Conf.canvas.create_polygon( *scale_coords(coords), fill=color )
        # Draw interior holes with white (transparent holes would be difficult...)
        for hole in s.interiors:
            coords = hole.coords
            if len(coords) > 0:
                Conf.canvas.create_polygon( *scale_coords(coords), fill="white" )


def draw_multipoint( s, color ):
    """Internal function for drawing a multipoint with the given color"""
    for p in s.geoms:
        draw_point( p, color )


def draw_multilinestring( s, color ):
    """Internal function for drawing a multilinestring with the given color"""
    for p in s.geoms:
        draw_linestring( p, color )


def draw_multipolygon( s, color ):
    """Internal function for drawing a multipolygon with the given color"""
    for p in s.geoms:
        draw_polygon( p, color )

# A dispatch table for drawing an arbitrary shape
dispatch = {
    'Point' : draw_point,
    'LineString' : draw_linestring,
    'LinearRing' : draw_linearring,
    'Polygon' : draw_polygon,
    'MultiPoint' : draw_multipoint,
    'MultiLineString' : draw_multilinestring,
    'MultiPolygon' : draw_multipolygon,
}
