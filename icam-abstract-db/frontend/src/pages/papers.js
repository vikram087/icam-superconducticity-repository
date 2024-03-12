import '../styles/papers.css';
import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom';
import ReactPaginate from 'react-paginate';
import { TailSpin } from 'react-loader-spinner';

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
    paper ? 
      <div className='paper'>
        <div className='button'>
          <button className='return' onClick={goBack}>Go Back</button>
        </div>
          <div dangerouslySetInnerHTML={{ __html: `<u>${paper.title}</u>` }}></div>
        <p><strong>Authors:</strong> {paper.authors}</p>
        <a href={paper.link} target='_blank' rel="noreferrer">
          <p><strong>DOI:</strong> {paper.doi}</p>
        </a>
        <p><strong>Journal:</strong> {paper.journal}</p>
        <p><strong>Date:</strong> {paper.date}</p>
        <div dangerouslySetInnerHTML={{ __html: `<strong>Citation:</strong> ${paper.citation}` }}></div>
        <div className='abstract' dangerouslySetInnerHTML={{ __html: `<strong>Abstract:</strong> ${paper.summary}` }}></div>
      </div>
    :
    <div className='loader'>
      <p>Loading ...</p>
      <TailSpin color="#00BFFF" height={100} width={100} />
    </div>
  );
}

export function Papers() {
  const [papers, setPapers] = useState([]);
  const [page, setPage] = useState(1)
  const pageCount = 250;
  // const [currentPage, setCurrentPage] = useState(0);
  const [expandedIndex, setExpandedIndex] = useState(-1);

  const toggleExpand = (index) => {
    if (expandedIndex === index) {
      setExpandedIndex(-1);
    } else {
      setExpandedIndex(index);
    }
  }


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
    // let doi = paperId.replace(/\//g, "-");
    // navigate(`/papers/${doi}`);
    navigate(`/papers/${paperId}`);
  }

  const handlePageClick = (data) => {
    let selectedPage = data.selected;
    // setCurrentPage(selectedPage);
    setPapers([]);
    changePage(selectedPage+1);
  };

  return (
    <div>
      <ReactPaginate
        previousLabel={'previous'}
        nextLabel={'next'}
        breakLabel={'...'}
        breakClassName={'break-me'}
        pageCount={pageCount}
        marginPagesDisplayed={2}
        pageRangeDisplayed={5}
        onPageChange={handlePageClick}
        containerClassName={'pagination'}
        activeClassName={'active'}
        // initialPage={currentPage}
        // forcePage={currentPage} 
      />
      <ul className="list">
        {papers.length !== 0 ?
          papers.map((paper, index) => (
            // <div className='container' key={index} onClick={() => changePaper(paper.doi)}>
            <div className={index === expandedIndex ? 'expanded-container' : 'container'} key={index}>
              <div onClick={() => changePaper(paper.id)}>
                  <u>
                    <div dangerouslySetInnerHTML={{ __html: paper.title }}></div>
                  </u>
                  <p>Authors: {paper.authors}</p>
                  <div>Abstract: </div>
              </div>
              <div className='expand-button'>
                <button onClick={() => toggleExpand(index)}>
                  {expandedIndex === index ? '-' : '+'}
                </button>
              </div>
              {expandedIndex === index ?
                <div onClick={() => changePaper(paper.id)}>
                  <div dangerouslySetInnerHTML={{ __html: `${paper.summary}` }} className={expandedIndex === index ? 'text expanded' : 'text'}></div>
                </div>
                :
                <div>
                  <div dangerouslySetInnerHTML={{ __html: `${paper.summary}` }} className={expandedIndex === index ? 'text expanded' : 'text'}></div>
                </div>
              }
            </div>
          )) :
          <div className='loader'>
            <p>Loading ...</p>
            <TailSpin color="#00BFFF" height={100} width={100} />
          </div>
        }
      </ul>
    </div>
  );
}