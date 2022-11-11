# importing necessary libraries

def get_inputFromUI():
    # take input from user
    keywords = [] # make a list
    keywords.append("Gerard Sanderink")
    return keywords


def get_queries():
    keywords = get_inputFromUI()
    
    #read the queries from a file
    with open('data/search_strings.txt', 'r', encoding="utf8") as file:
        queries = file.read().split('\n')

    for keyword in keywords:
        replaced_queries = [query.replace("entity", keyword) for query in queries]
        
    return replaced_queries
