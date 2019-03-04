"""
dummy.py
~~~~~~~~

Functions used to create small GeoTiff files based on numpy arrays. Useful for
testing purposes, both within demproc and beyond.
"""
import numpy as np
from osgeo import gdal, osr
from pyproj import Proj

def create_dummy_geotiff_from_array(tgt_fname, array):
    """Use a numpy array to create a dummy geotiff file for testing.
    See https://gis.stackexchange.com/questions/58517/python-gdal-save-array-\
        as-raster-with-projection-from-other-file.
    """
    PIXEL_SIZE = 10
    X_PIXELS = array.shape[1]
    Y_PIXELS = array.shape[0]

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(27700) # british national grid
    
    projection = Proj(init='epsg:27700')
    x_cc, y_cc = projection(-0.1269505, 51.5081364) # Charing cross in BNG

    driver = gdal.GetDriverByName('GTiff')    
    ds = driver.Create(tgt_fname, X_PIXELS, Y_PIXELS, 1, gdal.GDT_Int32)
    # Charing cross is top left hand corner of grid
    ds.SetGeoTransform((x_cc, PIXEL_SIZE, 0, y_cc, 0, -PIXEL_SIZE))  
    ds.SetProjection(srs.ExportToWkt())        
    ds.GetRasterBand(1).WriteArray(array)
    ds.FlushCache()  # Write to disk.

def make_dummy_hydro_incorrect_dem(fname):
    # note the 1 in the second row is a pit which should be removed
    arr = np.array([
        [2, 2, 2, 3, 2], 
        [2, 1, 2, 3, 4], 
        [2, 2, 2, 3, 2], 
        [3, 3, 4, 4, 3],
        [2, 2, 3, 3, 2]])
    
    create_dummy_geotiff_from_array(fname, arr)