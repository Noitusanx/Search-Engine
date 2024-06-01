import os
import subprocess
import re #rf
from FileParser import get_info_file

class CRankResult:
    def __init__(self):
        self.distinct_terms = 0
        self.words = []  # Menggunakan list untuk menampung lebih dari satu kata
        self.top_documents = []

    def parse_output(self, output):
        lines = output.split('\n')

        # Parsing distinct terms
        self.distinct_terms = int(lines[0].split()[1])

        # Mencari baris yang mengandung pola '#Word'
        word_lines = [line for line in lines if '#Word' in line]

        for word_line in word_lines:
            # Mencocokkan pola '#Word' menggunakan ekspresi reguler
            match = re.match(r"#Word \['(?P<word>\w+)'\], fw \(num of doc containing the word\) = (?P<fw>\d+\.\d+)", word_line)

            if match:
                # Mendapatkan word dan fw dari grup ekspresi reguler
                word = match.group('word')
                fw = float(match.group('fw'))
                self.words.append({'word': word, 'fw': fw})


        # Mencari baris yang mengandung pola 'Document [...]' untuk mendapatkan informasi dokumen
        document_lines = [line for line in lines if re.match(r"Document \[\d+ \d+\.+txt\] or docno \d+ ranked = \d+\.\d+", line)]

        # Mencocokkan pola 'Document [...]' menggunakan ekspresi reguler untuk setiap baris
        for doc_line in document_lines:
            match = re.match(r"Document \[(?P<id>\d+) (?P<file>\d+\.+txt)\] or docno (?P<docno>\d+) ranked = (?P<ranked>\d+\.\d+)", doc_line)

            if match:
                info_file = get_info_file('data/' + match.group('file'))
                # Mendapatkan informasi dokumen dari grup ekspresi reguler
                document_info = {
                    'document_id': int(match.group('id')),
                    'docno': match.group('docno'),
                    'file': match.group('file'),
                    'ranked': float(match.group('ranked')),
                    'title': info_file.title
                }
                self.top_documents.append(document_info)
        

    def __str__(self):
        result_str = f"#Found {self.distinct_terms} distinct terms in {len(self.top_documents)} documents\n"
        if self.words:
            for word_info in self.words:
                result_str += f"#Word ['{word_info['word']}'], fw (num of doc containing the word) = {word_info['fw']}\n"
        else:
            result_str += f"#Word is not indexed or all query terms are stopword\n"
        if self.top_documents:
            result_str += "\n#Top 15th documents are:\n"
            for doc in self.top_documents:
                result_str += f"Document [{doc['document_id']} {doc['file']}] or docno {doc['docno']} ranked = {doc['ranked']}\n"
        result_str += "#Time required: 0.000000 mseconds"
        return result_str

def get_rank_c_query(parameter, k):
    # Gunakan path relatif terhadap lokasi skrip Python
    c_program_directory = os.path.join(os.path.dirname(__file__), 'Rank-c')
    c_program_name = './querydb'

    try:
        # Simpan working directory saat ini
        current_directory = os.getcwd()

        # Ubah working directory ke path absolut dari file program C
        os.chdir(os.path.abspath(c_program_directory))

        # Sertakan parameter saat menjalankan program C
        result = subprocess.run([c_program_name, parameter, k], stdout=subprocess.PIPE, text=True, check=True)
        output = result.stdout.strip()

        # Buat objek RankCResult dan parse output program C
        result_obj = CRankResult()
        result_obj.parse_output(output)

        return result_obj
    except subprocess.CalledProcessError as e:
        print(f"Error running C program: {e}")
        return None
    finally:
        # Pastikan bahwa variabel current_directory sudah dideklarasikan sebelumnya
        if 'current_directory' in locals():
            # Kembalikan working directory ke yang semula
            os.chdir(current_directory)

