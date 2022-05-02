import json
import csv
import pandas

def export_file(dt_json: json, file_name: str):
    fh = open(file_name, "w")
    fh.write(json.dumps(dt_json, indent=4))
    fh.close()


def export_file_js_var(dt_json: json, var_name: str, file_name: str):
    var_data = json.loads(dt_json)
    var_data = json.dumps(var_data)
    js_str = "var " + var_name + " = '" + var_data + "'"
    fh = open(file_name, "w")
    fh.write(js_str)
    fh.close()


def export_matrix_to_csv(data: list, file_name: str):
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    file.close()


def export_dict_to_csv(data: dict, file_name: str):
    df = pandas.DataFrame(data)
    df.to_csv(file_name)