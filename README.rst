==============================================================================
DEMproc
==============================================================================

Purpose
------------------------------------------------------------------------------
Derive various raster layers based on a Digital Elevation Model.

Fundamentally a wrapper around TauDEM_ and gdal_, so working installations of 
those are required.

Currently implemented:

- Hydrologically correct DEM (remove pits)
- Flow direction map
- Slope map
- Continuous aspect
- Binary aspect

Standard usage
------------------------------------------------------------------------------

.. code-block:: python

   import demproc
   demproc.derive_all("dem.tif", "my_study_site")

.. _TauDEM: http://hydrology.usu.edu/taudem/taudem5/index.html
.. _gdal: https://www.gdal.org/