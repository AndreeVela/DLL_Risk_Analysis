import library.link_preprocessor as lp
import library.query_builder as qb
import library.web_crawler as wc
import library.credibility_analysis as ca
import pandas as pd



url_prefix = 'https://google.com/search?q='



if __name__ == "__main__":
    ## input comes from UI, maybe a list of inputs, modify code later
    ## contacting google with search string is done in nested loop
    keywords_list = qb.get_inputFromUI()
    
    # read the queries from a file
    queries = qb.get_queries()
    
    # Declaring what is scaraped from results
    final_hits_df = pd.DataFrame()
    
    # iterate over every query
    for query in queries:
        hits_df = wc.get_hitsinformation(url_prefix+query, keywords_list)
        final_hits_df = final_hits_df.append(hits_df)

    # credibility analysis (1 -> HIGHEST, 3 -> LOWEST)
    final_hits_df['Credibility Score'] = final_hits_df['Source Type'].apply(ca.score)
    
    print('Adverse Media Screened !!!')
    final_hits_df.to_excel('AMS.xlsx', index = False)
