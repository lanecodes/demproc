============================================================
dem_derive
============================================================

Derive various raster layers based on a Digital Elevation Model.

Fundamentally a wrapper around TauDEM_ and gdal_, so working installations of 
those are required.

Currently implemented:
- Hydrologically correct DEM (remove pits)
- Flow direction map
- Slope map
- Continuous aspect
- Binary aspect

.. _TauDEM: http://hydrology.usu.edu/taudem/taudem5/index.html
.. _gdal: https://www.gdal.org/