"""
demproc.py
~~~~~~~~~~~~~

Given a GeoTiff file name as input, calculate the following outputs:

1. Hydrologically correct (i.e. pits removed) DEM, replacing old one
2. Flow direction map (1=E, 2=NE, 3=N,..., 8=SE)
3. Slope (units are percent incline)
4. Continuous aspect (0 deg=E, 90 deg=N, 180 deg=W, 270 deg=S)
5. Binary aspect (0 if northerly, 0 if southerly)

Horizontal units must be the same as vertical units in DEM for this to work

Dependencies:
- TauDEM, in particular binaries for pitremove and d8flowdir
- gdal, specifically gdaldem
"""
import os
from subprocess import run
from shutil import copyfile

from osgeo import gdal
import numpy as np

from trim import trim_geotiff_edge

def add_prefix_to_fname(original_fname, prefix):
    """Add a prefix to a given filename.

    Examples:
        >>> add_prefix_to_fname("data.tif", "London")
        "London_data.tif"
    """
    file_dir = os.path.dirname(original_fname)
    file_basename = os.path.basename(original_fname)
    new_basename = "_".join([prefix, file_basename])
    return os.path.join(file_dir, new_basename)

def read_geotiff_as_array(tgt_fname):
    """Read a geotiff file as a numpy array.
    See https://gis.stackexchange.com/questions/164853/reading-modifying-and-w\
        riting-a-geotiff-with-gdal-in-python.
    """
    ds = gdal.Open(tgt_fname)
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    del ds
    return arr

def make_hydro_correct_dem(dem_fname, hydro_correct_dem_fname=None):
    """Make a hydrologically correct DEM.

    Remove pits to create a hydrologically correct Digital Elevation Model.
    Write a new GeoTiff file to disk containing the corrected DEM.

    Args:
        dem_fname (str): Path to the GeoTiff file containing the source
            Digital Elevation Model.
        hydro_correct_dem_fname (str, optional): Path for the GeoTiff file 
            containing the corrected DEM. Defaults to 
            `hydrocorrect_dem.tif`
    
    Returns: 
        None
    """
    print("Calculating hydrologically corrected DEM...")
    if not hydro_correct_dem_fname:
        hydro_correct_dem_fname = "hydrocorrect_dem.tif"
        
    run(["mpiexec", "-n", "2", "pitremove", "-z", dem_fname, "-fel",
         hydro_correct_dem_fname])

def make_flow_direction_map(dem_fname, flow_dir_map_fname=None):
    """ Make a flow direction map given a Digital Elevation Model.

    Resulting map will be coded such that 1=E, 2=NE, 3=N,..., 8=SE.

    See http://hydrology.usu.edu/taudem/taudem5/help53/D8FlowDirections.html
    for details of algorithm used.

    Args:
        dem_fname (str): Path to the GeoTiff file containing the source
            Digital Elevation Model.
        flow_dir_map_fname (str, optional): Path for the GeoTiff file 
            containing the generated flow direction map. Defaults to 
            `flowdir.tif`.
    
    Returns: 
        None    
    """
    if not flow_dir_map_fname:
        flow_dir_map_fname = "flowdir.tif"
    print("Calculating flow directions...")
    run(["mpiexec", "-n", "2", "d8flowdir", "-fel", dem_fname, "-sd8", 
        "tmp.tif", "-p", flow_dir_map_fname])
    
    # TauDEM's d8flowdir program automaticallt generates a grid showing slope 
    # in the flow direction which we don't need. Delete this.
    os.remove("tmp.tif")

def make_slope_map(dem_fname, slope_map_fname=None):
    """ Make a slope map given a Digital Elevation Model.

    Calculated values are percentage incline.

    Args:
        dem_fname (str): Path to the GeoTiff file containing the source
            Digital Elevation Model.
        slope_map_fname (str, optional): Path for the GeoTiff file containing 
            the generated slope map. Defaults to `slope.tif`.
    
    Returns: 
        None    
    """
    if not slope_map_fname:
        slope_map_fname = "slope.tif"
    
    print("Calculating slope...")
    run(["gdaldem", "slope", "-p", dem_fname, slope_map_fname])

def make_continuous_aspect_map(dem_fname, aspect_map_fname=None):
    """ Make a continuous aspect map given a Digital Elevation Model.

    Get continuous aspect in degrees (0 deg=E, 90 deg=N, 180 deg=W, 270 deg=S)

    Args:
        dem_fname (str): Path to the GeoTiff file containing the source
            Digital Elevation Model.
        aspect_map_fname (str, optional): Path for the GeoTiff file containing 
            the generated aspect map. Defaults to `continuous_aspect.tif`.
    
    Returns: 
        None    
    """
    if not aspect_map_fname:
        aspect_map_fname = "continuous_aspect.tif"
    print("Calculating aspect...")
    run(["gdaldem", "aspect",  dem_fname, aspect_map_fname, "-trigonometric",
        "-zero_for_flat"])

def make_binary_aspect_map(continuous_aspect_map_fname, 
        binary_aspect_map_fname=None):
    """ Make a continuous aspect map given a Digital Elevation Model.

    Get binary aspect in degrees, 0=Northerly, 1=Southerly

    Args:
        continuous_aspect_map_fname (str): Path to the continuous aspect map 
            GeoTiff file.
        binary_aspect_map_fname (str, optional): Path for the GeoTiff file 
            containing the generated binary aspect map. Defaults to 
            `binary_aspect.tif`.
    
    Returns: 
        None    
    """
    if not binary_aspect_map_fname:
        binary_aspect_map_fname = "binary_aspect.tif"

    print("Calculating aspect...")
    copyfile(continuous_aspect_map_fname, binary_aspect_map_fname)
    driver = gdal.GetDriverByName('GTIFF')
    aspect_raster = gdal.Open(binary_aspect_map_fname, gdal.GA_Update)
    band = aspect_raster.GetRasterBand(1).ReadAsArray()
    band = np.where([band < 180], 0, 1) 
    aspect_raster.GetRasterBand(1).WriteArray(band[0,:,:])
    aspect_raster=None

def derive_all(dem_fname, name_prefix=None, remove_pits=True, trim_edge=1):
    """Derive raster layers based on Digital Elevation Model.

    Args:
        dem_fname (str): Path to the GeoTiff file containing the source
            Digital Elevation Model.
        name_prefix (str, optional): Prefix given to all generated files, if 
            given. Defaults to None.
        remove_pits (boolean, optional): Whether or not to produce a 
            hydrologically corrected DEM. Defaults to True
        trim_edge (int, optional): Number of pixels to remove from each edge
            of the output files. Useful to remove 'missing data' cells at the 
            edge of flow direction maps.

    Returns:
        None    
    """
    layers = {
        "hydro_correct_dem": {"name": "hydrocorrect_dem.tif",
                              "func": make_hydro_correct_dem},
        "flow_direction_map": {"name": "flowdir.tif",
                               "func": make_flow_direction_map},
        "slope_map": {"name": "slope.tif",            
                      "func": make_slope_map},
        "continuous_aspect_map": {"name": "continuous_aspect.tif", 
                                  "func": make_continuous_aspect_map},
        "binary_aspect_map": {"name": "binary_aspect.tif", 
                              "func": make_binary_aspect_map}
    }

    if name_prefix:
        for k in layers.keys():
            layers[k]["name"] = add_prefix_to_fname(
                layers[k]["name"], name_prefix)

    def proc_layer(in_fname, out_fname, f, trim_edge):
        f(in_fname, out_fname)
        if trim_edge:
            trim_geotiff_edge(out_fname, out_fname, n=trim_edge)

    if remove_pits:
        new_dem_fname = layers["hydro_correct_dem"]["name"]
        proc_layer(dem_fname, new_dem_fname, 
            layers["hydro_correct_dem"]["func"], trim_edge=0)        
    else:
        new_dem_fname = dem_fname

    for layer_name in ["flow_direction_map", "slope_map", 
        "continuous_aspect_map"]:
        layer = layers[layer_name]
        proc_layer(new_dem_fname, layer["name"], layer["func"], trim_edge)

    layer = layers["binary_aspect_map"]
    # Don't trim binary aspect map again, continuous aspect map already trimmed
    layer["func"](layers["continuous_aspect_map"]["name"], layer["name"])

if __name__ == "__main__":
    derive_all("hydro_incorrect_dummy.tif")