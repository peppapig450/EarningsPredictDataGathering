import json


class OutputUtils:
    def save_json(self, json_data, output_file_path):
        with open(output_file_path, "w", encoding="utf-8") as file:
            json.dump(json_data, file, indent=4)
