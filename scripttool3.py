###################################################
#Date: 21 May 2020
#References: Penn State University: World Campus
# GEOG 489, Lesson 1
# https://www.e-education.psu.edu/geog489/node/2293
#ArcGIS Pro Project - Data management
# https://pro.arcgis.com/en/PRO-APP/TOOL-REFERENCE/DATA-MANAGEMENT/project.htm
#ArcGIS Pro Clip Clip_analysis
# https://pro.arcgis.com/en/pro-app/tool-reference/analysis/clip.htm
####################################################
import time
start_time = time.time()
import os, sys
import arcpy
import multiprocessing
from multicode3 import worker

workspace = arcpy.GetParameterAsText(0)
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True

# Input parameters
clipper = arcpy.GetParameterAsText(1)
tobeclipped = arcpy.GetParameterAsText(2)
outputFolder = arcpy.GetParameterAsText(3)
tobeclippedList = tobeclipped.split(";")

def get_install_path():
    if sys.maxsize > 2**32: return sys.exec_prefix #We're running in a 64bit process

    #We're 32 bit so see if there's a 64bit install
    path = r'SOFTWARE\Python\PythonCore\2.7'

    from _winreg import OpenKey, QueryValue
    from _winreg import HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_64KEY

    try:
        with OpenKey(HKEY_LOCAL_MACHINE, path, 0, KEY_READ | KEY_WOW64_64KEY) as key:
            return QueryValue(key, "InstallPath").strip(os.sep) #We have a 64bit install, so return that.
    except: return sys.exec_prefix #No 64bit, so return 32bit path

def mp_handler():

    try:

        arcpy.AddMessage("Creating Polygon OID list...")
        clipperDescObj = arcpy.Describe(clipper)
        field = clipperDescObj.OIDFieldName

        idList = []
        with arcpy.da.SearchCursor(clipper, [field]) as cursor:
            for row in cursor:
                id = row[0]
                idList.append(id)

        arcpy.AddMessage("There are " + str(len(idList)) + " object IDs (polygons) to process.")
        print("There are " + str(len(idList)) + " object IDs (polygons) to process.")

        jobs = []

        for id in idList:
            for fc in tobeclippedList:
                jobs.append((clipper,outputFolder,fc,field,id, workspace))
        arcpy.AddMessage("Job list has " + str(len(jobs)) + " elements.")
        print("Job list has " + str(len(jobs)) + " elements.")

        # Create and run multiprocessing pool.
        multiprocessing.set_executable(os.path.join(get_install_path(), 'pythonw.exe'))

        arcpy.AddMessage("Sending to pool")
        print("Sending to pool")

        cpuNum = multiprocessing.cpu_count()  # determine number of cores to use
        arcpy.AddMessage("there are: " + str(cpuNum) + " cpu cores on this machine")
        print("there are: " + str(cpuNum) + " cpu cores on this machine")

        with multiprocessing.Pool(processes=cpuNum) as pool:
            res = pool.starmap(worker, jobs)

        # If an error has occurred report it
        failed = res.count(False)
        if failed > 0:
            arcpy.AddError("{} workers failed!".format(failed))
            print("{} workers failed!".format(failed))

        arcpy.AddMessage("Finished multiprocessing!")
        print("Finished multiprocessing!")

    except arcpy.ExecuteError:
        # Geoprocessor threw an error
        arcpy.AddError(arcpy.GetMessages(2))
        print("Execute Error:", arcpy.ExecuteError)
    except Exception as e:
        # Capture all other errors
        arcpy.AddError(str(e))
        print("Exception:", e)

if __name__ == '__main__':
    mp_handler()
    #Implement and run simple code profiling using the time module
    arcpy.AddMessage("--- %s seconds ---" % (time.time() - start_time))
    print("--- %s seconds ---" % (time.time() - start_time))
