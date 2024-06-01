import os
import subprocess
import shlex
import re

class SwishEResult:
    def __init__(self):
        self.search_words = ""
        self.removed_stopwords = []
        self.number_of_hits = 0
        self.search_time = 0.0
        self.run_time = 0.0
        self.documents = []

    def parse_output(self, output):
        lines = output.split('\n')

        # Parsing search words
        search_words_line = next((line for line in lines if '# Search words:' in line), None)
        if search_words_line:
            self.search_words = search_words_line.split(':')[1].strip()

        # Parsing removed stopwords
        stopwords_line = next((line for line in lines if '# Removed stopwords:' in line), None)
        if stopwords_line:
            self.removed_stopwords = stopwords_line.split(':')[1].strip().split(', ')

        # Parsing number of hits
        hits_line = next((line for line in lines if '# Number of hits:' in line), None)
        if hits_line:
            self.number_of_hits = int(hits_line.split(':')[1])

        # Parsing search time
        search_time_line = next((line for line in lines if '# Search time:' in line), None)
        if search_time_line:
            search_time_str = search_time_line.split(':')[1].split()[0].replace(',', '.')
            try:
                self.search_time = float(search_time_str)
            except ValueError as e:
                print(f"Error converting search time to float: {e}")

        # Parsing run time
        run_time_line = next((line for line in lines if '# Run time:' in line), None)
        if run_time_line:
            run_time_str = run_time_line.split(':')[1].split()[0].replace(',', '.')
            try:
                self.run_time = float(run_time_str)
            except ValueError as e:
                print(f"Error converting run time to float: {e}")

        # Parsing document information
        document_lines = [line for line in lines if re.match(r"\d+ Rank-c/.+/\w+\.txt .+", line)]

        for doc_line in document_lines:
            match = re.match(r'(?P<rank>\d+) Rank-c/data/(?P<file_path>\w+\.txt) "(?P<content>.+)" (?P<skor>\d+)', doc_line)

            if match:
                document_info = {
                    'rank': int(match.group('rank')),
                    'file_path': match.group('file_path'),
                    'content': match.group('content'),
                    'skor': int(match.group('skor'))
                }
                self.documents.append(document_info)
            else:
                print(f"Failed to match line: {doc_line}")

    def __str__(self):
        result_str = f"# Search words: {self.search_words}\n"
        result_str += f"# Removed stopwords: {', '.join(self.removed_stopwords)}\n"
        result_str += f"# Number of hits: {self.number_of_hits}\n"
        result_str += f"# Search time: {self.search_time} seconds\n"
        result_str += f"# Run time: {self.run_time} seconds\n"

        if self.documents:
            result_str += "\n# Top documents are:\n"
            for doc in self.documents:
                result_str += f"{doc['rank']} {doc['file_path']} {doc['content']}\n"

        return result_str

def get_swish_e_query(parameter, k):
    try:
        # Ganti spasi dengan ' or ' dalam parameter
        parameter = ' or '.join(shlex.quote(word) for word in parameter.split())

        # Sertakan parameter saat menjalankan Swish-e
        result = subprocess.run(['swish-e', '-w', parameter, '-m', shlex.quote(k)], stdout=subprocess.PIPE, text=True, check=True)
        output = result.stdout.strip()

        # Buat objek SwishEResult dan parse output Swish-e
        result_obj = SwishEResult()
        result_obj.parse_output(output)

        return result_obj
    except subprocess.CalledProcessError as e:
        print(f"Error running Swish-e: {e}")
        return None
