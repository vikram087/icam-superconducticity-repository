import '../styles/App.css';
import React, { useState, useEffect } from 'react'

function App() {
  const [papers, setPapers] = useState([]);
  const [page, setPage] = useState(1)

  useEffect(() => {
    getPapers(page);
  }, [page]);

  const getPapers = (page) => {
    fetch("http://localhost:8080/api/papers", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ "page": page }),
    })
    .then(response => response.json())
    .then(data => {
      setPapers(data);

      if (window.MathJax) {
        window.MathJax.typesetPromise().then(() => {
          console.log("MathJax typesetting complete");
        }).catch((err) => console.error('MathJax typesetting failed: ', err));
      }
    })
    .catch(error => {
      console.error('Error fetching papers:', error);
    });
  }

  const changePage = (page) => {
    getPapers(page);
    setPage(page);
  };

  return (
    <div>
      <button onClick={() => changePage(page-1)}>&lt;</button>
      <button onClick={() => changePage(page+1)}>&gt;</button>
      <ul>
        {papers.map((paper, index) => (
          <li key={index}>
            <a href={paper.link} target='_blank' rel="noreferrer">
              <div dangerouslySetInnerHTML={{ __html: paper.title }}></div>
            </a>
            <p>Date: {paper.date}</p>
            <div>
              <div dangerouslySetInnerHTML={{ __html: `Citation: ${paper.citation}` }}></div>
            </div>
            <div>
              <div dangerouslySetInnerHTML={{ __html: `Abstract: ${paper.summary}` }}></div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;