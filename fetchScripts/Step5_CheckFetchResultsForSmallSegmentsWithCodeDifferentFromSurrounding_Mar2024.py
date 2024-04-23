# -*- coding: utf-8 -*-
# CheckFetchResultsForSmallSegmentsWithCodeDifferentFromSurrounding_Mar2024.py
#
# This script looks for arc segments 25m or less that have a fetch coding that is 
# different from the code of neighboring arcs.
#
# Arcs are flagged in the 'comment' and 'doThis' fields and must be manually checked and coding switched if deemed necessary.
#
# Import arcpy module
import arcpy
from arcpy import env
import time
from time import strftime

# Script arguments
workspaceGDB = arcpy.GetParameter(0)
# for example: "workspaceGDB = r"C:\Users\tamia\myWorkspace\SMM\VA_inventory_2023_2026\Hampton_2024\Hampton_2024_WorkingFetch.gdb"
inputFeaturelayer = arcpy.GetParameter(1)
# for example: "Hampton_fetch_withQuadAnalysis_arcs_03_25_2024_Final"
StudyAreaName = arcpy.GetParameterAsText(2) # for example: "Worcester"


# Set the overwriteOutput to true
env.overwriteOutput = True

# Set the geoprocessing workspace
env.workspace = workspaceGDB

# Local variables:
date = strftime("%m_%d_%Y")

fetchChecked_output = StudyAreaName + "_fetch_smallArcsToCheck" + date

# Take the ouput from the Fetch model and check for arcs less than or equal to 25 m located between another fetch classification. These areas are flagged and changed to match the coding it is embedded within.

# make a copy of the fetch output - use Select tool
# arcpy.management.Copy(inputFeaturelayer, "fetch_output_Copy_temp", "FeatureClass", None)
arcpy.analysis.Select(inputFeaturelayer, "fetch_output_Copy_temp")

# Dissolve on MaxQuadFetchCode to create "fetch_Dissolve_maxQuadFetchCode_temp", then Add fields (aDisID, comment)
arcpy.management.Dissolve("fetch_output_Copy_temp", "fetch_Dissolve_maxQuadFetchCode_temp", 'MxQExpCode', "", 'SINGLE_PART', 'DISSOLVE_LINES')
arcpy.management.AddField("fetch_Dissolve_maxQuadFetchCode_temp", "aDisID", "LONG", None, None, None, "", "NULLABLE", "NON_REQUIRED", "")
arcpy.management.AddField("fetch_Dissolve_maxQuadFetchCode_temp", "comment", "TEXT", None, None, None, "", "NULLABLE", "NON_REQUIRED", "")
arcpy.management.CalculateField("fetch_Dissolve_maxQuadFetchCode_temp", "aDisID", "!OBJECTID!")

# Select arcs lte 25.1m, creating "SelectArcsLTE25m"
arcpy.analysis.Select("fetch_Dissolve_maxQuadFetchCode_temp", "SelectArcsLTE25m", "Shape_Length <= 25.1")

# Buffer "SelectArcsLTE25m" 0.25 meters
arcpy.analysis.Buffer("SelectArcsLTE25m", "SelectArcsLTE25m_Buf", "0.25 Meters", "FULL", "ROUND", "NONE", [], "PLANAR")

# Run Feature Vertices To Points
arcpy.management.FeatureVerticesToPoints("fetch_Dissolve_maxQuadFetchCode_temp", "fetch_LineStartEndPoints", "BOTH_ENDS")

# Intersect Points with the buffer (SelectArcsLTE25m_Buf)
arcpy.analysis.Intersect([["SelectArcsLTE25m_Buf", ""], ["fetch_LineStartEndPoints", ""]], "SelectArcsLTE25m_Int_Points", "ALL", "", "POINT")

# Run Frequencies and then use Pivot Table to
arcpy.analysis.Frequency("SelectArcsLTE25m_Int_Points", "SelectArcsLTE25m_Int_freq", ["aDisID", "aDisID_1", "MxQExpCode_1"], [])
arcpy.analysis.Frequency("SelectArcsLTE25m_Int_freq", "SelectArcsLTE25m_Int_freq2", ["aDisID", "MxQExpCode_1"], [])
arcpy.management.PivotTable("SelectArcsLTE25m_Int_freq2", ["aDisID"], "MxQExpCode_1", "FREQUENCY", "SelectArcsLTE25m_Int_freq2_PT")

# Join fetch classification to buffer
arcpy.management.JoinField("SelectArcsLTE25m_Buf", "aDisID", "SelectArcsLTE25m_Int_freq2_PT", "aDisID", ["low", "moderate", "high"])

# Add field doThis
arcpy.management.AddField("SelectArcsLTE25m_Buf", "doThis", "TEXT")
arcpy.management.AddField("SelectArcsLTE25m_Buf", "originalMaxQuadFetch", "TEXT")
arcpy.management.CalculateField("SelectArcsLTE25m_Buf", "originalMaxQuadFetch", "!MxQExpCode!")

# Make Feature Layer from buffer to check for number of occurances of low where 1 indicates low fetch is on one side of Structural and 2 = Living Shoreline is on both end of Structural.
arcpy.management.MakeFeatureLayer("SelectArcsLTE25m_Buf", "Output_Layer")
arcpy.management.SelectLayerByAttribute("Output_Layer", "NEW_SELECTION", "low = 2")
arcpy.management.CalculateField("Output_Layer", "comment", '"change to low"')
arcpy.management.SelectLayerByAttribute("Output_Layer", "NEW_SELECTION", "low = 1 And MxQExpCode <> 'low'")
arcpy.management.CalculateField("Output_Layer", "doThis", '"qc"')

arcpy.management.SelectLayerByAttribute("Output_Layer", "NEW_SELECTION", "moderate = 2")
arcpy.management.CalculateField("Output_Layer", "comment", '"change to moderate"')
arcpy.management.SelectLayerByAttribute("Output_Layer", "NEW_SELECTION", "moderate = 1 And MxQExpCode <> 'moderate'")
arcpy.management.CalculateField("Output_Layer", "doThis", '"qc"')

arcpy.management.SelectLayerByAttribute("Output_Layer", "NEW_SELECTION", "high = 2")
arcpy.management.CalculateField("Output_Layer", "comment", '"change to high"')
arcpy.management.SelectLayerByAttribute("Output_Layer", "NEW_SELECTION", "high = 1 And MxQExpCode <> 'high'")
arcpy.management.CalculateField("Output_Layer", "doThis", '"qc"')

arcpy.management.SelectLayerByAttribute("Output_Layer", "NEW_SELECTION", "comment IS NULL And doThis IS NULL", None)
arcpy.management.CalculateField("Output_Layer", "comment", '"marsh island?"')

# Clear Selection
arcpy.management.SelectLayerByAttribute("Output_Layer", "CLEAR_SELECTION")

# Join buffer fields to "fetch_Dissolve_maxQuadFetchCode_temp"
arcpy.management.JoinField("fetch_Dissolve_maxQuadFetchCode_temp", "aDisID", "SelectArcsLTE25m_Buf", "aDisID", "comment;doThis;high;low;moderate;originalMaxQuadFetch")

# Use Select to copy to final output
arcpy.analysis.Select("fetch_Dissolve_maxQuadFetchCode_temp", fetchChecked_output)

# Delete unnecessary layers
arcpy.management.Delete("fetch_LineStartEndPoints")
arcpy.management.Delete("SelectArcsLTE25m_Int_freq")
arcpy.management.Delete("SelectArcsLTE25m_Int_freq2")
arcpy.management.Delete("fetch_output_Copy_temp")
arcpy.management.Delete("SelectArcsLTE25m")
arcpy.management.Delete("SelectArcsLTE25m_Int_Points")
arcpy.management.Delete("fetch_Dissolve_maxQuadFetchCode_temp")
arcpy.management.Delete("SelectArcsLTE25m_Int_freq2_PT")
arcpy.management.Delete("SelectArcsLTE25m_Buf")


# Return Output file
arcpy.SetParameterAsText(3, fetchChecked_output)

arcpy.AddMessage("Script complete")