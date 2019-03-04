"""
test_demproc.py

Tests for demproc.py
"""
import unittest
import os
import tempfile, shutil

import numpy as np
from osgeo import gdal, osr

from demproc.makelayers import make_hydro_correct_dem, read_geotiff_as_array
from demproc.trim import trim_geotiff_edge
from demproc.dummy import make_dummy_hydro_incorrect_dem

class DemProcTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_make_hydro_correct_dem(self):
        incorrect_dem = os.path.join(self.test_dir, "hydro_incorrect.tif")
        make_dummy_hydro_incorrect_dem(incorrect_dem)
        
        correct_dem = os.path.join(self.test_dir, "hydro_correct.tif")
        make_hydro_correct_dem(incorrect_dem, correct_dem)

        # note the pit in second row has been removed
        expected_arr = np.array([
            [2, 2, 2, 3, 2], 
            [2, 2, 2, 3, 4], 
            [2, 2, 2, 3, 2], 
            [3, 3, 4, 4, 3],
            [2, 2, 3, 3, 2]])

        self.assertTrue(np.array_equal(read_geotiff_as_array(correct_dem), 
            expected_arr))


class TrimTestCase(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_trim_geotiff_edge(self):
        """Trim one cell from each edge of the test grid."""
        incorrect_dem = os.path.join(self.test_dir, "hydro_incorrect.tif")
        trimmed_dem = os.path.join(self.test_dir, "trimmed_dem.tif")
        make_dummy_hydro_incorrect_dem(incorrect_dem)
        trim_geotiff_edge(incorrect_dem, trimmed_dem)
        
        # outer edge removed
        expected_arr = np.array([            
            [1, 2, 3], 
            [2, 2, 3], 
            [3, 4, 4]])

        self.assertTrue(np.array_equal(
            read_geotiff_as_array(trimmed_dem), expected_arr))

    def test_trim_geotiff_edge_two_cells_each_side(self):
        """Should be able to trim two grid cells from each side of grid."""
        incorrect_dem = os.path.join(self.test_dir, "hydro_incorrect.tif")
        trimmed_dem = os.path.join(self.test_dir, "trimmed_dem.tif")

        make_dummy_hydro_incorrect_dem(incorrect_dem)
        trim_geotiff_edge(incorrect_dem, trimmed_dem, n=2)
        
        # outer edge removed
        expected_arr = np.array([[2]])

        self.assertTrue(np.array_equal(
            read_geotiff_as_array(trimmed_dem), expected_arr))
