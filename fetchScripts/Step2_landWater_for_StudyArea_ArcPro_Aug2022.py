# -*- coding: utf-8 -*-
#
# Create a land/water feature class for the study area.
# Create a linear feature class to use for the water arcs template.
# Will need to manually add the water and land values to the field surface.
# Output: {name}_LandWaterPoly_{date}, {name}_water_arcs_template_{date}
# converted to ArcPro script August 2022
#

# Import arcpy module
import arcpy
from sys import argv
from arcpy import env
import time
from time import strftime

# Script arguments
name = arcpy.GetParameter(0)
workspaceGDB = arcpy.GetParameter(1)
studyArea = arcpy.GetParameter(2)
shoreline = arcpy.GetParameter(3)
BearingDistArcs = arcpy.GetParameter(4)
# distA = arcpy.GetParameter(4)
# distB = arcpy.GetParameter(5)
# BearingDistArcs = arcpy.GetParameter(6)

# Set the overwriteOutput to true
env.overwriteOutput = True

# Set the geoprocessing workspace
env.workspace = workspaceGDB

# Local variables:
date = strftime("%m_%d_%Y")
landWater = name + "_LandWaterPoly_" + date
waterArcsTemplate = name + "_water_arcs_template_" + date


# Buffer Study Area 10000m and 10010m. This is to create a land water polygon layer.
arcpy.analysis.Buffer(studyArea, "StudyArea_buffer", "10000 Meters", "FULL", "ROUND", "ALL")
arcpy.analysis.Buffer(studyArea, r"memory\tempBuffer", "10010 Meters", "FULL", "ROUND", "ALL")
# arcpy.analysis.Buffer(studyArea, "StudyArea_buffer", distA, "FULL", "ROUND", "ALL")
# arcpy.analysis.Buffer(studyArea, r"memory\tempBuffer", distB, "FULL", "ROUND", "ALL")

# Clip the regional shoreline. Use the clipped arc and the study area buffered boundary to create a polygon for land/water using Feature to Polygon. Fibally, add the "surface" field - Will need to manually select water polygons and calculate surface = "water" and surface = "land"
arcpy.analysis.Clip(shoreline, r"memory\tempBuffer", "chesbay_arcs_clip", "0.01 Meters")
arcpy.management.FeatureToPolygon(["StudyArea_buffer", "chesbay_arcs_clip"], landWater, "0.01 Meters", "NO_ATTRIBUTES", "")
arcpy.management.AddField(landWater, "surface", "TEXT", None, None, None, "", "NULLABLE", "NON_REQUIRED", "")

# Select Bearing Distance arcs to create a linear feature class to use for the water arcs template.
arcpy.analysis.Select(BearingDistArcs, r"memory\temp_sel", "\"ID\" = 10")
# Merge seelected bearing distance arcs with clipped shoreline arcs
arcpy.management.Merge(["chesbay_arcs_clip", r"memory\temp_sel"], "merge_temp", "", "NO_SOURCE_INFO")
# Select "distance is null"
arcpy.analysis.Select("merge_temp", r"memory\baseShl_temp", "\"distance\" IS NULL")
# Add Field surface
arcpy.management.AddField(r"memory\baseShl_temp", "surface", "TEXT", None, None, None, "", "NULLABLE", "NON_REQUIRED", "")
# Use Describe to get a SpatialReference object
spatial_ref = arcpy.Describe("StudyArea_buffer").spatialReference
# Finally, Create Feature Class
arcpy.management.CreateFeatureclass(workspaceGDB, waterArcsTemplate, "POLYLINE", r"memory\baseShl_temp", "DISABLED", "DISABLED", spatial_ref)

# file clean up
arcpy.Delete_management(r"memory\baseShl_temp")
arcpy.Delete_management(r"memory\temp_sel")
arcpy.Delete_management(r"memory\tempBuffer")
arcpy.Delete_management("merge_temp")

# Return output 
arcpy.SetParameterAsText(5, landWater)
arcpy.SetParameterAsText(6, waterArcsTemplate)


arcpy.AddMessage("Script complete")
