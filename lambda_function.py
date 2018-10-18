# TODO: add error handling
# TODO: add reconnection flow

import logging
import json
from botocore.vendored import requests


def lambda_handler(event, context):
    eventHandler = EventHandler()
    eventHandler.registerHandler("createListIntent", EventCreateList())
    eventHandler.registerHandler("addTaskIntent", EventAddTask())
    eventHandler.registerHandler("markTaskCompletedIntent", EventMarkTaskCompleted())
    eventHandler.registerHandler("deleteTaskIntent", EventDeleteTask())
    eventHandler.registerHandler("deleteListIntent", EventDeleteList())
    eventHandler.registerHandler("readTasksIntent", EventReadTasks())
    eventHandler.registerHandler("testIntent", EventTest())
    eventHandler.registerHandler("showAllListsIntent", EventShowAllLists())
    eventHandler.registerHandler("LaunchRequest", EventShowAllLists())

    return eventHandler.handleEvent(event)


class EventHandler:
    def __init__(self):
        self.handlers = {}

    def registerHandler(self, eventName, handler):
        self.handlers[eventName] = handler

    def handleEvent(self, event):
        if event['request']['type'] == "LaunchRequest":
            return self.handlers[event['request']['type']].execute(event)
        elif event['request']['type'] == "IntentRequest":
            return self.handlers[event['request']['intent']['name']].execute(event)


class Event:
    def execute(self, event):
        # logging.error(event)
        response = self.doExecute(event)
        return self.createResponse(response)

    def createResponse(self, responseText):
        return {
            'version': '1.0',
            'sessionAttributes': {},
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': responseText
                }
            }
        }

    def doExecute(self, event):
        return 0

    def makeGetRequest(self, path, params, event):
        req = requests.get(Event.baseURL + path,
                           params=params,
                           headers={
                               "X-Access-Token": event["context"]["System"]["user"]["accessToken"],
                               "X-Client-ID": "ee29112eeee47ea2179d"
                           })
        print(req)
        return req

    def makePostRequest(self, path, data, event):
        req = requests.post(Event.baseURL + path,
                            data=json.dumps(data),
                            headers={
                                "Content-Type": "application/json",
                                "X-Access-Token": event["context"]["System"]["user"]["accessToken"],
                                "X-Client-ID": "ee29112eeee47ea2179d"
                            })
        print(req)
        return req

    def makePatchRequest(self, path, data, event):
        req = requests.patch(Event.baseURL + path,
                             data=json.dumps(data),
                             headers={
                                 "Content-Type": "application/json",
                                 "X-Access-Token": event["context"]["System"]["user"]["accessToken"],
                                 "X-Client-ID": "ee29112eeee47ea2179d"
                             })
        print(req)
        return req

    def makeDeleteRequest(self, path, params, event):
        req = requests.delete(Event.baseURL + path,
                              params=params,
                              headers={
                                  "X-Access-Token": event["context"]["System"]["user"]["accessToken"],
                                  "X-Client-ID": "ee29112eeee47ea2179d"
                              })
        print(req)
        return req

    baseURL = "http://a.wunderlist.com/api/v1"


class EventCreateList(Event):
    def doExecute(self, event):
        listName = event["request"]["intent"]["slots"]["ListName"]["value"].lower()
        print("listName=" + listName)
        data = {
            "title": listName
        }
        response = self.makePostRequest(EventCreateList.path, data, event)
        logging.error("RESPONSE")
        logging.error(response.json())

        if response.status_code == EventCreateList.STATUS_CODE:
            return "I've created a new list called " + listName
        else:
            return "I couldn't create a list called " + listName

    path = "/lists"
    STATUS_CODE = 201


class EventAddTask(Event):
    def doExecute(self, event):
        getLists = self.makeGetRequest("/lists", {}, event)
        lists = getLists.json()
        logging.error(lists)

        listName = event["request"]["intent"]["slots"]["ListName"]["value"].lower()
        taskName = event["request"]["intent"]["slots"]["TaskName"]["value"].lower()
        listID = 0

        for listItem in lists:
            if listItem["title"].lower() == listName:
                listID = listItem["id"]

        if listID == 0:
            return "Could not find list " + listName

        print("listName=" + listName)
        data = {
            "list_id": listID,
            "title": taskName,
        }
        response = self.makePostRequest(EventAddTask.path, data, event)
        logging.error("RESPONSE")
        logging.error(listID)
        logging.error(response.json())

        if response.status_code == EventCreateList.STATUS_CODE:
            return taskName + " added to list, " + listName
        else:
            return "Failed to add task to " + listName

    path = "/tasks"
    STATUS_CODE = 200


class EventMarkTaskCompleted(Event):
    def doExecute(self, event):
        getLists = self.makeGetRequest("/lists", {}, event)
        lists = getLists.json()

        listName = event["request"]["intent"]["slots"]["ListName"]["value"].lower()
        taskName = event["request"]["intent"]["slots"]["TaskName"]["value"].lower()
        listID = 0
        revision = 0

        for listItem in lists:
            if listItem["title"].lower() == listName:
                listID = listItem["id"]

        if listID == 0:
            return "Could not find list"

        params = {
            "list_id": int(listID)
        }
        taskList = self.makeGetRequest("/tasks", params, event)
        logging.error(taskList.json())
        taskID = 0
        tasks = taskList.json()
        for task in tasks:
            if task['title'] == taskName:
                taskID = task['id']
                revision = task['revision']

        if taskID == 0:
            return "Could not find " + taskName + " in " + listName

        print("listName=" + listName)
        print("taskName=" + taskName)
        data = {
            "revision": revision,
            "completed": True
        }
        logging.error(Event.baseURL + EventMarkTaskCompleted.path + str(taskID))
        logging.error(taskID)
        check = self.makeGetRequest(EventMarkTaskCompleted.path + str(taskID), {}, event)
        logging.error(check.json())
        response = self.makePatchRequest(EventMarkTaskCompleted.path + str(taskID), data, event)
        logging.error("RESPONSE")
        logging.error(response.json())

        if response.status_code == EventMarkTaskCompleted.STATUS_CODE:
            return "I've checked off " + taskName + " from your " + listName + " list"
        else:
            return "I couldn't check off " + taskName + " from your " + listName + " list"

    path = "/tasks/"
    STATUS_CODE = 200


class EventDeleteTask(Event):
    def doExecute(self, event):
        getLists = self.makeGetRequest("/lists", {}, event)
        lists = getLists.json()

        listName = event["request"]["intent"]["slots"]["ListName"]["value"].lower()
        taskName = event["request"]["intent"]["slots"]["TaskName"]["value"].lower()
        revision = 0
        listID = 0

        for listItem in lists:
            if listItem["title"].lower() == listName:
                listID = listItem["id"]

        params = {
            "list_id": listID
        }
        taskList = self.makeGetRequest("/tasks", params, event).json()

        for task in taskList:
            if task['title'] == taskName:
                taskID = task['id']
                revision = task['revision']

        if taskID == 0:
            return "Could not find " + taskName + " in " + listName

        param = {
            "revision": revision
        }

        response = self.makeDeleteRequest(EventDeleteTask.path + str(taskID), param, event)
        logging.error(response.json)

        if response.status_code == EventDeleteTask.STATUS_CODE:
            return "I've removed " + taskName + " from " + listName
        else:
            return "I couldn't remove " + taskName + " from " + listName

    path = "/tasks/"
    STATUS_CODE = 204


class EventDeleteList(Event):
    def doExecute(self, event):
        getLists = self.makeGetRequest("/lists", {}, event)
        lists = getLists.json()

        listName = event["request"]["intent"]["slots"]["ListName"]["value"].lower()
        revision = 0
        listID = 0

        for listItem in lists:
            if listItem["title"].lower() == listName:
                revision = listItem["revision"]
                listID = listItem["id"]

        if revision == 0:
            return "Could not find " + listName

        params = {
            "revision": revision
        }

        response = self.makeDeleteRequest(EventDeleteList.path + str(listID), params, event)
        logging.error(response)
        return "I've deleted the list, " + listName

    path = "/lists/"
    STATUS_CODE = 204


class EventReadTasks(Event):
    def doExecute(self, event):
        lists = self.makeGetRequest("/lists", {}, event).json()
        listName = event["request"]["intent"]["slots"]["ListName"]["value"].lower()
        listID = 0

        for listItem in lists:
            if listItem["title"].lower() == listName:
                listID = listItem["id"]

        if listID == 0:
            return "Could not find " + listName

        params = {
            "list_id": listID
        }
        taskList = self.makeGetRequest("/tasks", params, event).json()
        taskNames = []
        for task in taskList:
            taskNames.append(task["title"])

        if len(taskNames) > 0:
            return "Your tasks in " + listName + " are " + ", ".join(
                taskNames)  # TODO: make this return better. Add and before last element.
        else:
            return "You have no tasks in " + listName + "."

    path = "/tasks"
    STATUS_CODE = 200


class EventTest(Event):
    def doExecute(self, event):
        return "Test Successful"


class EventShowAllLists(Event):
    def doExecute(self, event):
        data = {}
        response = self.makeGetRequest(EventShowAllLists.path, data, event)
        lists = response.json()
        listNames = []

        for listItem in lists:
            if listItem["list_type"] == "list":
                listNames.append(listItem["title"])

        if len(listNames) > 0:
            return "Your lists are " + ", ".join(
                listNames)  # TODO: make this return better. Add and before last element.
        else:
            return "You have no lists."

    path = "/lists"
