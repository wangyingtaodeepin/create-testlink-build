#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xmlrpc.client
import datetime
import requests
import json
import os

from mysql import getProjectAllSuite

testproject_name = os.getenv("testproject_name") or "桌面版系统升级测试"
testplan_name    = os.getenv("testplan_name")    or None
TESTLINKAPIKEY = os.getenv("TESTLINKAPIKEY") or None
SERVER_URL_ENV = os.getenv("SERVER_URL") or None
DEEPINRRAPIKEY = os.getenv("DEEPINRRAPIKEY") or None
keywords = os.getenv("keywords") or None

host      = os.getenv("HOST_API") or None
review_id = os.getenv("REVIEW_ID") or None
review_path = "review"
patch_path = "review"
buildname = os.getenv("version_flag_name") or None
rr_token = os.getenv("RR_TOKEN") or None
headers = {"Access-Token": rr_token}

def get_reviewIdTopic(id):
    rr_token = os.environ.get('RR_TOKEN') or None
    if None == review_id or None == host or None == rr_token:
        return None
    url_review = "/".join((host, review_path, review_id))
    data_response = requests.get(url_review, headers=headers)
    jsondata = json.loads(data_response.text)
    review_topic = ''
    try:
        review_topic = review_id + ' ' + jsondata["result"]["topic"]
        buildname = timestamp2datetime(jsondata["result"]["submit_timestamp"])
    except Exception:
        print("Got keyError Exception jsondata['result']['topic']")
        return None
    return {"topic": review_topic, "name": buildname}

def timestamp2datetime(timestamp, convert_to_local=False):
    if isinstance(timestamp, int):
        dt = datetime.datetime.utcfromtimestamp(timestamp)
        if convert_to_local: # 是否转化为本地时间
            dt = dt + datetime.timedelta(hours=8) # 中国默认时区
        return dt
    return timestamp

if None == testplan_name:
    data = get_reviewIdTopic(review_id)
    print(data)
    testplan_name = data["topic"]
    buildname = data["name"]

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

    def createBuild(self, dictargs):
        dictargs["devKey"] = self.devKey
        return self.server.tl.createBuild(dictargs)

    def addTestCaseToTestPlan(self, dictargs):
        dictargs["devKey"] = self.devKey
        return self.server.tl.addTestCaseToTestPlan(dictargs)

    def getTestSuitesForTestPlan(self, dictargs):
        dictargs["devKey"] = self.devKey
        return self.server.tl.getTestSuitesForTestPlan(dictargs)

    def getTestCasesForTestSuite(self, dictargs):
        dictargs["devKey"] = self.devKey
        return self.server.tl.getTestCasesForTestSuite(dictargs)

    def assignTestCaseExecutionTask(self, dictargs):
        dictargs["devKey"] = self.devKey
        return self.server.tl.assignTestCaseExecutionTask(dictargs)

# substitute your Dev Key Here
client = TestlinkAPIClient(TESTLINKAPIKEY)

jsondata = {}
jsondata["project"] = {}
jsondata["testplan"] = {}
jsondata["build"] = {}

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

def getTestCasesForProject(testproject_id, testplan_id, testbuild_id):
    tuple_suiteid = getProjectAllSuite()
    if tuple_suiteid == None:
        return None

    print(tuple_suiteid)

    keywordlist = keywords.split(';')
    print(keywordlist)
    pkglist = getPkgsName()
    print(pkglist)

    if keywordlist != None:
        allkeywords = keywordlist + pkglist
    else:
        allkeywords = pkglist

    for suiteid in tuple_suiteid:
        args_suite = {}
        args_suite["testsuiteid"] = suiteid
        args_suite["details"] = "full"
        args_suite["getkeywords"] = "true"
        allcasedetails = client.getTestCasesForTestSuite(args_suite)
        for row in allcasedetails:
            if "keywords" in row:
                for keyid in row["keywords"].keys():
                    if row["keywords"][keyid]["keyword"] in keywordlist:
                        for key in row.keys():
                            print(key + "\t:\t" + str(row[key]))

                        args_case = {}
                        args_case["testprojectid"] = testproject_id
                        args_case["testplanid"] = testplan_id
                        args_case["testcaseexternalid"] = row["external_id"]
                        args_case["version"] = int(row["version"])
                        print(client.addTestCaseToTestPlan(args_case))
                        args_assign = {}
                        args_assign["testplanid"] = testplan_id
                        args_assign["testcaseexternalid"] = row["external_id"]
                        args_assign["buildid"] = testbuild_id
                        args_assign["user"] = "zhaofangfang"
                        print(client.assignTestCaseExecutionTask(args_assign))
                        print("-" * 80)

        print("-" * 80)

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
        return False

def createBuild(testplanid, buildname):
    args = {}
    args["testplanid"] = testplanid
    args["buildname"] = buildname
    builddata = client.createBuild(args)
    print(builddata)
    if 'id' in builddata[0].keys():
        jsondata["build"]["id"] = builddata[0]["id"]
        jsondata["build"]["name"] = buildname
        return True
    return False

def patchReview(tl_test_plan, tl_build_id, tl_test_plan_id):
    print("In function patchReview:")
    print(tl_test_plan)
    print(tl_build_id)
    print(tl_test_plan_id)
    url_patch = "/".join((host, patch_path, review_id))
    data_patch = {"tl_test_plan": tl_test_plan,
                  "tl_build_id": tl_build_id,
                  "tl_test_plan_id": tl_test_plan_id}
    returndata = requests.patch(url_patch, data=data_patch, headers=headers)
    if returndata.status_code == 200:
        return True
    else:
        return False

def getRpaUrl():
    url_review = "/".join((host, review_path, review_id))
    url_info = requests.get(url_review, headers=headers)
    rpa_url = url_info.json()['result']['rpa']
    return rpa_url

def getdatajson():
    rpa_url = getRpaUrl()
    json_url = rpa_url + '/checkupdate/data.json'
    url_info = requests.get(json_url, headers=headers)
    datajson = url_info.json()
    return datajson

def getPkgsName():
    packages_names = []
    datajson = getdatajson()
    for data in datajson:
        packages_names.append(data["name"])
    return packages_names

def main():
    if not isExist(testproject_name):
        exit(1)

    if not createTestPlan(testproject_name, testplan_name):
        exit(1)
    else:
        print(buildname)
        if createBuild(jsondata["testplan"]["id"], str(buildname).split()[0]):
            print("Create build version ok.")
            getTestCasesForProject(jsondata["project"]["id"], jsondata["testplan"]["id"], jsondata["build"]["id"])
            testplanurl = 'https://testlink.deepin.io/lnl.php?apikey=%s&tproject_id=%s&tplan_id=%s&type=test_report' \
                          % (DEEPINRRAPIKEY, jsondata['project']['id'], jsondata['testplan']['id'])
            print(testplanurl)
            if patchReview(testplanurl, str(jsondata["build"]["id"]), str(jsondata["testplan"]["id"])):
                print("Update review ok.")
            else:
                print("Update review fail.")
        else:
            print("Create build version fail")

        print(jsondata)
        jsonstr = json.dumps(jsondata, sort_keys=True, indent=4)
        with open("testlink.json", "w") as f:
            f.write(jsonstr)
            f.close()

if __name__ == "__main__":
    main()
