from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import re
import json

app = Flask(__name__)
CORS(app)

class Paper:
    def __init__(self, link: str, title: str, date: str, citation: str, summary: str, authors: str, id: int, doi: str, journal: str):
        self.link = link
        self.title = title
        self.date = date
        self.citation = citation
        self.summary = summary
        self.authors = authors
        self.id = id
        self.doi = doi
        self.journal = journal
        
    def __init__(self):
        self.link = ''
        self.title = ''
        self.date = ''
        self.citation = ''
        self.summary = ''
        self.authors = ''
        self.id = -1
        self.doi = ''
        self.journal = ''
        
    def __str__(self):
        return f"link: {self.link}\ntitle: {self.title}\ndate: {self.date}\ncitation: {self.citation}\nabstract: {self.summary}\nauthors: {self.authors}\nid: {self.id}\ndoi: {self.doi}\njournal: {self.journal}"        
        
def findInfo(page) -> list[Paper]:
    url = f"https://journals.aps.org/search/results?sort=recent&clauses=%5B%7B%22field%22:%22abstitle%22,%22value%22:%22superconductivity%22,%22operator%22:%22AND%22%7D%5D&page={page}&per_page=20"

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    content = soup.find_all("script")
    text = ''.join(str(element) for element in content) # possibly unnecessary, join just to split again
                                                        # consider omitting and just iterating through content
                                                        # then only keeping those which match html pattern

    extracted_texts = [part.strip() for part in text.split('"html"') if part.strip()]
    extracted_texts.pop(0)
        
    # pattern = r'html(.*?)html'
    # matches = re.finditer(pattern, text, re.DOTALL) # Issue is here "html" ... "html" ... "html" ... "html"
                                                    # Only gets the alternates, bc it searches after each tag
    
    # extracted_texts = [f"{match.group(1)}" for match in matches]
                
    return assignPaperMetadata(extracted_texts)

def assignPaperMetadata(extracted_texts: list[str]) -> list[Paper]:
    papers = []
    fields = ["link", "title", "date", "citation", "summary", "authors", "doi", "journal"]
    paperIds = [] # id possibly not necessary once DB is setup, because page for each paper will just be DOI
    
    for extracted in extracted_texts:
        paper = Paper()
        if(len(paperIds) == 0):
            id = 0
            setattr(paper, "id", id)
        else:
            id = papers[len(papers)-1].id + 1
            setattr(paper, "id", id)
        paperIds.append(id)
            
        for field in fields:
            patterns = rf'"{field}":"(.*?)(?=",")'
        
            matches = re.search(patterns, extracted)
            field1 = f'No {field} found'
            if(matches):
                field1 = f"{matches.group(1)}"
            
            if(field == "link"):
                field1 = "https://journals.aps.org/" + field1
                
            decoded_text = field1.encode().decode('unicode-escape').replace('\\"', '"')
                
            setattr(paper, field, decoded_text)
        
        exists = False
        for pub in papers:
            if(pub.title == paper.title):
                exists = True
                break
        if(not exists):
            papers.append(paper)
            
    return papers

def get_all_papers():
    pages = range(1, 625)
    all_papers = []
    
    for page in pages:
        papers = findInfo(page)
        for paper in papers:
            paper_dict = {
                "title": paper.title,
                "authors": paper.authors,
                "link": paper.link,
                "date": paper.date,
                "citation": paper.citation,
                "doi": paper.doi,
                "journal": paper.journal,
                "summary": paper.summary
            }
            all_papers.append(paper_dict)
        print(page)
        
    with open('papers.json', 'w') as file:
        json.dump(all_papers, file, indent=4)
                
# get_all_papers() 

# /api/papers/${paperId}
@app.route('/api/papers/<paper_id>', methods=['POST'])
def get_paper(paper_id):
    data = request.get_json()
    page = int(data.get('page', 0))
    papers = findInfo(page)
    # paper = next((paper for paper in papers if paper.doi.replace("/", "-") == str(paper_id)), None)
    paper = next((paper for paper in papers if paper.id == int(paper_id)), None)
    if(paper == None):
        paper = Paper()
        print("ID not correct")
    paper_dict = paper.__dict__
    if paper:
        return jsonify(paper_dict)
    else:
        return jsonify({"error": "Paper not found"}), 404
    
# /api/papers
@app.route("/api/papers", methods=['POST'])
def papers():
    data = request.get_json()
    page = int(data.get('page', 0))
    papers = findInfo(page)
    papers_dict = [paper.__dict__ for paper in papers]
    papers_json = json.dumps(papers_dict)
    return jsonify(papers_dict)

if __name__ == "__main__":
    app.run(debug=True, port=8080)