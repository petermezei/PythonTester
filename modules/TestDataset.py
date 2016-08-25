# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 12:05:56 2016

@author: peter
"""

import time
import slamby_sdk
from slamby_sdk.rest import ApiException

class TestDataset:
    def __init__(self):
        self.serverUrl = ""
        self.secret = ""
        self.datasetName = "hello"
        self.renameIteration = 5
        
    # Test Method
    def Start(self):
        client = slamby_sdk.ApiClient(self.serverUrl)
        client.set_default_header("Authorization", "Slamby {0}".format(self.secret))
        
        current_time = int(round(time.time(),0))
        self.datasetName = "test_dataset_{0}".format(current_time)

        dataset_template = {
            "IdField": "id",
            "InterpretedFields": ["title", "desc"],
            "Name": self.datasetName,
            "NGramCount": "3",
            "TagField": "tag",
            "SampleDocument": {
                "id": 9,
                "title": "Example Product Title",
                "desc": "Example Product Description",
                "tag": [1,2,3]
            }
        }
        
        try:
            slamby_sdk.DataSetApi(client).create_data_set(data_set=dataset_template)
            print("Created dataset: {0}".format(self.datasetName))
            return True
        except ApiException as e:
            print(e)
            return False
            
    # Test Method
    def Stop(self):
        client = slamby_sdk.ApiClient(self.serverUrl)
        client.set_default_header("Authorization", "Slamby {0}".format(self.secret))
        
        try:
            slamby_sdk.DataSetApi(client).delete_data_set(name=self.datasetName)
            print("Removed dataset: {0}".format(self.datasetName))
            return True
        except ApiException as e:
            print(e)
            return False
        
    def _listAllDataset(self):
        client = slamby_sdk.ApiClient(self.serverUrl)
        client.set_default_header("Authorization", "Slamby {0}".format(self.secret))
        
        try:
            datasets = slamby_sdk.DataSetApi(client).get_data_sets()
            print(datasets)
            return True
        except ApiException as e:
            print(e)
            return False
        
    def _renameDataset(self):
        client = slamby_sdk.ApiClient(self.serverUrl)
        client.set_default_header("Authorization", "Slamby {0}".format(self.secret))

        targetName = self.datasetName
        testName = "{0}_renamed".format(self.datasetName)

        for iteration in range(0,self.renameIteration):
            try:
                slamby_sdk.DataSetApi(client).update_data_set(name=targetName,data_set_update={"name":testName})
                print("rename ok: {0}".format(self.datasetName))
                
                try:
                    slamby_sdk.DataSetApi(client).update_data_set(name=testName,data_set_update={"name":targetName})
                    print("rename back ok: {0}".format(self.datasetName))
                except ApiException as e:
                    print(e)
                    return false
                
            except ApiException as e:
                print(e)
                return False
        
        return True

    def _getDataset(self):
        client = slamby_sdk.ApiClient(self.serverUrl)
        client.set_default_header("Authorization", "Slamby {0}".format(self.secret))
        
        try:
            datasetDetails = slamby_sdk.DataSetApi(client).get_data_set(name=self.datasetName)
            print("Get dataset {0}: {1}".format(self.datasetName,datasetDetails))
            return True
        except ApiException as e:
            print(e)
            return False
            
#test = TestDataset()
#test.serverUrl = "https://europe.slamby.com/demo/"
#test.secret = "s3cr3t"
#test.datasetName = "peti-test-99-hektor"
#test.StartCreateDataset()
#test._GetDataset()
#test._RenameDataset()
#test._ListAllDataset()
#test._RenameDataset()
#test.StopDeleteDataset()