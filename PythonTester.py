# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 20:49:00 2016

@author: peter
"""

import os
import importlib
import sys, getopt
import json

#### Settings

## Init Settings

# Available modules in modules folder
testModules = []
# Available functions in modules
testFunctions = {}

## Settings Creation

# Extra variables injection into modul variable list
commonVariables = {
    "Arg":[],
    "ModuleIteration":1,
    "FunctionIteration":1
}
# Available settings available in modules
settings = {
    "common":{
        "serverUrl":"https://europe.slamby.com/demo/",
        "secret":"s3cr3t"
    },
    "moduleSettings":{}
}

## Test Plan Creation

# Custom settings read from custom settings file. -p
customSettings = {}
# Test Plan Container
testPlan = {}

## Test

# Test Instances
testInstances = {}
# Test Data
test = {
    "stat":{},
    "result":[]
}

## ---------------------
## Helpers
## ---------------------

# Helper
def loadClass(module):
    return getattr(importlib.import_module("modules.{0}".format(module)), module)        

# Helper
def exportToJson(fileName,content):
    if not os.path.exists(os.path.dirname(fileName)):
        try:
            os.makedirs(os.path.dirname(fileName))
        except OSError as e: # Guard against race condition
            print(e)
    with open(fileName,"w") as outfile:
        json.dump(content,outfile,sort_keys = True, indent = 4)
        
# Helper
def importJson(fileName):
    with open(fileName) as setting_file:    
        return json.load(setting_file)

## ---------------------
## Init
## ---------------------

# Detecting modules in modules folder
modules = os.listdir("./{0}".format("modules/"))
for module in modules:
    if module.endswith(".py") and module != "__init__.py":
        testModules.append("{0}".format(os.path.splitext(module)[0]))
    
# Detecting functions in available modules
# Create settings template file
for module in testModules:
    if module not in settings.keys():
        settings["moduleSettings"][module] = {}
        testFunctions[module] = []
    clss = loadClass(module)()
    for item in dir(clss):
        if item[0] == "_" and item[1] is not "_":
            testFunctions[module].append(item)
    settings["moduleSettings"][module] = vars(clss)
    for commonVariable in commonVariables.keys():
        if commonVariable not in settings["moduleSettings"][module].keys():
            settings["moduleSettings"][module][commonVariable] = commonVariables[commonVariable]

# Create Test Plan from settings file
def testPlanner():
    global testFunctions
    for module in customSettings["moduleSettings"]:
        moduleInstanceNumber = len(customSettings["moduleSettings"][module]["Arg"]) if len(customSettings["moduleSettings"][module]["Arg"]) > 0 else 1
        moduleIteration = customSettings["moduleSettings"][module]["ModuleIteration"] if customSettings["moduleSettings"][module]["ModuleIteration"] > 0 else 1
        functionIteration = customSettings["moduleSettings"][module]["FunctionIteration"] if customSettings["moduleSettings"][module]["FunctionIteration"] > 0 else 1
        
        for instanceArgNumber in range(0,moduleInstanceNumber):
            if moduleIteration > 1:
                for moduleIterationNumber in range(0,moduleIteration):
                    instanceName = "{0}_{1}_{2}".format(module,instanceArgNumber,moduleIterationNumber)
                    if instanceName not in testPlan.keys():
                        testPlan[instanceName] = {"settings":customSettings["moduleSettings"][module],"actions":[],"moduleName":module}
                    if len(testPlan[instanceName]["actions"]) == 0:
                        testPlan[instanceName]["actions"].append({"action":"Start","result":{}})
                    for functionIterationNumber in range(0,functionIteration):
                        for function in testFunctions[module]:
                            testPlan[instanceName]["actions"].append({"action":function,"result":{}})
                    testPlan[instanceName]["actions"].append({"action":"Stop","result":{}})
                    # Check for common settings options
                    for setting in testPlan[instanceName]["settings"]:
                        if testPlan[instanceName]["settings"][setting] == "":
                            if setting in customSettings["common"].keys():
                                testPlan[instanceName]["settings"][setting] = customSettings["common"][setting]
            else:
                instanceName = "{0}_{1}_{2}".format(module,instanceArgNumber,0)
                if instanceName not in testPlan.keys():
                    testPlan[instanceName] = {"settings":customSettings["moduleSettings"][module],"actions":[],"moduleName":module}
                if len(testPlan[instanceName]["actions"]) == 0:
                    testPlan[instanceName]["actions"].append({"action":"Start","result":{}})
                for functionIterationNumber in range(0,functionIteration):
                    for function in testFunctions[module]:
                        testPlan[instanceName]["actions"].append({"action":function,"result":{}})
                testPlan[instanceName]["actions"].append({"action":"Stop","result":{}})
                # Check for common settings options
                for setting in testPlan[instanceName]["settings"]:
                    if testPlan[instanceName]["settings"][setting] == "":
                        if setting in customSettings["common"].keys():
                            testPlan[instanceName]["settings"][setting] = customSettings["common"][setting]

# Tester Method
def tester(testPlan):
    global testInstances
    #Instance Creation
    for instanceName in testPlan:
        # Create Instances
        testInstances[instanceName] = loadClass(testPlan[instanceName]["moduleName"])()
        # Settings auto loading
        for variable in testPlan[instanceName]["settings"]:
            # if variable exists in Instance Class
            instanceVariables = vars(testInstances[instanceName])
            if variable in instanceVariables.keys():
                setattr(testInstances[instanceName],variable,testPlan[instanceName]["settings"][variable])

    for instanceName in testPlan:
        print(vars(testInstances[instanceName]))
        for item in testPlan[instanceName]["actions"]:           
            getattr(testInstances[instanceName],item["action"])()

## ---------------------
## Console Level
## ---------------------

def main(argv):
    global customSettings
    faq = '''
    python PythonTester.py
    -h (print help message)
    -s <SettingsFileName> (generate settings template)
    -p <SettingsFileName> (generate test plan from settings file)
    -t <TestPlanFileName>
    '''
    try:
        opts, args = getopt.getopt(argv,"hi:s:p:t:",["i=","s=","p=","t="])
    except getopt.GetoptError:
        print (faq)
        sys.exit(2)

    # Manage available options
    for opt, arg in opts:
        if opt == '-h':
            print(faq)
            sys.exit()
        elif opt in ("-s", "--ofile"):
            fileName = "test_settings.json"
            if arg is not "":
                fileName = arg
            exportToJson(fileName,settings)
        elif opt in ("-p", "--ofile"):
            customSettings = importJson(arg)
            testPlanner()
            exportToJson("{0}/plan.json".format(os.path.dirname(arg)),testPlan)
        elif opt in ("-t", "--ofile"):
            customTestPlan = importJson(arg)
            tester(customTestPlan)
                
if __name__ == "__main__":
   main(sys.argv[1:])