gdal_translate -mask 4 default_modified.tif trans.tif
gdal2tiles.py trans.tif /Users/nakamurasatoru/git/d_hi/map/shoen/batch/docs/files/仁-126 -z3-18 --xyz --processes=1