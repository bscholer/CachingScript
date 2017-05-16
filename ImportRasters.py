#AUTHOR: BEN SCHOLER 5/16/2017
import arcpy
import os
import time
import datetime

county = raw_input("Enter name of county (HamiltonCountyIN): ")
year = raw_input("Enter year orthos were captured: ")
orthos = raw_input("Enter path of directory with orthos rasters: ")
res = raw_input("Enter resolution if multiple resolutions exist. Otherwise, leave blank (3Inch, 1Meter): ")
geodb = raw_input("Enter name of geodatabase if it exists. Otherwise, leave blank (HamiltonCountyIN_2017Orthos): ")

# This should be changed to match where you store county ortho data. A folder will be
# created inside of it called the county name (HamiltonCountyIN), which will contain the geodatabase.
basepath = "T:/Orthos/"

if len(res) > 0:
    name = county + "_" + year + "_" + res
else:
    name = county + "_" + year + "_Orthos"
if len(geodb) > 0:
    gdb = basepath + county + "/" + geodb + ".gdb"
else:
    gdb = basepath + county + "/" + name + ".gdb"

if not os.path.exists(basepath + county):
    os.makedirs(basepath + county)
if len(geodb) == 0:
    arcpy.CreateFileGDB_management(basepath + county, name);

tiffs = ""
arcpy.env.pyramid = "NONE"
arcpy.env.rasterStatistics = "NONE"
arcpy.compression = "JPEG 50"
arcpy.env.resamplingMethod = "BILINEAR"

start = time.time();
i = 0
while i < len(os.listdir(orthos)):
    file = os.listdir(orthos)[i]
    if file.endswith(".tif") | file.endswith(".jpg"):
        end = time.time()
        print (str(i) + " / " + str(len(os.listdir(orthos))))
        print("Remaining time: " + str(datetime.timedelta(seconds=int(end - start) / i) * (len(os.listdir(orthos)) - i)))
        # Expecting to have a .tfw file first.
        if i == 0 | i == 1:
            arcpy.RasterToGeodatabase_conversion(orthos + "/" + file, gdb);
            if file.endswith(".tif"):
                arcpy.CopyRaster_management(gdb + "/T" + file[:file.index(".")], gdb + "/" + name)
                arcpy.Delete_management(gdb + "/T" + file[:file.index(".")])
            else:
                arcpy.CopyRaster_management(gdb + "/" + file[:file.index(".")], gdb + "/" + name)
                arcpy.Delete_management(gdb + "/" + file[:file.index(".")])
            start = time.time()
        else:
            arcpy.Mosaic_management(inputs = orthos + "/" + file,
                                    target = gdb + "/" + name,
                                    mosaic_type = "LAST", colormap = "FIRST", background_value = "", nodata_value = "",
                                    onebit_to_eightbit = "NONE", mosaicking_tolerance = "0", MatchingMethod = "NONE")
    i += 1

print("BUILDING PYRAMIDS")
arcpy.BuildPyramids_management(
        in_raster_dataset = gdb + "/" + name,
        pyramid_level = "-1", SKIP_FIRST = "NONE", resample_technique = "BILINEAR", compression_type = "JPEG",
        compression_quality = "50", skip_existing = "OVERWRITE")
