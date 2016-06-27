#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xmlrpc.client
import requests
import json
import os

testproject_name = os.getenv("testproject_name") or "桌面版系统升级测试"
testplan_name    = os.getenv("testplan_name")    or None
TESTLINKAPIKEY = os.getenv("TESTLINKAPIKEY") or None
SERVER_URL_ENV = os.getenv("SERVER_URL") or None
review_id = None

def get_reviewIdTopic(id):
    review_id = os.environ.get('REVIEW_ID') or None
    host = os.environ.get('HOST_API') or None
    rr_token = os.environ.get('RR_TOKEN') or None
    if None == review_id or None == host or None == rr_token:
        return None
    headers = {"Access-Token":rr_token}
    review_path = "review"
    url_review = "/".join((host, review_path, review_id))
    data_response = requests.get(url_review, headers=headers)
    jsondata = json.loads(data_response.text)
    review_topic = ''
    try:
        review_topic = review_id + ' ' + jsondata["result"]["topic"]
    except Exception:
        print("Got keyError Exception jsondata['result']['topic']")
        return None
    return review_topic



if None == testplan_name:
    testplan_name = get_reviewIdTopic(review_id)

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
jsondata["project"] = {}
jsondata["testplan"] = {}

def isExist(testproject_name):
    projectsdata = client.getProjects()
    for project in projectsdata:
        if testproject_name == project["name"]:
            print(project)
            jsondata["project"]["id"] = project["id"]
            jsondata["project"]["name"] = project["name"]
            return True
    print("Can't find the project: %s" % testproject_name)
    return False

def createTestPlan(testproject_name, testplan_name):
    args = {}
    args["testprojectname"] = testproject_name
    args["testplanname"] = testplan_name
    plandata = client.getPlaninfo(args)
    print(plandata)
    if "id" in plandata[0].keys():
        jsondata["testplan"]["id"] = plandata[0]["id"]
        jsondata["testplan"]["name"] = plandata[0]["name"]
        return True
    else:
        print("Create test plan: %s" % testplan_name)
        returndata = client.createTestPlan(args)
        print(returndata)
        if "id" in returndata[0].keys():
            jsondata["testplan"]["id"] = returndata[0]["id"]
            jsondata["testplan"]["name"] = testplan_name
            print("Create test plan ok!")
            return True
        else:
            return False

if not isExist(testproject_name):
    exit(1)

if not createTestPlan(testproject_name, testplan_name):
    exit(1)
else:
    print(jsondata)
    jsonstr = json.dumps(jsondata, sort_keys=True, indent=4)
    with open("testlink.json", "w") as f:
        f.write(jsonstr)
        f.close()
