# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 12:05:56 2016

@author: peter
"""
import slamby_sdk
from slamby_sdk.rest import ApiException
from TestDataset import TestDataset
import uuid

class TestDocument:
    def __init__(self):
        self.serverUrl = ""
        self.secret = ""
        self.datasetName = ""
        self.datasetInstance = ""
        self.singleDocumentCreationIterationNumber = 5
        self.testDocumentIds = []
        
    # Test Method
    def Start(self):
        self.datasetInstance = TestDataset()
        self.datasetInstance.serverUrl = self.serverUrl
        self.datasetInstance.secret = self.secret
        self.datasetInstance.Start()
        # Set test document ids
        for step in range(0,self.singleDocumentCreationIterationNumber):
            self.testDocumentIds.append(str(uuid.uuid4()))
            
        self.createSingleDocuments()
        
        return True
            
    # Test Method
    def Stop(self):
        client = slamby_sdk.ApiClient(self.serverUrl)
        client.set_default_header("Authorization", "Slamby {0}".format(self.secret))
        client.set_default_header("X-DataSet", self.datasetInstance.datasetName);
        
        for documentId in self.testDocumentIds:
            try:
                slamby_sdk.DocumentApi(client).delete_document(id=documentId)
                print("Document {0} removed".format(documentId))
            except ApiException as e:
                print(e)
                return False
                
        self.datasetInstance.Stop()
        return True
        
    def createSingleDocuments(self):
        client = slamby_sdk.ApiClient(self.serverUrl)
        client.set_default_header("Authorization", "Slamby {0}".format(self.secret))
        client.set_default_header("X-DataSet", self.datasetInstance.datasetName);

        for documentId in self.testDocumentIds:
            tmp_document = {
                "id": documentId,
                "title": "Example Product Title",
                "desc": "Example Product Description",
                "tag": [1,2,3]
            }        
            
            try:
                slamby_sdk.DocumentApi(client).create_document(document=tmp_document)
                print("Document {0} added".format(documentId))                    
            except ApiException as e:
                print(e)
                return False
            
        return True
        
    def _getDocument(self):
        client = slamby_sdk.ApiClient(self.serverUrl)
        client.set_default_header("Authorization", "Slamby {0}".format(self.secret))
        client.set_default_header("X-DataSet", self.datasetInstance.datasetName);
        
        for documentId in self.testDocumentIds:
            try:
                document = slamby_sdk.DocumentApi(client).get_document(documentId)
                print(document)
            except ApiException as e:
                print(e)
                return False        
        return True
        
    def _updateDocument(self):
        client = slamby_sdk.ApiClient(self.serverUrl)
        client.set_default_header("Authorization", "Slamby {0}".format(self.secret))
        client.set_default_header("X-DataSet", self.datasetInstance.datasetName);
        
        for documentId in self.testDocumentIds:
            try:
                slamby_sdk.DocumentApi(client).update_document(id=documentId,document={"title":"Updated title"})
                print("Updated {0}".format(documentId))
            except ApiException as e:
                print(e)
                return False
        return True
        
    def _getSampleByPercentage(self):
        client = slamby_sdk.ApiClient(self.serverUrl)
        client.set_default_header("Authorization", "Slamby {0}".format(self.secret))
        client.set_default_header("X-DataSet", self.datasetInstance.datasetName);

        settings = {
            "Id" : str(uuid.uuid4()),
            "Percent" : "10",
            "Size" : "0",
            "TagIds" : [],
            "Fields": ["*"]
        }
        
        try:
            slamby_sdk.DocumentApi(client).get_sample_documents(sample_settings=settings)
        except ApiException as e:
            print(e)
            return False
            
        return True
        
    def _getSampleByFixNumber(self):
        client = slamby_sdk.ApiClient(self.serverUrl)
        client.set_default_header("Authorization", "Slamby {0}".format(self.secret))
        client.set_default_header("X-DataSet", self.datasetInstance.datasetName);

        settings = {
            "Id" : str(uuid.uuid4()),
            "Percent" : "0",
            "Size" : "100",
            "TagIds" : [],
            "Fields": ["*"]
        }
        
        try:
            slamby_sdk.DocumentApi(client).get_sample_documents(sample_settings=settings)
        except ApiException as e:
            print(e)
            return False
            
        return True
            
#test = TestDocument()
#test.serverUrl = "https://europe.slamby.com/demo/"
#test.secret = "s3cr3t"
#test.Start()
#test._removeSingleDocument()
#test.Stop()