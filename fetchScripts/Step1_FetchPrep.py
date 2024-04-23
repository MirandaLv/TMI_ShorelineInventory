# -*- coding: utf-8 -*-
# Step 1: Fetch Prep
# Prepare the shoreline for determining fetch (distance across water).
# - Shoreline is dissolved  into one arc. 
# - Using the 'Generate Points Along Lines' tool, points are created along the line at the distance specified. 
# - Points are then used to split the arcs. 
# - A center point is created for each arc segment. These center points are used to calculate the fetch.
# - Finally, this model creates lines 10000m long in 16 directions originating from each shoreline point (center point).
# The user may specify a different length but the lines must be greater than 3219 m (2 miles) to capture high fetch.
# (updated April 2020) - modified for ArcPro (July 2020) - converted to a python script May 23, 2022
#


import arcpy
from sys import argv
import time
from time import strftime

# Script arguments
Shoreline = arcpy.GetParameter(0)            # Shoreline="Worcester_lubc"
Distance = arcpy.GetParameter(1)             # Distance="25 Meters"
name = arcpy.GetParameter(2)                 # name="Worcester"
workspaceGDB = arcpy.GetParameter(3)         # workspaceGDB="C:\\Users\\tamia\\myWorkspace\\SMM\\Maryland_SMM\\Worcester\\working\\Worcester_working_FileGDB.gdb"
Distance_Expression = arcpy.GetParameter(4)  # Distance_"50000"

# Set the overwriteOutput to true
arcpy.env.overwriteOutput = True

# Set the geoprocessing workspace
arcpy.env.workspace = workspaceGDB

# Local variables:
thedate = strftime("%m_%d_%Y")

wkspGDB = workspaceGDB

shlDissolve = "shoreline_Dissolved"
GeneratePoint = "GeneratePoint"
SplitLineAtPoint = "SplitLineAtPoint_" + name
LineCtrPnt = "SplitLine_center_point_" + name + "_" + thedate
BearingDist = "BearingDistance_arcs_" + name + "_" + thedate

# Select the lubc shoreline and make a copy. Then add and cacluate a field, then dissolve on that field
arcpy.analysis.Select(Shoreline, r"memory\shorelineCopy")
arcpy.management.AddField(r"memory\shorelineCopy", "shoreline", "TEXT")
arcpy.management.CalculateField(r"memory\shorelineCopy", "shoreline", "\"shl\"", "PYTHON3", "", "TEXT", "NO_ENFORCE_DOMAINS")
arcpy.management.Dissolve(r"memory\shorelineCopy", shlDissolve, ["shoreline"], [],"MULTI_PART", "DISSOLVE_LINES")
arcpy.Delete_management(r"memory\shorelineCopy")

# Generate Points Along Lines
arcpy.management.GeneratePointsAlongLines(shlDissolve, GeneratePoint, "DISTANCE", Distance, None, "NO_END_POINTS")

# Split Line at Point
arcpy.management.SplitLineAtPoint(shlDissolve, GeneratePoint, SplitLineAtPoint, "1 Meters")

# Add and calculate some Fields (splitID)
arcpy.management.AddField(SplitLineAtPoint, "splitID", "LONG", None, None, None, "", "NULLABLE", "NON_REQUIRED")
arcpy.management.CalculateField(SplitLineAtPoint, "splitID", "!OBJECTID!", "PYTHON3")
arcpy.management.AddField(SplitLineAtPoint, "ID", "LONG", None, None, None, "", "NULLABLE", "NON_REQUIRED")
arcpy.management.CalculateField(SplitLineAtPoint, "ID", "!splitID!", "PYTHON3")

# convert line segments to points: Feature To Point
arcpy.management.FeatureToPoint(SplitLineAtPoint, LineCtrPnt, "INSIDE")

# Copy the center points using Select. Then add several fields (XY coordinates, distance, degrees, direction.
arcpy.analysis.Select(LineCtrPnt, r"memory\centerPntsCopied")
arcpy.management.AddXY(r"memory\centerPntsCopied")
arcpy.management.AddField(r"memory\centerPntsCopied", "distance", "LONG")
arcpy.management.AddField(r"memory\centerPntsCopied", "degrees", "DOUBLE")
arcpy.management.AddField(r"memory\centerPntsCopied", "direction", "TEXT")

# Calculate Fields
arcpy.management.CalculateField(r"memory\centerPntsCopied", "distance", Distance_Expression, "PYTHON3")
arcpy.management.CalculateField(r"memory\centerPntsCopied", "direction", "\"n\"", "PYTHON3")
arcpy.management.CalculateField(r"memory\centerPntsCopied", "degrees", "0.0", "PYTHON3")

# Do a series of Selects to create 16 different points with different calculated directions and degrees
arcpy.analysis.Select(r"memory\centerPntsCopied", r"memory\tempPoint_1", where_clause="")
arcpy.management.CalculateField(r"memory\tempPoint_1", "direction", "\"nne\"", "PYTHON3")
arcpy.management.CalculateField(r"memory\tempPoint_1", "degrees", "22.5", "PYTHON3")

arcpy.analysis.Select(r"memory\centerPntsCopied", r"memory\tempPoint_2", where_clause="")
arcpy.management.CalculateField(r"memory\tempPoint_2","direction", "\"ne\"", "PYTHON3")
arcpy.management.CalculateField(r"memory\tempPoint_2", "degrees", "45", "PYTHON3")

arcpy.analysis.Select(r"memory\centerPntsCopied", r"memory\tempPoint_3", where_clause="")
arcpy.management.CalculateField(r"memory\tempPoint_3", "direction", "\"ene\"", "PYTHON3")
arcpy.management.CalculateField(r"memory\tempPoint_3", "degrees", "67.5", "PYTHON3")

arcpy.analysis.Select(r"memory\centerPntsCopied", r"memory\tempPoint_4", where_clause="")
arcpy.management.CalculateField(r"memory\tempPoint_4", "direction", "\"e\"", "PYTHON3")
arcpy.management.CalculateField(r"memory\tempPoint_4", "degrees", "90", "PYTHON3")

arcpy.analysis.Select(r"memory\centerPntsCopied", r"memory\tempPoint_5", where_clause="")
arcpy.management.CalculateField(r"memory\tempPoint_5", "direction", "\"ese\"", "PYTHON3")
arcpy.management.CalculateField(r"memory\tempPoint_5", "degrees", "112.5", "PYTHON3")

arcpy.analysis.Select(r"memory\centerPntsCopied", r"memory\tempPoint_6", where_clause="")
arcpy.management.CalculateField(r"memory\tempPoint_6", "direction", "\"se\"", "PYTHON3")
arcpy.management.CalculateField(r"memory\tempPoint_6", "degrees", "135", "PYTHON3")

arcpy.analysis.Select(r"memory\centerPntsCopied", r"memory\tempPoint_7", where_clause="")
arcpy.management.CalculateField(r"memory\tempPoint_7", "direction", "\"sse\"", "PYTHON3")
arcpy.management.CalculateField(r"memory\tempPoint_7", "degrees", "157.5", "PYTHON3")

arcpy.analysis.Select(r"memory\centerPntsCopied", r"memory\tempPoint_8", where_clause="")
arcpy.management.CalculateField(r"memory\tempPoint_8", "direction", "\"s\"", "PYTHON3")
arcpy.management.CalculateField(r"memory\tempPoint_8", "degrees", "180", "PYTHON3")

arcpy.analysis.Select(r"memory\centerPntsCopied", r"memory\tempPoint_9", where_clause="")
arcpy.management.CalculateField(r"memory\tempPoint_9", "direction", "\"ssw\"", "PYTHON3")
arcpy.management.CalculateField(r"memory\tempPoint_9", "degrees", "202.5", "PYTHON3")

arcpy.analysis.Select(r"memory\centerPntsCopied", r"memory\tempPoint_10", where_clause="")
arcpy.management.CalculateField(r"memory\tempPoint_10", "direction", "\"sw\"", "PYTHON3")
arcpy.management.CalculateField(r"memory\tempPoint_10", "degrees", "225", "PYTHON3")

arcpy.analysis.Select(r"memory\centerPntsCopied", r"memory\tempPoint_11", where_clause="")
arcpy.management.CalculateField(r"memory\tempPoint_11", "direction", "\"wsw\"", "PYTHON3")
arcpy.management.CalculateField(r"memory\tempPoint_11", "degrees", "247.5", "PYTHON3")

arcpy.analysis.Select(r"memory\centerPntsCopied", r"memory\tempPoint_12", where_clause="")
arcpy.management.CalculateField(r"memory\tempPoint_12", "direction", "\"w\"", "PYTHON3")
arcpy.management.CalculateField(r"memory\tempPoint_12", "degrees", "270", "PYTHON3")

arcpy.analysis.Select(r"memory\centerPntsCopied", r"memory\tempPoint_13", where_clause="")
arcpy.management.CalculateField(r"memory\tempPoint_13", "direction", "\"wnw\"", "PYTHON3")
arcpy.management.CalculateField(r"memory\tempPoint_13", "degrees", "292.5", "PYTHON3")

# Process: Select (15) (Select) (analysis)
arcpy.analysis.Select(r"memory\centerPntsCopied", r"memory\tempPoint_14", where_clause="")
arcpy.management.CalculateField(r"memory\tempPoint_14", "direction", "\"nw\"", "PYTHON3")
arcpy.management.CalculateField(r"memory\tempPoint_14", "degrees", "315", "PYTHON3")

arcpy.analysis.Select(r"memory\centerPntsCopied", r"memory\tempPoint_15", where_clause="")
arcpy.management.CalculateField(r"memory\tempPoint_15", "direction", "\"nnw\"", "PYTHON3")
arcpy.management.CalculateField(r"memory\tempPoint_15", "degrees", "337.5", "PYTHON3")

# Append all the tempPoints
test_pointsT_app = arcpy.management.Append([r"memory\tempPoint_1", r"memory\tempPoint_2", r"memory\tempPoint_3", r"memory\tempPoint_4", r"memory\tempPoint_5", r"memory\tempPoint_6",
                                           r"memory\tempPoint_7", r"memory\tempPoint_8", r"memory\tempPoint_9", r"memory\tempPoint_10", r"memory\tempPoint_11", r"memory\tempPoint_12",
                                           r"memory\tempPoint_13", r"memory\tempPoint_14", r"memory\tempPoint_15"], r"memory\centerPntsCopied", "NO_TEST")[0]

# Run Bearing Distance To Line to create the 16 direction arcs for each center point
arcpy.management.BearingDistanceToLine(test_pointsT_app, BearingDist, "POINT_X", "POINT_Y", "distance", "METERS", "degrees", "DEGREES", "GEODESIC", "ID",
                                       "PROJCS[\"NAD_1983_UTM_Zone_18N\",GEOGCS[\"GCS_North_American_1983\",DATUM[\"D_North_American_1983\",SPHEROID[\"GRS_1980\",6378137.0,298.257222101]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"False_Easting\",500000.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",-75.0],PARAMETER[\"Scale_Factor\",0.9996],PARAMETER[\"Latitude_Of_Origin\",0.0],UNIT[\"Meter\",1.0]];-5120900 -9998100 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision", attributes="NO_ATTRIBUTES")

# Frequency on degrees and direction, then join table to BearingDistance layer
arcpy.analysis.Frequency(test_pointsT_app, r"memory\degreesDirectionTable", ["degrees", "direction"])
arcpy.management.JoinField(BearingDist, "degrees", r"memory\degreesDirectionTable", "degrees", ["direction"])

# Clean up
arcpy.Delete_management(r"memory\tempPoint_1")
arcpy.Delete_management(r"memory\tempPoint_2")
arcpy.Delete_management(r"memory\tempPoint_3")
arcpy.Delete_management(r"memory\tempPoint_4")
arcpy.Delete_management(r"memory\tempPoint_5")
arcpy.Delete_management(r"memory\tempPoint_6")
arcpy.Delete_management(r"memory\tempPoint_7")
arcpy.Delete_management(r"memory\tempPoint_8")
arcpy.Delete_management(r"memory\tempPoint_9")
arcpy.Delete_management(r"memory\tempPoint_10")
arcpy.Delete_management(r"memory\tempPoint_11")
arcpy.Delete_management(r"memory\tempPoint_12")
arcpy.Delete_management(r"memory\tempPoint_13")
arcpy.Delete_management(r"memory\tempPoint_14")
arcpy.Delete_management(r"memory\tempPoint_15")
arcpy.Delete_management(r"memory\degreesDirectionTable")
arcpy.Delete_management(r"memory\centerPntsCopied")


# Return Output files
arcpy.SetParameterAsText(5, shlDissolve)
arcpy.SetParameterAsText(6, GeneratePoint)
arcpy.SetParameterAsText(7, SplitLineAtPoint)
arcpy.SetParameterAsText(8, LineCtrPnt)
arcpy.SetParameterAsText(9, BearingDist)

arcpy.AddMessage ("process completed")
