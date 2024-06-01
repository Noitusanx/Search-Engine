import re

class FileParser:
    def __init__(self, path):
        self.path = path
        self.title = None
        self.file_content = None

    def read_file(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                self.file_content = file_content
                self.extract_content(file_content)
        except FileNotFoundError:
            print(f"File not found: {self.path}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def extract_content(self, file_content):
        title_match = re.match(r'<title>(.*?)</title>', file_content, re.DOTALL)
        if title_match:
            self.title = title_match.group(1).strip()

def get_info_file(file_path):
    fileParser_instance = FileParser(file_path)
    fileParser_instance.read_file()
    return fileParser_instance


