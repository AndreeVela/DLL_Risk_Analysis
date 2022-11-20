# importing necessary libraries

def get_inputFromUI():
    # take input from user
    keywords = [] # make a list
    keywords.append("Strukton")
    return keywords


def get_queries(keywords=None, search_strings_path='./flaskr/queries/search_strings.txt'):
    if not keywords:
        keywords = get_inputFromUI()
    
    #read the queries from a file
    with open(search_strings_path, 'r', encoding="utf8") as file:
        queries = file.read().split('\n')

    for keyword in keywords:
        replaced_queries = [query.replace("entity", keyword) for query in queries]
        
    return replaced_queries
