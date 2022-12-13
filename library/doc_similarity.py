import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, util


def pairwise_doc_similariy(list_of_urls, list_of_content):
	model = SentenceTransformer('all-MiniLM-L6-v2')
	list_of_content1 = list_of_content
	list_of_content2 = list_of_content

	# computing embedding for both lists
	sentence_embeddings1 = model.encode(list_of_content1, convert_to_tensor=True)
	sentence_embeddings2 = model.encode(list_of_content2, convert_to_tensor=True)

	cosine_scores = util.cos_sim(sentence_embeddings1, sentence_embeddings2)
	cosine_scores = abs(cosine_scores)

	urls = list_of_urls
	doc_similarity_df = pd.DataFrame(cosine_scores, index = urls, columns = urls)

	return doc_similarity_df


def compute_avg_similarity(doc_similarity_matrix):
	n_docs = doc_similarity_matrix.shape[0]
	doc_similarity_matrix_rowwise_sum = np.sum(doc_similarity_matrix, axis = 1)
	doc_similarity_matrix_diagonal_version = np.diag(doc_similarity_matrix*np.eye(n_docs, n_docs))
	doc_similarity_matrix_rowwise_avg = (doc_similarity_matrix_rowwise_sum - doc_similarity_matrix_diagonal_version)/(n_docs - 1)
	return doc_similarity_matrix_rowwise_avg
