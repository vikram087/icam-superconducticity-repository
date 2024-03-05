import '../styles/papers.css';
import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom';

window.page = 0;

export function PaperDetail() {
  const [paper, setPaper] = useState(null);

  let navigate = useNavigate();
  let { id } = useParams();

  useEffect(() => {
    fetch(`http://localhost:8080/api/papers/${id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ "page": window.page }),
    })
    .then((response) => response.json())
    .then(data => {
      setPaper(data);
    })
  }, [id]);

  function goBack() {
    navigate(`/papers`);
  }

  return (
    paper && (
      <div className='paper'>
        <div className='button'>
          <button className='return' onClick={goBack}>Go Back</button>
        </div>
        <a href={paper.link} target='_blank' rel="noreferrer">
          <div dangerouslySetInnerHTML={{ __html: paper.title }}></div>
        </a>
        <p>Authors: {paper.authors}</p>
        <p>Date: {paper.date}</p>
        <div dangerouslySetInnerHTML={{ __html: `Citation: ${paper.citation}` }}></div>
        <div className='abstract' dangerouslySetInnerHTML={{ __html: `Abstract: ${paper.summary}` }}></div>
      </div>
    )
  );
}

export function Papers() {
  const [papers, setPapers] = useState([]);
  const [page, setPage] = useState(1)

  let navigate = useNavigate();

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
    window.page = page;
  };

  function changePaper(paperId) {
    navigate(`/papers/${paperId}`);
  }

  return (
    <div>
      <button onClick={() => changePage(page-1)}>&lt;</button>
      <button onClick={() => changePage(page+1)}>&gt;</button>
      <ul className="list">
        {papers.map((paper, index) => (
          <div className='container' key={index} onClick={() => changePaper(paper.id)}>
            <a href={paper.link} target='_blank' rel="noreferrer">
              <div dangerouslySetInnerHTML={{ __html: paper.title }}></div>
            </a>
            <p>Authors: {paper.authors}</p>
            <div dangerouslySetInnerHTML={{ __html: `Abstract: ${paper.summary}` }}></div>
          </div>
        ))}
      </ul>
    </div>
  );
}