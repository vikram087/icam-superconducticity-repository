from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import re
import json

app = Flask(__name__)
CORS(app)

class Paper:
    def __init__(self, link: str, title: str, date: str, citation: str, summary: str):
        self.link = link
        self.title = title
        self.date = date
        self.citation = citation
        self.summary = summary
        
    def __init__(self):
        self.link = ''
        self.title = ''
        self.date = ''
        self.citation = ''
        self.summary = ''
        
    def __str__(self):
        return f"link: {self.link}\ntitle: {self.title}\ndate: {self.date}\ncitation: {self.citation}\nabstract: {self.summary}"        
        
def findInfo(page) -> list[Paper]:
    url = f"https://journals.aps.org/search/results?sort=recent&clauses=%5B%7B%22field%22:%22abstitle%22,%22value%22:%22superconductivity%22,%22operator%22:%22AND%22%7D%5D&page={page}&per_page=20"

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    content = soup.find_all("script")
    text = ''.join(str(element) for element in content)
    
    pattern = r'html(.*?)html'
    matches = re.finditer(pattern, text, re.DOTALL)

    extracted_texts = [f"{match.group(1)}" for match in matches]
            
    return assignPaperMetadata(extracted_texts)

def assignPaperMetadata(extracted_texts: list[str]) -> list[Paper]:
    papers = []
    fields = ["link", "title", "date", "citation", "summary"]
    
    for extracted in extracted_texts:
        paper = Paper()
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
            
        papers.append(paper)
            
    return papers
    
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