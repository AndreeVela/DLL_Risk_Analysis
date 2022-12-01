import library.link_preprocessor as lp
import library.query_builder as qb
import library.web_crawler as wc
import library.credibility_analysis as cra
import library.content_analysis as ca
import library.dataframe_preprocessor as dp
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
    final_hits_df['Credibility Score'] = final_hits_df['Source Type'].apply(cra.score)

    # performing content analysis for non-social media sources
    ## creating a new column, 'content' to get the content for non-Social Media sources
    final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Content'] = final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'URL'].apply(ca.extractor)

    # creating a new column, 'Content check': 0 for not having keyword, 1 for having keyword
    final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Content check'] = final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Content'].apply(ca.entity_check, args = (keywords_list,))

    # removing rows having 'Content check' = 0
    final_hits_df = final_hits_df.loc[final_hits_df['Content check'] != 0, :]

    # dropping 'Content check' columns ...
    final_hits_df.drop(['Content check'], axis = 1, inplace = True)

    # measuring the adversity score for each and every content
    final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Adversity Score'] = final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Content'].apply(ca.adversity)

    final_hits_df = dp.generate_google_and_date_ranks(final_hits_df)

    
    print('Adverse Media Screened !!!')
    final_hits_df.to_excel('AMS.xlsx', index = False)
