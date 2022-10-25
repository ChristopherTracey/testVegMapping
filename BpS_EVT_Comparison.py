# -*- coding: utf-8 -*-
"""
BpS/EVT Comparision
"""
import arcpy, os
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("spatial") # Check out any necessary licenses.
arcpy.env.overwriteOutput = True

# test comment


def Model():  # Model
    StudyArea = "studyArea2"
    BpS = arcpy.Raster("BPSclip_CoastalPlain_new")
    EVT = arcpy.Raster("EVTclip_CoastalPlain_new")
    RemapTable = "RemapTable"

    arcpy.env.extent = StudyArea # Set the extent environment using a feature class
    arcpy.env.mask = StudyArea # Set Mask environment
    arcpy.env.cellSize = EVT # Set the cell size environment using a raster dataset.
    
    print("clipping the EVT")
    outEVT_ExtractByMask = ExtractByMask(EVT, StudyArea)
    outEVT_ExtractByMask.save("clipEVT")
    print("clipping the BpS")
    outBpS_ExtractByMask = ExtractByMask(BpS, StudyArea)
    outBpS_ExtractByMask.save("clipBpS1")

    print("buidling pyramids")
    arcpy.BatchBuildPyramids_management("clipEVT;clipBpS", "6", "SKIP_FIRST",
      "NEAREST", "JPEG", "50", "SKIP_EXISTING")

    print("comparing ecological system lists")
    # Set the output field properties for both FieldMap objects
    arcpy.TableToTable_conversion("clipEVT", r"S:\Projects\SGI_Southeastern_Grasslands_Initiative\SGI_ArcPro\tmp_comparisonToolDev.gdb", "clipEVT_table", '', 'Value "Value" false true false 4 Long 0 0,First,#,clipEVT,Value,-1,-1', '')
    arcpy.TableToTable_conversion("clipBpS", r"S:\Projects\SGI_Southeastern_Grasslands_Initiative\SGI_ArcPro\tmp_comparisonToolDev.gdb", "clipBpS_table", '', 'Value "Value" false true false 4 Long 0 0,First,#,clipBpS,Value,-1,-1', '')
    arcpy.management.JoinField("clipEVT_table", "Value", "clipBpS_table", "Value", "Value")
    arcpy.conversion.TableToTable("clipEVT_table", r"S:\Projects\SGI_Southeastern_Grasslands_Initiative\SGI_ArcPro\tmp_comparisonToolDev.gdb", "IterateValuesList", "Value_1 IS NOT NULL", 'Value_1 "Value" true true false 4 Long 0 0,First,#,clipEVT_table,Value_1,-1,-1', '')

    print("processing each ecological system")
    with arcpy.da.SearchCursor("IterateValuesList", "Value_1") as cursor:
        for row in cursor:
            print(row[0])
            # EVT
            print("- extracting the EVT")
            tmp_EVT_Value = fr"S:\Projects\SGI_Southeastern_Grasslands_Initiative\SGI_ArcPro\tmp_comparisonToolDev.gdb\tmp_EVT_{row[0]}"
            Extract_by_Attributes = tmp_EVT_Value
            tmp_EVT_Value = arcpy.sa.ExtractByAttributes(in_raster="clipEVT", where_clause=f"Value = {row[0]}")
            arcpy.management.CalculateField(tmp_EVT_Value, "sumValue", "1", "PYTHON3", '', "LONG", "NO_ENFORCE_DOMAINS")
            tmp_EVT_Value.save(Extract_by_Attributes)
            print("- reclassifying the EVT")
            tmp_EVT_reclass = fr"S:\\Projects\\SGI_Southeastern_Grasslands_Initiative\\SGI_ArcPro\\tmp_comparisonToolDev.gdb\\tmp_EVT_rec_{row[0]}"
            ReclassByTableEVT = tmp_EVT_reclass
            tmp_EVT_reclass = arcpy.sa.Reclassify(tmp_EVT_Value, "sumValue", "1 1;NODATA 0", "DATA")
            tmp_EVT_reclass.save(ReclassByTableEVT)
            
            #BpS
            print("- extracting the BpS")
            tmp_BpS_Value = fr"S:\Projects\SGI_Southeastern_Grasslands_Initiative\SGI_ArcPro\tmp_comparisonToolDev.gdb\tmp_BpS_{row[0]}"
            Extract_by_Attributes = tmp_BpS_Value
            tmp_BpS_Value = arcpy.sa.ExtractByAttributes(in_raster="clipBpS", where_clause=f"Value = {row[0]}")
            arcpy.management.CalculateField(tmp_BpS_Value, "sumValue", "2", "PYTHON3", '', "LONG", "NO_ENFORCE_DOMAINS")
            tmp_BpS_Value.save(Extract_by_Attributes)
            print("- reclassifying the BpS")
            tmp_BpS_reclass = fr"S:\\Projects\\SGI_Southeastern_Grasslands_Initiative\\SGI_ArcPro\\tmp_comparisonToolDev.gdb\\tmp_BpS_rec_{row[0]}"
            ReclassByTableBpS = tmp_BpS_reclass
            tmp_BpS_reclass = arcpy.sa.Reclassify(tmp_BpS_Value, "sumValue", "2 2;NODATA 0", "DATA")
            tmp_BpS_reclass.save(ReclassByTableBpS)

            # Combine
            print("- combining the BpS and EVT")
            tmp_combine = fr"S:\\Projects\\SGI_Southeastern_Grasslands_Initiative\\SGI_ArcPro\\tmp_comparisonToolDev.gdb\\tmp_combine_{row[0]}"
            Combine_EVTBpS = tmp_combine
            tmp_combine = Plus(ReclassByTableBpS, ReclassByTableEVT)
            tmp_combine.save(Combine_EVTBpS)

            # Delete intermediate files
            print("- combining the BpS and EVT")
            arcpy.Delete_management("Extract_by_Attributes;ReclassByTableEVT;ReclassByTableBpS")

if __name__ == '__main__':
    # Global Environment settings
    with arcpy.EnvManager(scratchWorkspace=r"S:\Projects\SGI_Southeastern_Grasslands_Initiative\SGI_ArcPro\tmp_comparisonToolDev.gdb",
                          workspace=r"S:\Projects\SGI_Southeastern_Grasslands_Initiative\SGI_ArcPro\tmp_comparisonToolDev.gdb"):
        Model()
