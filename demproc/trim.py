"""
trim.py
~~~~~~~

Functions to trim the outermost cells from a raster in a GeoTiff file. 

See https://gis.stackexchange.com/questions/42584/how-to-call-gdal-translate-f\
    rom-python-code.
"""
import shutil
from osgeo import gdal

def geotiff_to_array(fname, band_no=1):
    """Read a GeoTiff file, return a numpy array containing grid values."""
    ds = gdal.Open(fname)
    
    # Get a numpy array representing the source dataset
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()

    return arr

def trim_geotiff_edge(src_name, tgt_name, n=1):
    """Make a new GeoTiff with n pixels trimmed from each edge.
    
    Args:
        src_name (str): Path to GeoTiff containing original raster grid.
        tgt_name (str): Path to GeoTiff which will contain the trimmed raster 
            grid.
        n (int): Number of pixels to trim from each edge of the raster grid.

    Returns:
        None
    """
    ds = gdal.Open(src_name)
    
    # Get a numpy array representing the source dataset
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()

    # remove buffer pixela from both edges in each dimension
    tgt_width = arr.shape[0] - n*2
    tgt_height = arr.shape[1] - n*2

    # See osgeo.gdal.TranslateOptions.
    # srcWin --- subwindow in pixels to extract: [left_x, top_y, width, height]
    ds = gdal.Translate("tmp.tif", ds, srcWin=[n, n, tgt_width, tgt_height])
    ds = None

    shutil.move("tmp.tif", tgt_name) # overrites src if same as target



