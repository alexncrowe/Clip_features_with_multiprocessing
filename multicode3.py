import os, sys
import arcpy

def worker(clipper, outFolder, tobeclipped, field, oid, workspace):
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    try:

        query = '"' + field +'" = ' + str(oid)
        clipperFC = arcpy.MakeFeatureLayer_management(clipper, "clipper_" + str(oid), query)

        tobeclippedName = (tobeclipped.replace((workspace +"\\"), ""))
        clippedFC = outFolder + r"\clipped" + str(oid) + tobeclippedName + ".shp"
        arcpy.Clip_analysis(tobeclipped, clipperFC, clippedFC)

        # Determine if the input has a defined coordinate system, can't project it if it does not
        dsc = arcpy.Describe(clippedFC)

        if dsc.spatialReference.Name == "Unknown":
            print('skipped this fc due to undefined coordinate system: ' + clippedFC)
        else:

            # Determine the new output feature class path and name
            projectedFC = outFolder + r"\clipped" + str(oid) + tobeclippedName + "_projected.shp"

            # Set output coordinate system
            outCS = arcpy.SpatialReference('WGS 1984')

            # run project tool
            arcpy.Project_management(clippedFC, projectedFC, outCS)

            # check messages
            print(arcpy.GetMessages())

        print("finished clipping:", str(oid))
        return True # everything went well so we return True
    except:
        # Some error occurred so return False
        arcpy.GetMessages()
        print("error condition")
        return False
