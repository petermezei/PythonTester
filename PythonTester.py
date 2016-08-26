# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 20:49:00 2016

@author: peter
"""

import os
import importlib
import sys, getopt
import json
import csv
import random
import copy

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
randomTestPlan = []
## Test

# Test Instances
testInstances = {}
# Test Data
testResult = {
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
        
# Helper
def exportDictToCsv(fileName,dictionary):
    if not os.path.exists(os.path.dirname(fileName)):
        try:
            os.makedirs(os.path.dirname(fileName))
        except OSError as e: # Guard against race condition
            print(e)
    with open(fileName,"wb") as f:
        w = csv.DictWriter(f,dictionary[0].keys())
        w.writeheader()
        w.writerow(dictionary)
        
# Helper
def importJsonFromCsv(fileName):
    result = []
    with open(fileName,"rb") as csvfile:
        reader = csv.DictReader(csvfile)
        for item in reader:
            result.append(item)
    return result
        
# Helper
def exportListToCsv(fileName,content):
    if not os.path.exists(os.path.dirname(fileName)):
        try:
            os.makedirs(os.path.dirname(fileName))
        except OSError as e: # Guard against race condition
            print(e)
    with open(fileName,"wb") as f:
        w = csv.writer(f,quoting=csv.QUOTE_ALL)
        for row in content:
            m = []
            for item in row:
                if type(item) is dict and len(item) > 0:
                    m.append(json.dumps(item, separators=(',',':')))
                m.append(item)
            w.writerow(m)
            
# Helper
def readJsonFromString(string):
    return json.loads(string)

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
    global testPlan
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

    newPlan = {}
    for instanceName in testPlan:
        newPlan[instanceName] = copy.deepcopy(testPlan[instanceName])
        if len(newPlan[instanceName]["settings"]["Arg"]) > 0:
            a = testPlan[instanceName]["settings"]["Arg"][int(instanceName.split("_")[1])]
            newPlan[instanceName]["settings"]["Arg"] = a
    # Rewrite modified plan
    testPlan = newPlan
                            
# Randomizer
def randomTestGenerator():
    global testPlan
    # Random instance selection
    randomInstanceName = testPlan.keys()[random.randint(0,len(testPlan.keys())-1)]
    # If Start method still exists
    if testPlan[randomInstanceName]["actions"][0]["action"] == "Start":
        settings = testPlan[randomInstanceName]["settings"].copy()
        if len(testPlan[randomInstanceName]["settings"]["Arg"]) == 0:
            settings["Arg"] = ""
        addToRandomTestPlan(
            randomInstanceName,
            testPlan[randomInstanceName]["moduleName"],
            "Start",
            settings
        )
        del testPlan[randomInstanceName]["actions"][0]
    
    if len(testPlan[randomInstanceName]["actions"]) > 1:
        actionIndex = random.randint(0,len(testPlan[randomInstanceName]["actions"])-2)
    else:
        actionIndex = 0

    addToRandomTestPlan(
        randomInstanceName,
        testPlan[randomInstanceName]["moduleName"],
        testPlan[randomInstanceName]["actions"][actionIndex]["action"],
        {}
    )
    del testPlan[randomInstanceName]["actions"][actionIndex]
    
    if len(testPlan[randomInstanceName]["actions"]) == 0:
        del testPlan[randomInstanceName]

    if len(testPlan) > 0:
        randomTestGenerator()
    
def addToRandomTestPlan(instanceName,module,action,settings):
    global randomTestPlan
    if len(randomTestPlan) == 0:
        randomTestPlan.append(["InstanceName","Module","Action","Settings"])
    randomTestPlan.append([instanceName,module,action,settings])

def tester(fileName):
    global testInstances
    for testCase in importJsonFromCsv(fileName):
        # Create Instance if new test case start
        if testCase["Action"] == "Start":
            testInstances[testCase["InstanceName"]] = loadClass(testCase["Module"])()
            # Settings auto loading
            settings = readJsonFromString(testCase["Settings"])
            for variable in settings:
                # if variable exists in Instance Class
                instanceVariables = vars(testInstances[testCase["InstanceName"]])
                if variable in instanceVariables.keys():
                    setattr(testInstances[testCase["InstanceName"]],variable,settings[variable])
        test(testCase["InstanceName"],testInstances[testCase["InstanceName"]],testCase["Action"])

# Tester Method
def _tester(fileName):
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

    #for instanceName in testPlan:
    #    print(vars(testInstances[instanceName]))
    #    for item in testPlan[instanceName]["actions"]:           
    #        getattr(testInstances[instanceName],item["action"])()
    autoTester(testPlan)

def autoTester(testPlan):
    global testInstances
    # Random instance selection
    instance = testPlan.keys()[random.randint(0,len(testPlan.keys())-1)]
    # If Start method still exists
    if testPlan[instance]["actions"][0]["action"] == "Start":
        #getattr(testInstances[instance],"Start")()
        test(instance,testInstances[instance],"Start")
        del testPlan[instance]["actions"][0]
    
    if len(testPlan[instance]["actions"]) > 2:
        actionIndex = random.randint(0,len(testPlan[instance]["actions"])-2)
    else:
        actionIndex = 0
        test(instance,testInstances[instance],testPlan[instance]["actions"][actionIndex]["action"])
        
    del testPlan[instance]["actions"][actionIndex]
    if len(testPlan[instance]["actions"]) == 0:
        del testPlan[instance]
    if len(testPlan) > 0:
        autoTester(testPlan)
        
def test(instanceName,instance,action):
    log(
        instanceName,
        action,
        getattr(instance,action)()
    )
    
def log(instanceName,action,result):
    global testResult
    testResult["result"].append({
        "instance":instanceName,
        "action":action,
        "result":result
    })
    
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
            randomTestGenerator()
            exportListToCsv("{0}/plan.random.csv".format(os.path.dirname(arg)),randomTestPlan)
        elif opt in ("-t", "--ofile"):
            tester(arg)
                
if __name__ == "__main__":
   main(sys.argv[1:])