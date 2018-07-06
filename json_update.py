import json 
jsondata1 = []
dict = {}
file_txt = open("config_tmp.ini")
data = file_txt.read()
jsondata = json.loads(data)
list1 =  jsondata["node"]

for val in list1:  #val dictionary item of list 
    line = val["WDS"]  # line by record key
    flag=  line.find("docker_container_name")
    if (flag >-1):
        jsondata1.append(val)
newdata = PROJ-WDS_16-011261
dict["docker_container_name"] = newdata

file_json= open("newdata6.json", "w")
json.dump(dict,file_json, indent=2)
    
file_txt.close()
file_json.close()
