# -*- coding: utf-8 -*-
# Step4: Fetch Analysis script
# This script has three major sections. 
# The first finds the maximum arc length and direction for each point 
# along the shoreline and creates a pivot table containing the direction 
# and distance of each water arc by ID.
# The second checks the pivot table to determine if there are any ids 
# that have a frequency greater than 1. If so, the  pivot table is 
# fixed so that there is only one of each unique ID. 
# The third part modifies the initial single line maximum fetch 
# results by calculating the average quadrant fetch for each of 4 quadrants
# (NE, SE, SW, NW) and then chooses the longest average quadrant fetch.

# (originally updated April 2020 as a modelbuilder model) 
# model Updated for Pro Nov 2021
# Converted to a script for ArcPro June 2022

# Import arcpy module
import arcpy
from sys import argv
from arcpy import env
import time
from time import strftime


# This is for running in ArcPro python window as a test
# workspaceGDB = r"N:\cci\living_shl\SMM_Versions\SMM_version5_1_2019\Maryland_SMMv5_1\QueenAnnes\Working\QueenAnnesMD_working_FileGDB.gdb"
# WaterArcs = r"N:\cci\living_shl\SMM_Versions\SMM_version5_1_2019\Maryland_SMMv5_1\QueenAnnes\Working\QueenAnnesMD_working_FileGDB.gdb\QueenAnnes_water_arcs_all_06012022"
# SplitShoreline = r"N:\cci\living_shl\SMM_Versions\SMM_version5_1_2019\Maryland_SMMv5_1\QueenAnnes\Working\QueenAnnesMD_working_FileGDB.gdb\SplitLineAtPoint_QueenAnnes"
# CenterPoints = r"N:\cci\living_shl\SMM_Versions\SMM_version5_1_2019\Maryland_SMMv5_1\QueenAnnes\Working\QueenAnnesMD_working_FileGDB.gdb\SplitLine_center_point_QueenAnnes_05_24_2022"
# name = "QueenAnnes"


# Script arguments
workspaceGDB = arcpy.GetParameter(0)
# for example: "N:\\cci\\living_shl\\SMM_Versions\\SMM_version5_1_2019\\Maryland_SMMv5_1\\Worchester\\working\\WorchesterMD_working_FileGDB.gdb"
WaterArcs = arcpy.GetParameter(1)
# for example: "C:\\Users\\tamia\\myWorkspace\\SMM\\Maryland_SMM\\Worcester\\working\\Worcester_working_FileGDB.gdb\\Worcester_water_arcs_all_11092021"
SplitShoreline = arcpy.GetParameter(2)
# for example: "C:\\Users\\tamia\\myWorkspace\\SMM\\Maryland_SMM\\Worcester\\working\\Worcester_working_FileGDB.gdb\\Worcester_SplitLineAtPoint"
CenterPoints = arcpy.GetParameter(3)
# for example: "C:\\Users\\tamia\\myWorkspace\\SMM\\Maryland_SMM\\Worcester\\working\\Worcester_working_FileGDB.gdb\\Worcester_SplitLine_center_point_Nov_01_2021"
name = arcpy.GetParameterAsText(4) # for example: "Worcester"

# Set the overwriteOutput to true
env.overwriteOutput = True

# Set the geoprocessing workspace
env.workspace = workspaceGDB

# Local variables:
date = strftime("%m_%d_%Y")

# Begin by finding maximum arc length and direction for each for each point 
# along the shoreline and create a pivot table containing the direction 
# and distance of each water arc by ID.

# run statistics on length then join max length to water arcs
waterArcsStats = name + "_selected_water_arcs_" + date + "stats"
arcpy.analysis.Statistics(WaterArcs, waterArcsStats, [["Shape_Length", "MAX"]], ["ID"])
arcpy.management.JoinField(WaterArcs, "ID", waterArcsStats, "ID", ["MAX_Shape_Length"])

# Select water arcs where length = max length, then Add Field (maxDir) and calculate maxDir = direction
maxWtrArcs = name + "_selected_arcs_max_distance_" + date
arcpy.analysis.Select(WaterArcs, maxWtrArcs, "Shape_Length = MAX_Shape_Length")
arcpy.management.AddField(maxWtrArcs, "maxDir", "TEXT", None, None, None, "", "NULLABLE", "NON_REQUIRED", "")
arcpy.management.CalculateField(maxWtrArcs, "maxDir", "!direction!", "PYTHON3", "", "TEXT", "NO_ENFORCE_DOMAINS")

# Pivot the Water Arcs then join the maximum arc length and direction to the water arcs pivot table
WtrArcsPT = name + "_selected_water_arcs_" + date + "_PT"
arcpy.management.PivotTable(WaterArcs, ["ID"], "direction", "Shape_Length", WtrArcsPT)
arcpy.management.JoinField(WtrArcsPT, "ID", maxWtrArcs, "ID", ["MAX_Shape_Length", "maxDir"])

# Run Summary Statistics on the water arcs pivot table
wtrPTSumStat = name + "_PT_stats_" + date
arcpy.analysis.Statistics(WtrArcsPT, wtrPTSumStat, [["e", "SUM"], ["ene", "SUM"], ["ese", "SUM"], ["n", "SUM"], ["ne", "SUM"], ["nne", "SUM"], ["nnw", "SUM"], ["nw", "SUM"], ["s", "SUM"], ["se", "SUM"], ["sse", "SUM"], ["ssw", "SUM"], ["sw", "SUM"], ["w", "SUM"], ["wnw", "SUM"], ["wsw", "SUM"]], ["ID"])

# find all the null values in the pivot table stats table (wtrPTSumStat) and make them zero
fieldObs = arcpy.ListFields(wtrPTSumStat)
fieldNames = []  
for field in fieldObs:  
    fieldNames.append(field.name)  
del fieldObs  
fieldCount = len(fieldNames) 
with arcpy.da.UpdateCursor(wtrPTSumStat, fieldNames) as curU:  
    for row in curU:  
        rowU = row  
        for field in range(fieldCount):  
            if rowU[field] == None:  
                rowU[field] = "0"                  
        curU.updateRow(rowU)
del curU

# Join the water arc pivot table (WtrArcsPT) directions (n, e, etc) data to the pivot table stats file (wtrPTSumStat)
arcpy.management.JoinField(wtrPTSumStat, "ID", WtrArcsPT, "ID", ["e", "ene", "ese", "n", "ne", "nne", "nnw", "nw", "s", "se", "sse", "ssw", "sw", "w", "wnw", "wsw", "MAX_Shape_Length", "maxDir"])

# Calculate the direction fields with the direction_sum fields (ex. e = SUM_e)
arcpy.management.CalculateField(wtrPTSumStat, "e", "!SUM_e!", "PYTHON3")
arcpy.management.CalculateField(wtrPTSumStat, "ene", "!SUM_ene!", "PYTHON3")
arcpy.management.CalculateField(wtrPTSumStat, "ese", "!SUM_ese!", "PYTHON3")
arcpy.management.CalculateField(wtrPTSumStat, "n", "!SUM_n!", "PYTHON3")
arcpy.management.CalculateField(wtrPTSumStat, "ne", "!SUM_ne!", "PYTHON3")
arcpy.management.CalculateField(wtrPTSumStat, "nne", "!SUM_nne!", "PYTHON3")
arcpy.management.CalculateField(wtrPTSumStat, "nnw", "!SUM_nnw!", "PYTHON3")
arcpy.management.CalculateField(wtrPTSumStat, "nw", "!SUM_nw!", "PYTHON3")
arcpy.management.CalculateField(wtrPTSumStat, "s", "!SUM_s!", "PYTHON3")
arcpy.management.CalculateField(wtrPTSumStat, "se", "!SUM_se!", "PYTHON3")
arcpy.management.CalculateField(wtrPTSumStat, "sse", "!SUM_sse!", "PYTHON3")
arcpy.management.CalculateField(wtrPTSumStat, "ssw", "!SUM_ssw!", "PYTHON3")
arcpy.management.CalculateField(wtrPTSumStat, "sw", "!SUM_sw!", "PYTHON3")
arcpy.management.CalculateField(wtrPTSumStat, "w", "!SUM_w!", "PYTHON3")
arcpy.management.CalculateField(wtrPTSumStat, "wnw", "!SUM_wnw!", "PYTHON3")
arcpy.management.CalculateField(wtrPTSumStat, "wsw", "!SUM_wsw!", "PYTHON3")

# Copy split line at point layer to new layer 'name_exposure_date' (exposureArcs), then join the direction fields, max direction and max length from wtrPTSumStat
exposureArcs = name + "_exposure_" + date
arcpy.analysis.Select(SplitShoreline, exposureArcs, "")
arcpy.management.JoinField(exposureArcs, "ID", wtrPTSumStat, "ID", fields=["e", "ene", "ese", "n", "ne", "nne", "nnw", "nw", "s", "se", "sse", "ssw", "sw", "w", "wnw", "wsw", "MAX_Shape_Length", "maxDir"])

# Add Field (exposure) to exposureArcs
arcpy.management.AddField(exposureArcs, "exposure", "TEXT", None, None, None, "", "NULLABLE", "NON_REQUIRED", "")

# Use update cursor to classifiy the max arc lenth in the exposure field
# set the variables, then create the update cursor for the feature class
fc = exposureArcs
fields = ['MAX_Shape_Length', 'exposure']
with arcpy.da.UpdateCursor(fc, fields) as cursor:
    # For each row, evaluate the 'MAX_Shape_Length' value (index position 
    # of 0), and update 'exposure' (index position of 1)
    for row in cursor:
        if (row[0] == None):
            row[1] = "point misplacement"
        elif (row[0] <= 804.67):
            row[1] = "low"
        elif (row[0] > 804.67 and row[0] <= 3218.69):
            row[1] = "moderate"
        elif (row[0] > 3218.69):
            row[1] = "high"

        # Update the cursor with the updated list
        cursor.updateRow(row)
del cursor


# Select splitLine_center_points (CenterPoints) and copy to name_exposure_points_date (exposurePoints)
exposurePoints = name + "_exposure_points_" + date
arcpy.analysis.Select(CenterPoints, exposurePoints, "")

# Join the directions fields, max shape length, maxDir, and exposure fields from exposureArcs
arcpy.management.JoinField(exposurePoints, "splitID", exposureArcs, "splitID", ["e", "ene", "ese", "n", "ne", "nne", "nnw", "nw", "s", "se", "sse", "ssw", "sw", "w", "wnw", "wsw", "MAX_Shape_Length", "maxDir", "exposure"])

# make a copy of exposurePoints and add count and mean fields for the quadrants (ne, se, sw, nw) and calculate count fields
quadAnalyPntsA = name + "_fetch_withQuadAnalysis_points_" + date + "_part1"
arcpy.analysis.Select(exposurePoints, quadAnalyPntsA, "")
arcpy.management.AddField(quadAnalyPntsA, "NE_Count", "LONG", None, None, None, "", "NULLABLE", "NON_REQUIRED", "")
arcpy.management.AddField(quadAnalyPntsA, "NW_Count", "LONG", None, None, None, "", "NULLABLE", "NON_REQUIRED", "")
arcpy.management.AddField(quadAnalyPntsA, "SE_Count", "LONG", None, None, None, "", "NULLABLE", "NON_REQUIRED", "")
arcpy.management.AddField(quadAnalyPntsA, "SW_Count", "LONG", None, None, None, "", "NULLABLE", "NON_REQUIRED", "")
arcpy.management.CalculateField(quadAnalyPntsA, "NE_Count", "sum(1 for field in ( !n! , !ne! , !nne! , !ene! , !e! ) if field)", "PYTHON3", "", "TEXT", "NO_ENFORCE_DOMAINS")
arcpy.management.CalculateField(quadAnalyPntsA, "SW_Count", "sum(1 for field in ( !s!, !ssw!, !sw!, !wsw!, !w! ) if field)", "PYTHON_9.3", "", "TEXT", "NO_ENFORCE_DOMAINS")
arcpy.management.CalculateField(quadAnalyPntsA, "SE_Count", "sum(1 for field in ( !e! , !ese! , !se! , !sse! , !s! ) if field)", "PYTHON3", "", "TEXT", "NO_ENFORCE_DOMAINS")
arcpy.management.CalculateField(quadAnalyPntsA, "NW_Count", "sum(1 for field in ( !n! , !w! , !wnw! , !nw! , !nnw!) if field)", "PYTHON3", "", "TEXT", "NO_ENFORCE_DOMAINS")
arcpy.management.AddField(quadAnalyPntsA, "NE_Mean", "DOUBLE", 14, 4, None, "", "NULLABLE", "NON_REQUIRED", "")
arcpy.management.AddField(quadAnalyPntsA, "NW_Mean", "DOUBLE", 14, 4, None, "", "NULLABLE", "NON_REQUIRED", "")
arcpy.management.AddField(quadAnalyPntsA, "SE_Mean", "DOUBLE", 14, 4, None, "", "NULLABLE", "NON_REQUIRED", "")
arcpy.management.AddField(quadAnalyPntsA, "SW_Mean", "DOUBLE", 14, 4, None, "", "NULLABLE", "NON_REQUIRED", "")
 
# Calculate quadrant means
arcpy.management.MakeFeatureLayer(quadAnalyPntsA, "quadAnalysisLayerA")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerA", "NEW_SELECTION", "NE_Count = 0", "") 
arcpy.management.CalculateField("quadAnalysisLayerA", "NE_Mean", "0", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerA", "NEW_SELECTION", "NE_Count > 0", "")
arcpy.management.CalculateField("quadAnalysisLayerA", "NE_Mean", "( !n! + !nne! + !ne! + !ene! + !e! )/ !NE_Count!", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerA", "NEW_SELECTION", "SW_Count > 0", "")
arcpy.management.CalculateField("quadAnalysisLayerA", "SW_Mean", "( !s! + !ssw! + !sw! + !wsw! + !w! )/ !SW_Count!", "PYTHON3", )
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerA", "NEW_SELECTION", "SW_Count = 0", "")
arcpy.management.CalculateField("quadAnalysisLayerA", "SW_Mean", "0", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerA", "NEW_SELECTION", "SE_Count > 0", "")
arcpy.management.CalculateField("quadAnalysisLayerA", "SE_Mean", "( !e! + !ese! + !se! + !sse! + !s! )/ !SE_Count!", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerA", "NEW_SELECTION", "SE_Count = 0", "")
arcpy.management.CalculateField("quadAnalysisLayerA", "SE_Mean", "0", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerA", "NEW_SELECTION", "NW_Count > 0", "")
arcpy.management.CalculateField("quadAnalysisLayerA", "NW_Mean", "( !n! + !nnw! + !nw! + !wnw! + !w! )/ !NW_Count!", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerA", "NEW_SELECTION", "NW_Count = 0", "")
arcpy.management.CalculateField("quadAnalysisLayerA", "NW_Mean", "0", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerA", "CLEAR_SELECTION", "")

# Add and calc MaxQuadFetch, then add more quad fields
arcpy.management.AddField(quadAnalyPntsA, "MaxQFetch", "DOUBLE", 14, 4, None, "MaxQuadFetch", "NULLABLE", "NON_REQUIRED", "")
arcpy.management.CalculateField(quadAnalyPntsA, "MaxQFetch", "max([ !NE_Mean! , !SW_Mean! , !SE_Mean! , !NW_Mean! ])", "PYTHON3")
arcpy.management.AddField(quadAnalyPntsA, "MxQExpCode", "TEXT", None, None, None, "MaxQuadFetchCode", "NULLABLE", "NON_REQUIRED", "")
arcpy.management.AddField(quadAnalyPntsA, "MaxQuadDir", "TEXT", None, None, None, "", "NULLABLE", "NON_REQUIRED", "")
arcpy.management.AddField(quadAnalyPntsA, "QuadCnt1", "TEXT", None, None, None, "QuadCountOne", "NULLABLE", "NON_REQUIRED", "")
arcpy.management.AddField(quadAnalyPntsA, "OneIsMax", "TEXT", None, None, None, "", "NULLABLE", "NON_REQUIRED", "")
arcpy.management.AddField(quadAnalyPntsA, "MxQFetchOld", "DOUBLE", None, 4, None, "MaxQuadFetchOriginal", "NULLABLE", "NON_REQUIRED", "")
arcpy.management.AddField(quadAnalyPntsA, "MxQExpCodeO", "TEXT", None, None, None, "MaxQuadFetchCodeOriginal", "NULLABLE", "NON_REQUIRED", "")
arcpy.management.AddField(quadAnalyPntsA, "MaxQDirO", "TEXT", None, None, None, "MaxQuadDirOriginal", "NULLABLE", "NON_REQUIRED", "")


# Calculate the MaxQuadDir and the MxQExpCode (MaxQuadFetchCode)
arcpy.management.MakeFeatureLayer(quadAnalyPntsA, "quadAnalysisLayerB")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerB", "NEW_SELECTION", "ROUND (NE_Mean, 4) =  ROUND (MaxQFetch, 4)", "")
arcpy.management.CalculateField("quadAnalysisLayerB", "MaxQuadDir", "\"NE\"", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerB", "NEW_SELECTION", "ROUND (SW_Mean, 4) =  ROUND (MaxQFetch, 4)", "")
arcpy.management.CalculateField("quadAnalysisLayerB", "MaxQuadDir", "\"SW\"", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerB", "NEW_SELECTION", "ROUND (SE_Mean, 4) =  ROUND (MaxQFetch, 4)", "")
arcpy.management.CalculateField("quadAnalysisLayerB", "MaxQuadDir", "\"SE\"", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerB", "NEW_SELECTION", "ROUND (NW_Mean, 4) =  ROUND (MaxQFetch, 4)", "")
arcpy.management.CalculateField("quadAnalysisLayerB", "MaxQuadDir", "\"NW\"", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerB", "NEW_SELECTION", "MaxQFetch >= 804.67 AND MaxQFetch < 3218.69", "")
arcpy.management.CalculateField("quadAnalysisLayerB", "MxQExpCode", "\"moderate\"", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerB", "NEW_SELECTION", "MaxQFetch >= 3218.69", "")
arcpy.management.CalculateField("quadAnalysisLayerB", "MxQExpCode", "\"high\"", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerB", "NEW_SELECTION", "MaxQFetch < 804.67", "")
arcpy.management.CalculateField("quadAnalysisLayerB", "MxQExpCode", "\"low\"", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerB", "CLEAR_SELECTION", "", "")

# Calculate three fields that will hold the original or old values (for comparison?)
arcpy.management.CalculateField(quadAnalyPntsA, "MxQFetchOld", "!MaxQFetch!", "PYTHON3")
arcpy.management.CalculateField(quadAnalyPntsA, "MxQExpCodeO", "!MxQExpCode!", "PYTHON3")
arcpy.management.CalculateField(quadAnalyPntsA, "MaxQDirO", "!MaxQuadDir!", "PYTHON3")


# Expression and Code block for calculating the second largest value
expressionQ = "maxnum([ !NE_Mean!, !SW_Mean!, !SE_Mean!, !NW_Mean!])"

codeblockQ = """
def maxnum(fields):
    fields.sort()
    return fields[-2]"""
 
# Check for quads that have 1 count. If the MaxQFetch  = the quad mean, then recalculate the MaxQFetch to use the second highest quad value
arcpy.management.MakeFeatureLayer(quadAnalyPntsA, "quadAnalysisLayerC")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerC", "NEW_SELECTION", "SE_Count = 1", "")
arcpy.management.CalculateField("quadAnalysisLayerC", "QuadCnt1", "\"SE\"", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerC", "SUBSET_SELECTION", "ROUND (SE_Mean, 4) =  ROUND (MaxQFetch, 4)", "")
arcpy.management.CalculateField("quadAnalysisLayerC", "OneIsMax", "\"Use second highest quad fetch\"", "PYTHON3")
arcpy.management.CalculateField("quadAnalysisLayerC", "MaxQFetch", expressionQ, "PYTHON3", codeblockQ)

arcpy.management.SelectLayerByAttribute("quadAnalysisLayerC", "NEW_SELECTION", "SW_Count = 1", "")
arcpy.management.CalculateField("quadAnalysisLayerC", "QuadCnt1", "\"SW\"", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerC", "SUBSET_SELECTION", "ROUND (SW_Mean, 4) =  ROUND (MaxQFetch, 4)", "")
arcpy.management.CalculateField("quadAnalysisLayerC", "OneIsMax", "\"Use second highest quad fetch\"", "PYTHON3")
arcpy.management.CalculateField("quadAnalysisLayerC", "MaxQFetch", expressionQ, "PYTHON3", codeblockQ)

arcpy.management.SelectLayerByAttribute("quadAnalysisLayerC", "NEW_SELECTION", "NE_Count = 1", "")
arcpy.management.CalculateField("quadAnalysisLayerC", "QuadCnt1", "\"NE\"", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerC", "SUBSET_SELECTION", "ROUND (NE_Mean, 4) =  ROUND (MaxQFetch, 4)", "")
arcpy.management.CalculateField("quadAnalysisLayerC", "OneIsMax", "\"Use second highest quad fetch\"", "PYTHON3")
arcpy.management.CalculateField("quadAnalysisLayerC", "MaxQFetch", expressionQ, "PYTHON3", codeblockQ)

arcpy.management.SelectLayerByAttribute("quadAnalysisLayerC", "NEW_SELECTION", "NW_Count = 1", "")
arcpy.management.CalculateField("quadAnalysisLayerC", "QuadCnt1", "\"NW\"", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerC", "SUBSET_SELECTION", "ROUND (NW_Mean, 4) =  ROUND (MaxQFetch, 4)", "")
arcpy.management.CalculateField("quadAnalysisLayerC", "OneIsMax", "\"Use second highest quad fetch\"", "PYTHON3")
arcpy.management.CalculateField("quadAnalysisLayerC", "MaxQFetch", expressionQ, "PYTHON3", codeblockQ)

# Recalculate the maxQuad direction and maxQuad exposure classification
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerC", "NEW_SELECTION", "ROUND (NE_Mean, 4) =  ROUND (MaxQFetch, 4)", "")
arcpy.management.CalculateField("quadAnalysisLayerC", "MaxQuadDir", "\"NE\"", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerC", "NEW_SELECTION", "ROUND (SW_Mean, 4) =  ROUND (MaxQFetch, 4)", "")
arcpy.management.CalculateField("quadAnalysisLayerC", "MaxQuadDir", "\"SW\"", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerC", "NEW_SELECTION", "ROUND (SE_Mean, 4) =  ROUND (MaxQFetch, 4)", "")
arcpy.management.CalculateField("quadAnalysisLayerC", "MaxQuadDir", "\"SE\"", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerC", "NEW_SELECTION", "ROUND (NW_Mean, 4) =  ROUND (MaxQFetch, 4)", "")
arcpy.management.CalculateField("quadAnalysisLayerC", "MaxQuadDir", "\"NW\"", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerC", "NEW_SELECTION", "MaxQFetch >= 804.67 AND MaxQFetch < 3218.69", "")
arcpy.management.CalculateField("quadAnalysisLayerC", "MxQExpCode", "\"moderate\"", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerC", "NEW_SELECTION", "MaxQFetch >= 3218.69", "")
arcpy.management.CalculateField("quadAnalysisLayerC", "MxQExpCode", "\"high\"", "PYTHON3")
arcpy.management.SelectLayerByAttribute("quadAnalysisLayerC", "NEW_SELECTION", "MaxQFetch < 804.67", "")
arcpy.management.CalculateField("quadAnalysisLayerC", "MxQExpCode", "\"low\"", "PYTHON3")

arcpy.management.SelectLayerByAttribute("quadAnalysisLayerC", "CLEAR_SELECTION", "", "")

finalPtName = name + "_fetch_withQuadAnalysis_points_" + date + "_Final"
arcpy.analysis.Select("quadAnalysisLayerC", finalPtName, "")

finalArcName = name + "_fetch_withQuadAnalysis_arcs_" + date + "_Final"
arcpy.analysis.Select(exposureArcs, finalArcName, "")

# Join attributes from the final exposure points file to the final exposure arcs file
arcpy.management.JoinField(finalArcName, "splitID", finalPtName, "splitID", ["NE_Count", "NW_Count", "SE_Count", "SW_Count", "NE_Mean", "NW_Mean", "SE_Mean", "SW_Mean", "MaxQFetch", "MxQExpCode", "MaxQuadDir", "QuadCnt1", "OneIsMax", "MxQFetchOld", "MxQExpCodeO", "MaxQDirO"])

# Return Output files
arcpy.SetParameterAsText(5, finalPtName)
arcpy.SetParameterAsText(6, finalArcName)

# clean up some files
arcpy.Delete_management(quadAnalyPntsA)
arcpy.Delete_management(waterArcsStats)
arcpy.Delete_management(maxWtrArcs)
arcpy.Delete_management(wtrPTSumStat)
arcpy.Delete_management(exposureArcs)
arcpy.Delete_management(exposurePoints)
arcpy.Delete_management(WtrArcsPT)

# script completed message
arcpy.AddMessage("Script complete")