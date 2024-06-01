# app.py
from flask import Flask, jsonify, request, render_template
from markupsafe import Markup  # Import Markup from markupsafe
from CResult import get_rank_c_query
from SwishEResult import get_swish_e_query #rf
from FileParser import get_info_file

app = Flask(__name__)

# Daftar search engine yang dapat dipilih
search_engines = ['rankc', 'swishe']

@app.route("/")
def home():
    default_search_engine = search_engines[0]
    return render_template('index.html', search_engines=search_engines, search_engine=default_search_engine, current_k=5)

@app.route('/content/<file_name>')
def serve_file(file_name):
    try:
        file_name = 'Rank-c/data/' + file_name
        file_content = get_info_file(file_name)
        title = file_content.title
        content = Markup(file_content.file_content)
        print(title)
        return render_template('content.html', title=title, content=content)
    except FileNotFoundError:
        return "File not found", 404
    
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('search_query')
    search_engine = request.args.get('search_engine')
    k_value = request.args.get('top_documents')

    if search_engine == 'rankc':
        # Panggil program C dan ambil outputnya
        query_result = get_rank_c_query(query, k_value)

        if query_result:
            # Persiapkan respons JSON
            response = {
                'words': query_result.words,
                'distinct_terms': query_result.distinct_terms,
                'top_documents': query_result.top_documents
            }

            # Jika kata tidak terdaftar atau query hanya terdiri dari stopword
            if not query_result.words:
                response['error'] = 'Word is not indexed or all query terms are stopword'
                response['words'] = None
                response['top_documents'] = None

            # Return kirim hasil
            return render_template('search.html', results = response, current_k = k_value, search_engines = search_engines, search_engine = search_engine)
        else:
            return jsonify({'error': 'Error running C program'}), 500
        
    elif search_engine == 'swishe':
        query_result = get_swish_e_query(query, k_value)

        if query_result:
            # Persiapkan respons JSON
            response = {
                'search_words': query_result.search_words,
                'number_of_hits': query_result.number_of_hits,
                'search_time': query_result.search_time,
                'run_time': query_result.run_time,
                'documents': query_result.documents
            }

            # Jika kata tidak terdaftar atau query hanya terdiri dari stopword
            if not query_result.search_words:
                response['error'] = 'Word is not indexed or all query terms are stopword'
                response['search_words'] = None
                response['documents'] = None

            # Return kirim hasil
            return render_template('search.html', results = response, current_k=k_value, search_engines=search_engines, search_engine=search_engine)
        else:
            return jsonify({'error': 'Failed to process the request'}), 500

if __name__ == '__main__':
    app.run(debug=True)
