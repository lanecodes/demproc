"""
DEMproc
~~~~~~~
"""
__version__ = "0.0.1"
from demproc.makelayers import (make_hydro_correct_dem, make_flow_direction_map, 
    make_slope_map, make_continuous_aspect_map, make_binary_aspect_map,
    derive_all)
from demproc.trim import geotiff_to_array, trim_geotiff_edge