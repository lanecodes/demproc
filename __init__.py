"""
DEMproc
~~~~~~~
"""
from demproc import (make_hydro_correct_dem, make_flow_direction_map, 
    make_slope_map, make_continuous_aspect_map, make_binary_aspect_map,
    derive_all)
from trim import trim_geotiff_edge