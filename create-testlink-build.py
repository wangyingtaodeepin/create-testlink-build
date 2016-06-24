#!/usr/bin/env python
# coding=utf-8

import xmlrpc.client
import json
import os

testproject_name = os.getenv("testproject_name") or None
testplan_name    = os.getenv("testplan_name")    or None
TESTLINKAPIKEY = os.getenv("TESTLINKAPIKEY") or None
SERVER_URL_ENV = os.getenv("SERVER_URL") or None

if None == testproject_name or None == testplan_name or None == TESTLINKAPIKEY or None == SERVER_URL_ENV:
    print("Can not get the value of the params: testproject_name or testplan_name")
    exit(1)

class TestlinkAPIClient:        
    # substitute your server URL Here
    SERVER_URL = SERVER_URL_ENV
      
    def __init__(self, devKey):
        self.server = xmlrpc.client.ServerProxy(self.SERVER_URL)
        self.devKey = devKey

    def getInfo(self):
        return self.server.tl.about()

    def getProjects(self):
        return self.server.tl.getProjects(dict(devKey=self.devKey))

    def getPlaninfo(self, dictargs):
        dictargs["devKey"] = self.devKey
        return self.server.tl.getTestPlanByName(dictargs)

    def getBuildsForTestPlan(self, dictargs):
        dictargs["devKey"] = self.devKey
        return self.server.tl.getBuildsForTestPlan(dictargs)

    def getTestcaseForTestPlan(self, dictargs):
        dictargs["devKey"] = self.devKey
        return self.server.tl.getTestCasesForTestPlan(dictargs)
        
    def getTestCaseIDByName(self, dictargs):
        dictargs["devKey"] = self.devKey
        return self.server.tl.getTestCaseIDByName(dictargs)

    def createTestPlan(self, dictargs):
        dictargs["devKey"] = self.devKey
        return self.server.tl.createTestPlan(dictargs)

    def addTestCaseToTestPlan(self, dictargs):
        dictargs["devKey"] = self.devKey
        return self.server.tl.addTestCaseToTestPlan(dictargs)

    def getTestSuitesForTestPlan(self, dictargs):
        dictargs["devKey"] = self.devKey
        return self.server.tl.getTestSuitesForTestPlan(dictargs)

# substitute your Dev Key Here
client = TestlinkAPIClient(TESTLINKAPIKEY)

jsondata = {}

def isExist(testproject_name):
    projectsdata = client.getProjects()
    print(projectsdata)
    return True


def createTestPlan(testproject_name, testplan_name):
    args = {}
    args["testprojectname"] = testproject_name
    args["testplanname"] = testplan_name
    plandata = client.getPlaninfo(args)
    print(plandata)

isExist(testproject_name)

#jsonstr = json.dumps(alldata, sort_keys=True, indent=4)
#with open('tcase_detail.json', "w") as f:
#    f.write(jsonstr)
#    f.close()
