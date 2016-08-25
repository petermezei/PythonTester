# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 12:05:56 2016

@author: peter
"""
import slamby_sdk
from slamby_sdk.rest import ApiException

class TestStatus:
    def __init__(self):
        self.serverUrl = ""
        self.secret = ""
        self.iterationNumber = 3
        
    # Test Method
    def Start(self):
        return True
            
    # Test Method
    def Stop(self):
        return True
        
    def _getStatus(self):
        client = slamby_sdk.ApiClient(self.serverUrl)
        client.set_default_header("Authorization", "Slamby {0}".format(self.secret))
        
        for iteration in range(0,int(self.iterationNumber)):
            try:
                status = slamby_sdk.StatusApi(client).get_status()
                print(status)
            except ApiException as e:
                print(e)
                return False
                
        return True
            
#test = TestStatus()
#test.serverUrl = "https://europe.slamby.com/demo/"
#test.secret = "s3cr3t"
#test.StartCreateDataset()
#test._getStatus()
#test.StopDeleteDataset()