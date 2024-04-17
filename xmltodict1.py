import re
import xmltodict
import json


def parse_xml_to_json(xml_file):
    try:
        with open(xml_file, "r") as f:
            xml_data = f.read()
            json_data = xmltodict.parse(xml_data)
        return json.dumps(json_data, indent=4)
    except Exception as e:
        raise ValueError(f"Error parsing XML file: {e}")


def CreateJSONObject(jsondata, xml_file_path):
    if jsondata is not None:
        j = json.dumps(jsondata)
        jfile = re.sub(".xml", "", xml_file_path) + ".json"
        with open(jfile, "w") as f:
            f.write(jsondata)
    else:
        print("Cannot create JSON object due to invalid XML data.")


# Example usage
xml_file_path = "lead1.xml"
json_data = parse_xml_to_json(xml_file_path)
print(json_data)
CreateJSONObject(json_data, xml_file_path)
# Use try catch and error handling
