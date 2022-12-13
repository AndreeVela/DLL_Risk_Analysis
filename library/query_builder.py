# importing necessary libraries

def get_inputFromUI():
    # take input from user
    keywords = [] # make a list
    keywords.append("Rabobank")
    #keywords.append("Strukton")
    return keywords


def get_queries(keywords=None, search_strings_path='./flaskr/queries/search_strings.txt'):
    if not keywords:
        keywords = get_inputFromUI()
    
    #read the queries from a file
    with open(search_strings_path, 'r', encoding="utf8") as file:
        queries = file.read().split('\n')

    replaced_queries = []
    keyword_mapper = []
    adverse_type_mapper = []

    for keyword in keywords:
        replaced_queries += [query.replace("entity", keyword) for query in queries]
        keyword_mapper += [keyword]*len(queries)
        adverse_type_mapper += ['CAMS', 'CAMS', 'ESG']

    return replaced_queries, keyword_mapper, adverse_type_mapper
