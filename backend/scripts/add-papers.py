# from bs4 import BeautifulSoup
# import requests
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
from sentence_transformers import SentenceTransformer
import urllib.request as libreq
import feedparser
import time
import argparse

program_name = """
add-papers.py
"""
program_usage = """
add-papers.py [options] -i ITER -a AMT
"""
program_description = """description:
This is a python script to upload a specified number of documents to an elasticsearch
database from arXiv
"""
program_epilog = """ 

"""
program_version = """
Version 3.0 2024-06-01
Created by Vikram Penumarti
"""

load_dotenv()
API_KEY = os.getenv('API_KEY')

client = Elasticsearch(
  "https://localhost:9200",
  api_key=API_KEY,
  ca_certs="../config/ca.crt"
)

# print(client.info())
# exit()

# client = Elasticsearch("http://localhost:9200")

model = SentenceTransformer('all-MiniLM-L6-v2')

def set_parser(program_name,program_usage,program_description,program_epilog,program_version):
    parser = argparse.ArgumentParser(prog=program_name,
                                     usage=program_usage,
                                     description=program_description,
                                     epilog=program_epilog,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i','--iter', required=False, default=1, type=int,
                        help="[Required] Number of iterations of file uploads to perform (higher number is more likely to get rate limited, min 1)")
    parser.add_argument('-a','--amt', required=False, default=2000, type=int,
                        help="[Required] Number of documents to fetch from arXiv (max 2000, min 1)")
    parser.add_argument('-v','--version', action='version', version=program_version)
    
    return parser

def findInfo(start, amount):
  search_query = 'all:superconductivity'
#   wait_time = 60

  url = f'http://export.arxiv.org/api/query?search_query={search_query}&start={start}&max_results={amount}'
    
  print(f'Searching arXiv for {search_query}')
    
  with libreq.urlopen(url) as url:
    content = url.read()

  feed = feedparser.parse(content)
  
  paper_list = []
  for entry in feed.entries:          
    paper_dict = {
      'id': entry.id.split('/abs/')[-1].replace("/", "-"),
      'title': entry.title,
      'links': [link['href']for link in entry.get('links')],
      'summary': entry.get('summary'),
      'date': int(time.strftime("%Y%m%d", entry.get('published_parsed'))),
      'updated': int(time.strftime("%Y%m%d", entry.get('updated_parsed'))),
      'categories': [category['term'] for category in entry.get('tags')],
      'authors': [author['name'] for author in entry.get('authors')],
      'doi': entry.get('arxiv_doi'),
      'journal_ref': entry.get('arxiv_journal_ref'),
      'comments': entry.get('arxiv_comment'),
      'primary_category': entry.get('arxiv_primary_category').get('term'),
    }
    
    paper_list.append(paper_dict)
    
  print(f"Collected papers {start} - {start + amount}")
    
#   print(f'Sleeping for {wait_time} seconds')
#   time.sleep(wait_time)
    
  return replaceNullValues(paper_list)

def replaceNullValues(papers_list):
  for i in range(len(papers_list)):
    for key, val in papers_list[i].items():
      if not val:
        papers_list[i][key] = "N/A"
  
  return papers_list 
    
def createNewIndex(delete, index):
    if client.indices.exists(index=index) and delete:
        client.indices.delete(index=index)
    if not client.indices.exists(index=index):
        client.indices.create(
            index=index, 
            mappings={
                'properties': {
                    'embedding': {
                        'type': 'dense_vector'
                    },
                    # 'elser_embedding': {
                    #     'type': 'sparse_vector',
                    # },
                },
            },
            # settings={
            #     'index': {
            #         'default_pipeline': 'elser-ingest-pipeline'
            #     }
            # }
        )
    else:
        print("Index already exists and no deletion specified")
        
def getEmbedding(text):
    return model.encode(text)

def insert_documents(documents, index):
    print("Starting Insertion")
    operations = []
    for document in documents:
        operations.append({'create': {'_index': index, "_id": document["id"]} })
        operations.append({
            **document,
            "summary_embedding": getEmbedding(document["summary"]),
            "title_embedding": getEmbedding(document["title"]),
        })
        # print(operations[1])
        # break
    
    print("Successfully Completed Insertion")
    return client.bulk(operations=operations)

def upload_to_es(amount, iterations):
    wait_time = 3
    start = client.count(index="search-papers-meta")['count']
    print(f"Total documents in DB, start: {start}\n")
    for i in range(iterations):
        insert_documents(findInfo(start, amount), "search-papers-meta")
        print(f"Uploaded documents {start} - {start + amount}")
        start += amount
        
        print(f'Sleeping for {wait_time} seconds')
        time.sleep(wait_time)
        
    print(f"Total documents in DB, finish: {start}\n")
    
def main(args):
    amount = args.amt
    iterations = args.iter
    if amount > 2000 or amount < 1 or iterations < 1:
        raise Exception("Flag error: please ensure your flag values match the specifications")
    
    upload_to_es(amount, iterations)

if __name__ == "__main__":
    parser = set_parser(program_name,program_usage,program_description,program_epilog,program_version)
    args = parser.parse_args()
    main(args)

# # FIXME: comments, journal_ref, report_number
# There is an Api

# def findInfo(page):
#     start = 50 * (page-1)
#     url = f"https://arxiv.org/search/?query=superconductivity&searchtype=all&abstracts=show&order=&size=50&start={start}"

#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, "html.parser")
#     results_arr = soup.findAll('li', "arxiv-result")
    
#     # print(results_arr)
        
#     papers = []
#     for res in results_arr:
#         paper_dict = {}
#         results = BeautifulSoup(str(res), "html.parser")
        
#         id_tag = results.find('p', class_="list-title is-inline-block")
#         id = id_tag.find('a').get_text(strip=True)
#         paper_dict['id'] = id # id
        
#         title_tag = results.find('p', class_='title is-5 mathjax')
#         title = title_tag.get_text(strip=True, separator=' ') # title
#         paper_dict['title'] = title
        
#         source = results.find('p', class_='list-title is-inline-block')
#         other = source.findAll('a', href=True)
#         links = [a['href'] for a in other]
#         paper_dict['links'] = links
            
#         abstract = results.find('span', class_="abstract-full has-text-grey-dark mathjax")
#         summary = abstract.get_text(strip=True, separator=' ')
#         summary = summary.replace("△ Less", "") # abstract
#         paper_dict['summary'] = summary
        
#         dates = results.find('p', class_='is-size-7')
#         date_text = dates.get_text(separator=' ', strip=True)
#         submitted = date_text.split(';')[0].replace('Submitted', '').strip()
#         split_date = submitted.split(" ") # 1 May 2024
#         months = {"January,": "01", "February,": "02", "March,": "03", "April,": "04", "May,": "05", "June,": "06", "July,": "07", "August,": "08", "September,": "09", "October,": "10", "November,": "11", "December,": "12"}
#         if len(split_date[0]) == 1:
#             truncated_date = f"{split_date[2]}{months[split_date[1]]}0{split_date[0]}"
#         else:
#             truncated_date = f"{split_date[2]}{months[split_date[1]]}{split_date[0]}"
#         date_num = int(truncated_date)
#         paper_dict['date'] = date_num # submission date
#         announced = date_text.split(';')[1].replace('originally announced', '').strip()
#         paper_dict['announced'] = announced # announce date
        
#         journal_tag = results.find('div', class_="tags is-inline-block")
#         journals = [journal.get_text(strip=True) for journal in journal_tag.findAll('span')] # journals
#         paper_dict['journals'] = journals
        
#         author_tag = results.find('p', class_="authors")
#         authors = [author.get_text(strip=True) for author in author_tag.findAll('a')]
#         paper_dict['authors'] = authors # authors
        
#         doi_tag = results.find('span', 'tag is-light is-size-7')
#         if doi_tag:
#             doi = doi_tag.find('a', href=True)['href']
#         else:
#             doi = "N/A"
#         paper_dict['doi'] = doi
        
#         bottom_tag = results.findAll('span', class_="comments is-size-7")
#         if bottom_tag:
#             for tag in bottom_tag:
#                 type = tag.find('span', class_="has-text-black-bis has-text-weight-semibold").get_text(strip=True)
#                 if type == "Journal ref:":
#                     journal_ref = tag.get_text(strip=True)
#                     paper_dict['journal_ref'] = journal_ref
#                 elif type == "Comments:":
#                     comments = tag.find('span', class_="has-text-grey-dark mathjax").get_text(strip=True)
#                     paper_dict['comments'] = comments
#                 elif type == "Report number:":
#                     report_number = tag.get_text(strip=True)
#                     paper_dict['report_number'] = report_number
#         else:
#             paper_dict['journal_ref'] = "N/A"
#             paper_dict['comments'] = "N/A"
#             paper_dict['report_number'] = "N/A"
            
#         # id, title, report_number, comments, journal_ref, doi, authors, journals, announced, submitted
#         # summary, links
                
#         # print(paper_dict)
#         # print("\n\n")
#         papers.append(paper_dict) 
    
#     return papers  


# Code for adding specific categorical searches, 
# category:superconductivity --> This uses superconductivity as a categorical search

# def extract_filters(query):
#     filters = []

#     filter_regex = r'category:([^\s]+)\s*'
#     m = re.search(filter_regex, query)
#     if m:
#         filters.append({
#             'term': {
#                 'category.keyword': {
#                     'value': m.group(1)
#                 }
#             }
#         })
#         query = re.sub(filter_regex, '', query).strip()

#     return {'filter': filters}, query

# Do not have current capacity to use these

# def deploy_elser():
#     # download ELSER v2
#     client.ml.put_trained_model(model_id='.elser_model_2',
#                                     input={'field_names': ['text_field']})
    
#     # wait until ready
#     while True:
#         status = client.ml.get_trained_models(model_id='.elser_model_2',
#                                                 include='definition_status')
#         if status['trained_model_configs'][0]['fully_defined']:
#             # model is ready
#             break
#         time.sleep(1)

#     # deploy the model
#     client.ml.start_trained_model_deployment(model_id='.elser_model_2')

#     # define a pipeline
#     client.ingest.put_pipeline(
#         id='elser-ingest-pipeline',
#         processors=[
#             {
#                 'inference': {
#                     'model_id': '.elser_model_2',
#                     'input_output': [
#                         {
#                             'input_field': 'summary',
#                             'output_field': 'elser_embedding',
#                         }
#                     ]
#                 }
#             }
#         ]
#     )
    
# def deploy_elser_model():
#     try:
#         deploy_elser()
#     except Exception as exc:
#         print(f'Error: {exc}')
#     else:
#         print(f'ELSER model deployed.')

# Do not have permission to scrape from APS

# class Paper:
#     def __init__(self, link: str, title: str, date: str, citation: str, summary: str, authors: str, doi: str, journal: str):
#         self.link = link
#         self.title = title
#         self.date = date
#         self.citation = citation
#         self.summary = summary
#         self.authors = authors
#         self.doi = doi
#         self.journal = journal
        
#     def __init__(self):
#         self.link = ''
#         self.title = ''
#         self.date = ''
#         self.citation = ''
#         self.summary = ''
#         self.authors = ''
#         self.doi = ''
#         self.journal = ''
        
#     def __str__(self):
#         return f"link: {self.link}\ntitle: {self.title}\ndate: {self.date}\ncitation: {self.citation}\nabstract: {self.summary}\nauthors: {self.authors}\ndoi: {self.doi}\njournal: {self.journal}"        

# def findInfo(page) -> list[Paper]:
#     url = f"https://journals.aps.org/search/results?sort=recent&clauses=%5B%7B%22field%22:%22abstitle%22,%22value%22:%22superconductivity%22,%22operator%22:%22AND%22%7D%5D&page={page}&per_page=20"

#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, "html.parser")
#     content = soup.find_all("script")
#     text = ''.join(str(element) for element in content) # possibly unnecessary, join just to split again
#                                                         # consider omitting and just iterating through content
#                                                         # then only keeping those which match html pattern

#     extracted_texts = [part.strip() for part in text.split('"html"') if part.strip()]
#     extracted_texts.pop(0)
        
#     # pattern = r'html(.*?)html'
#     # matches = re.finditer(pattern, text, re.DOTALL) # Issue is here "html" ... "html" ... "html" ... "html"
#                                                     # Only gets the alternates, bc it searches after each tag
    
#     # extracted_texts = [f"{match.group(1)}" for match in matches]
                
#     return assignPaperMetadata(extracted_texts)

# def assignPaperMetadata(extracted_texts: list[str]) -> list[Paper]:
#     papers = []
#     fields = ["link", "title", "date", "citation", "summary", "authors", "doi", "journal"]
    
#     for extracted in extracted_texts:
#         paper = Paper()
            
#         for field in fields:
#             patterns = rf'"{field}":"(.*?)(?=",")'
        
#             matches = re.search(patterns, extracted)
#             field1 = f'No {field} found'
#             if(matches):
#                 field1 = f"{matches.group(1)}"
            
#             if(field == "link"):
#                 field1 = "https://journals.aps.org/" + field1
                
#             decoded_text = field1.encode().decode('unicode-escape').replace('\\"', '"')
                
#             setattr(paper, field, decoded_text)
        
#         exists = False
#         for pub in papers:
#             if(pub.title == paper.title):
#                 exists = True
#                 break
#         if(not exists):
#             papers.append(paper)
            
#     return papers
    
# def upload_documents(start, end):
#     pages = range(start, end)
#     all_papers = []
    
#     for page in pages:
#         papers = findInfo(page)
#         for paper in papers:
#             paper_dict = {
#                 "title": paper.title,
#                 "authors": paper.authors,
#                 "link": paper.link,
#                 "date": paper.date,
#                 "citation": paper.citation,
#                 "doi": paper.doi,
#                 "journal": paper.journal,
#                 "summary": paper.summary
#             }
#             all_papers.append(paper_dict)
#         print(page)
        
#     return all_papers  