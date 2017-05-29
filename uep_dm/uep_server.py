import requests
import json
import time
import urllib
from pprint import pprint

#key of developer in Greece
#API_KEY = 'YX48HVaO9bSH18094S4CvEFffF397186ACZ8S3vYRkMLRxMvwOe'

#key of developer in UNIBN
#API_KEY = 'RuR4r60A18063xYpLcM5A84vyC637539zy14Txx6YerGvoxWLlc'

#key of Fraunhofer server
API_KEY = 'sZN53u1sh18065mi3KvrHhwHWj38204A7HW9pnYHGgxj9SasZmA'

API_URL = 'https://br-dev.lmcloud.vse.cz/easyminercenter/api'

ANTECEDENT_COLUMNS = []
# there can be list of data fields (columns) in the input CSV -
#  if this array is empty, all data fields not included in consequent will be added into antecedent
CONSEQUENT_COLUMNS = ["Technical_Assistance_5"]
# data fields for the consequent
MIN_CONFIDENCE = 0.7
# requested minimal value of confidence
MIN_SUPPORT = 0.1
# requested minimal value of support

CSV_SEPARATOR = ";"
CSV_ENCODING = "utf8"


#1 upload data set - create datasource
def upload_data_set(csv_file, csv_separator, csvEncoding):
    """
    input-file for the data-mining is a csv file, in which <csv_separator> is used as separator
    :param csv_file:
    :param csv_separator:
    :return: an identification number of the csv file
    """
    headers = {"Accept": "application/json"}
    files = {("file", open(csv_file, 'rb'))}
    req = requests.post(API_URL + '/datasources?separator=' + urllib.parse.quote(csv_separator) +
                  '&encoding=' + csvEncoding + '&type=limited&apiKey=' + API_KEY, files=files, headers=headers)

    dataSourceId = req.json()["id"]
    return dataSourceId


#2 create miner
def create_miner(dataSourceId, minerName, apiURL, apiKey):
    """
    create a data-mining instance from the server-side
    :param dataSourceId: an identification number of the csv file
    :param minerName: the name of the data-mining service
    :param apiURL: the URL of the API
    :param apiKey: user key
    :return:
    """
    headers = {'Content-Type': 'application/json', "Accept": "application/json"}
    json_data = json.dumps({"name": minerName, "type": "cloud", "datasourceId": dataSourceId})
    req = requests.post(apiURL + "/miners?apiKey=" + apiKey, headers=headers, data=json_data.encode())
    minerId = req.json()["id"]
    return minerId


#3 preprocess data fields to attributes
def preprocess_data_fields_to_attributes(miner_id, dataSourceId, apiURL, apiKey):
    headers = {'Content-Type': 'application/json', "Accept": "application/json"}
    req = requests.get(apiURL + '/datasources/' + str(dataSourceId) + '?apiKey=' + apiKey, headers=headers)
    datasourceColumns = req.json()['column']
    attributesColumnsMap = {}
    for col in datasourceColumns:
        column = col["name"]
        json_data = json.dumps(
            {"miner": miner_id, "name": column, "columnName": column, "specialPreprocessing": "eachOne"})
        req1 = requests.post(apiURL + "/attributes?apiKey=" + apiKey, headers=headers, data=json_data.encode())
        if req1.status_code != 201:
            break  # error occured
        attributesColumnsMap[column] = req1.json()['name']
        # map of created attributes (based on the existing data fields)
    return attributesColumnsMap


#4 prepare antecedent pattern
def prepare_antecedent_pattern(antecedentColumns, attributes_columns_map):
    antecedent = []
    if len(antecedentColumns):
        # add to antecedent only fields defined in the constant
        for column in antecedentColumns:
            antecedent.append({"attribute": attributes_columns_map[column]})
    else:
        # add to antecedent all fields not used in consequent
        for (column, attribute_name) in attributes_columns_map.items():
            if not(column in antecedentColumns):
                antecedent.append({"attribute": attribute_name})
    return antecedent


#5 prepare consequent pattern
def prepare_consequent_pattern(consequentColumns, attributesColumnsMap):
    consequent = []
    for column in consequentColumns:
        consequent.append({"attribute": attributesColumnsMap[column]})
    return consequent


#6 define data mining task
def define_data_mining_task(apiUrl, apiKey, taskName, minerId, minerName, antecedentColumns, consequentColumns, attributesColumnsMap,minConfidence, minSupport):
    headers = {'Content-Type': 'application/json', "Accept": "application/json"}
    antecedent = prepare_antecedent_pattern(antecedentColumns, attributesColumnsMap)
    consequent = prepare_consequent_pattern(consequentColumns, attributesColumnsMap)
    json_data = json.dumps({"miner": minerId,
                            "name": minerName,
                            "limitHits": 1000,
                            "IMs": [
                                    {
                                        "name": "CONF",
                                        "value": minConfidence
                                    },
                                    {
                                        "name": "SUPP",
                                        "value": minSupport
                                    }
                                ],
                            "antecedent": antecedent,
                            "consequent": consequent
                            })

    req = requests.post(apiUrl + "/tasks/"+taskName+"?apiKey=" + apiKey, headers=headers, data=json_data.encode())
    print("create task response code:" + str(req.status_code))
    taskId = str(req.json()["id"])
    return taskId

#6.1 define outlier tast
def define_outlier_mining_task(apiUrl, apiKey, taskName, miner_id, minerName, min_support):
    headers = {'Content-Type': 'application/json', "Accept": "application/json"}
    json_data = json.dumps({"miner": miner_id, "minSupport": min_support})
    r = requests.post(apiUrl + "/outliers-tasks?apiKey=" + apiKey, headers=headers, data=json_data.encode())
    outlier_task_id = str(r.json()["id"])
    return outlier_task_id


#7 running task
def start_task(apiURL, taskId, apiKey):
    headers = {'Content-Type': 'application/json', "Accept": "application/json"}
    while True:
        time.sleep(1)
        # check state
        r = requests.get(apiURL + "/tasks/" + taskId + "/start?apiKey=" + apiKey, headers=headers)
        task_state = r.json()["state"]
        print("task_state:" + task_state)
        if task_state == "solved":
            return True
        if task_state == "failed":
            print(CSV_FILE + ": task failed executing")
            return False

#7.1 running outlier task
def start_outlier_task(apiURL, outlier_task_id, apiKey):
    headers = {'Content-Type': 'application/json', "Accept": "application/json"}
    while True:
        time.sleep(1)
        # check state
        r = requests.get(apiURL + "/outliers-tasks/" + outlier_task_id + "/start?apiKey=" + apiKey, headers=headers)
        while True:
            time.sleep(1)
            # check state
            r = requests.get(apiURL + "/outliers-tasks/" + outlier_task_id + "/state?apiKey=" + apiKey,
                             headers=headers)
            task_state = r.json()["state"]
            print("task_state:" + task_state)
            if task_state == "solved":
                break
            if task_state == "failed":
                print("task failed executing")
                break


#8 export rules in JSON format
# export of standardized PMML AssociationModel
# export of GUHA PMML
def export_rules_in_JSON(apiURL, taskId, apiKey, output_format = "json"):
    headers = {"Accept": "application/json"}
    task_flag = start_task(apiURL, taskId, apiKey)
    if not task_flag:
        print('task failed')
        return -1
    if output_format == "json":
        r = requests.get(apiURL + '/tasks/' + taskId + '/rules?apiKey=' + apiKey, headers=headers)
        taskRules = r.json()
        #pprint(taskRules)
        return json.dumps(taskRules)
    elif output_format == "PMML":
        r = requests.get(apiURL + '/tasks/' + taskId + '/pmml?model=associationmodel&apiKey=' + apiKey)
        pmml = r.text
        return pmml
    elif output_format == "GUHA_PMML":
        r = requests.get(apiURL + '/tasks/' + taskId + '/pmml?model=guha&apiKey=' + apiKey)
        guha_pmml = r.text
        return guha_pmml
    else:
        print("output_format = 'json' or 'PMML' or 'GUHA_PMLL'")
        return -1

#8.1 export rules in JSON format
# export of standardized PMML AssociationModel
# export of GUHA PMML
def export_outliers_in_JSON(apiURL, outlier_task_id, apiKey, output_format = "json"):
    offset = 0
    limit = 10
    headers = {"Accept": "application/json"}
    task_flag = start_outlier_task(apiURL, outlier_task_id, apiKey)
    if not task_flag:
        print('task failed')
        return -1
    if output_format == "json":
        r = requests.get(apiURL + '/outliers-tasks/' + outlier_task_id + '/outliers?apiKey=' + apiKey + '&offset=' + offset + '&limit=' + limit, headers=headers)
        outliers = r.json()['outlier']

        #pprint(outliers)
        return json.dumps(outliers)



def send_request_to_UEP_server(csvFile,taskName="simple", apiURL=API_URL, apiKey=API_KEY, outputFormat = 'json',
                               antecedentColumns=ANTECEDENT_COLUMNS, consequentColumns=CONSEQUENT_COLUMNS,
                               minConfidence=MIN_CONFIDENCE, minSupport=MIN_SUPPORT, csvSeprator=CSV_SEPARATOR,
                               csvEncoding=CSV_ENCODING):
    """
    the main function to send a rule-mining request to the UEP server
    :param csvFile: a csv file as the input
    :param apiURL: the URL for the data-mining API
    :param apiKey: userkey
    :param outputFormat: the default output format is json, other formats are PMML, GUHA_PMML
    :param antecedentColumns: antecedent of a rule
    :param consequentColumns: consequent of a rule
    :return: identified rules, and a description of the rule-mining task
    """
    datasourceId = upload_data_set(csvFile, csvSeprator, csvEncoding)
    minerId = create_miner(datasourceId, "TEST MINER", apiURL, apiKey)
    attributes_columns_map = preprocess_data_fields_to_attributes(minerId, datasourceId, apiURL, apiKey)
    if(taskName=="simple"):
        task_id = define_data_mining_task(apiURL, apiKey, taskName, minerId, "Test Miner", antecedentColumns,
                                      consequentColumns, attributes_columns_map, minConfidence, minSupport)
        result = export_rules_in_JSON(apiURL, task_id, apiKey, output_format = outputFormat)
    if (taskName == "outlier"):
        task_id = define_outlier_mining_task(apiURL, apiKey, taskName, minerId, "Test Miner", minSupport)
        result = export_outliers_in_JSON(apiURL, task_id, apiKey, output_format=outputFormat)

    return result

