import library.link_preprocessor as lp
import library.query_builder as qb
import library.web_crawler as wc
import library.credibility_analysis as cra
import library.content_analysis as ca
import library.dataframe_preprocessor as dp
import library.doc_similarity as ds
import pandas as pd
import numpy as np

from datetime import date



url_prefix = 'https://google.com/search?q='



if __name__ == "__main__":
    ## input comes from UI, maybe a list of inputs, modify code later
    ## contacting google with search string is done in nested loop
    keywords_list = qb.get_inputFromUI()
    
    # read the queries from a file
    queries, keyword_mapper, adverse_type_mapper = qb.get_queries()
    
    # Declaring what is scaraped from results
    final_hits_df = pd.DataFrame()
    
    # iterate over every query
    indexer = 0
    for query in queries:
        hits_df = wc.get_hitsinformation(url_prefix+query, keywords_list)
        hits_df['Target Search'] = keyword_mapper[indexer]
        hits_df['Adverse Type'] = adverse_type_mapper[indexer]
        indexer += 1
        final_hits_df = final_hits_df.append(hits_df)


    # credibility analysis (1 -> HIGHEST, 3 -> LOWEST)
    final_hits_df['Credibility Score'] = final_hits_df['Source Type'].apply(cra.score)

    # relevancy analysis (< 5 years: 'Recency' = 1 and 0 otherwise)
    final_hits_df['Recency'] = final_hits_df['Date'].map(lambda date: 1 if (date.today().year - date.year) <= 5 else 0)


    # performing content analysis for non-social media sources
    ## creating a new columns, 'heading' and 'content' to get the content for non-Social Media sources
    heading_content_df = final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'URL'].apply(ca.extractor)
    headings = [heading_content[0] for heading_content in list(heading_content_df)]
    contents = [heading_content[1] for heading_content in list(heading_content_df)]

    final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Heading'] = headings
    final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Content'] = contents

    '''
    # creating a new column, 'Content check': 0 for not having keyword, 1 for having keyword
    final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Content check'] = final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Content'].apply(ca.entity_check, args = (keywords_list,))

    # removing rows having 'Content check' = 0
    final_hits_df = final_hits_df.loc[final_hits_df['Content check'] != 0, :]

    # dropping 'Content check' columns ...
    final_hits_df.drop(['Content check'], axis = 1, inplace = True)
    '''

    # measuring the adversity score for each and every content
    final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Adversity Score'] = final_hits_df.loc[final_hits_df['Source Type'] != 'Social Media', 'Content'].apply(ca.adversity)

    final_hits_df = dp.generate_google_and_date_ranks(final_hits_df)


    # top max 50 sources or URLs of Adverse Media

    ## picking the news that are related for the last five years
    top_hits_df = final_hits_df.loc[final_hits_df['Recency'] == 1]

    ## sorting the date and Adversity score
    top_hits_df.sort_values(by=['Date', 'Adversity Score'], inplace=True, ascending = [False, False])

    ## selecting the first 50 rows
    top_hits_df = top_hits_df.head(40)

    '''
    # document similarity and reliability analysis
    top_hits_df_notsocialmedia = top_hits_df.loc[top_hits_df['Source Type'] != 'Social Media']
    top_hits_df_notsocialmedia = top_hits_df_notsocialmedia[top_hits_df_notsocialmedia['Source Type'].notna()]
    top_hits_df_notsocialmedia = top_hits_df_notsocialmedia[top_hits_df_notsocialmedia['Content'].notna()]

    top_hits_df_notsocialmedia['Preprocessed Content'] = top_hits_df_notsocialmedia['Content'].apply(dp.text_process)
    doc_similarity_df = ds.pairwise_doc_similariy(list(top_hits_df_notsocialmedia['URL']), list(top_hits_df_notsocialmedia['Content']))

    avg_doc_similarity_scores = ds.compute_avg_similarity(np.array(doc_similarity_df))

    top_hits_df_notsocialmedia['Reliability Score'] = avg_doc_similarity_scores

    top_hits_df = pd.merge(top_hits_df, top_hits_df_notsocialmedia, on = 'URL', how = 'outer')
    '''

    
    print('Adverse Media Screened !!!')
    final_hits_df.to_excel('AMS.xlsx', index = False)
    top_hits_df.to_excel('AMS_top_hits.xlsx', index = False)
