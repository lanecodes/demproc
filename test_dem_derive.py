"""
test_dem_derive.py

Tests for dem_derive.py
"""
import unittest

import numpy as np
from osgeo import gdal, osr
from pyproj import Proj

from dem_derive import make_hydro_correct_dem, read_geotiff_as_array

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

def make_dummy_hydro_incorrect_dem():
    # note the 1 in the seconcontinuous-aspect.tifd row is a pit
    arr = np.array([
        [2, 2, 2, 3, 2], 
        [2, 1, 2, 3, 4], 
        [2, 2, 2, 3, 2], 
        [3, 3, 4, 4, 3],
        [2, 2, 3, 3, 2]])
    
    create_dummy_geotiff_from_array("hydro_incorrect_dummy.tif", arr)


class DemDeriveTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_make_hydro_correct_dem(self):
        make_dummy_hydro_incorrect_dem()
        
        # note the pit in second row has been removed
        expected_arr = np.array([
            [2, 2, 2, 3, 2], 
            [2, 2, 2, 3, 4], 
            [2, 2, 2, 3, 2], 
            [3, 3, 4, 4, 3],
            [2, 2, 3, 3, 2]])
        
        make_hydro_correct_dem("hydro_incorrect_dummy.tif", 
            "hydro_correct_dummy.tif")

        self.assertTrue(np.array_equal(
            read_geotiff_as_array("hydro_correct_dummy.tif"), expected_arr))