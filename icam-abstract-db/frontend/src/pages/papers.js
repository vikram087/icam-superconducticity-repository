import '../styles/papers.css';
import React, { useState, useEffect } from 'react'
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import ReactPaginate from 'react-paginate';
import { TailSpin } from 'react-loader-spinner';
import { Search } from './homepage';

window.page = 0;

export function PaperDetail({ searchParams }) {
  const [paper, setPaper] = useState(null);

  let navigate = useNavigate();
  let { id } = useParams();

  useEffect(() => {
    fetch(`http://localhost:8080/api/papers/${id}`)
    .then((response) => response.json())
    .then(data => {
      setPaper(data);
    })
  }, [id]);

  const goBack = () => {
    navigate(`/papers?page=${searchParams.page}&per_page=${searchParams.per_page}&query=${searchParams.query}&sort=${searchParams.sorting}`);
  };

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

function Filters({ searchParams }) {
  const navigate = useNavigate();
  
  const journals = [
    "Phys. Rev. B",
    "Phys. Rev. Lett.",
    "Phys. Rev.",
    "Phys. Rev. D",
    "Phys. Rev. Materials",
    "Phys. Rev. Research",
    "Phys. Rev. X",
    "Rev. Mod. Phys.",
    "Phys. Rev. A",
    "Phys. Rev. C",
    "Phys. Rev. Applied",
    "Physics",
    "Phys. Rev. E",
    "Phys. Rev. Focus",
    "Phys. Rev. Accel. Beams",
    "Phys. Rev. ST Accel. Beams",
    "Physics Physique Fizika",
    "PRX Quantum",
    "PRX Energy",
    "PRX Life",
    "Phys. Rev. Fluids",
    "Phys. Rev. Phys. Educ. Res.",
    "Phys. Rev. ST Phys. Educ. Res.",
    "Phys. Rev. (Series I)"
  ];

  const results = ["No Selection", "20", '10', "50", "100"];

  const order = ["No Selection", "Most Recent", "Oldest First", "Most Relevant"];

  const sort = (e) => {
    let sorting = e.target.value;

    if(sorting === "Most Relevant" || sorting === "No Selection") {
      sorting = "Most Recent";
    }

    const modified = sorting.replace(" ", "-");

    navigate(`?page=${searchParams.page}&per_page=${searchParams.per_page}&query=${searchParams.query}&sort=${modified}`);
  };

  const changeResultsPerPage = (e) => {
    let resultsPerPage = e.target.value;
    if(resultsPerPage === "No Selection") {
      resultsPerPage = "20";
    }

    navigate(`?page=${searchParams.page}&per_page=${resultsPerPage}&query=${searchParams.query}&sort=${searchParams.sorting}`);
  };

  return (
    <div>
      <u>Sort</u>
      <br></br>
      <div className='results-per-page'>
        <select onChange={sort}>
          {order.map((option, index) => (
              <option key={index} value={option}>{option}</option>
          ))}
        </select>
      </div>
      <br></br>
      <u>Results Per Page</u>
      <br></br>
      <div className='results-per-page'>
        <select onChange={changeResultsPerPage}>
          {results.map((option, index) => (
              <option key={index} value={option}>{option}</option>
          ))}
        </select>
      </div>
      <br></br>
      <u>Journal</u>
      {journals.map((journal, index) => (
        <div  key={index} className='journals'>
          <input type="checkbox"></input>
          {journal}
        </div>
      ))}
    </div>
  );
}

export function Papers({ searchParams, setSearchParams }) {
  const location = useLocation();

  const [papers, setPapers] = useState([]);
  const [pageCount, setPageCount] = useState(250);
  // const pageCount = 250;
  const [expandedIndex, setExpandedIndex] = useState(-1);

  const navigate = useNavigate();

  const toggleExpand = (index) => {
    if (expandedIndex === index) {
      setExpandedIndex(-1);
    } else {
      setExpandedIndex(index);
    }
  }

  useEffect(() => {
    const query = new URLSearchParams(location.search);
    let page = query.get('page') || searchParams.page;
    let perPage = query.get('per_page') || searchParams.per_page;
    let search = query.get('query') || searchParams.query;
    let sorting = query.get('sort') || searchParams.sorting;

    setSearchParams({
      per_page: perPage,
      page: page,
      query: search,
      sorting: sorting
    });

    getPapers(page, perPage, search, sorting);
  }, [searchParams.page, searchParams.per_page, searchParams.sorting, setSearchParams, searchParams.query, location]);

  const getPapers = (page, results, query, sorting) => {
    fetch("http://localhost:8080/api/papers", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ "page": page, "results": results, "query": query, "sorting": sorting }),
    })
    .then(response => response.json())
    .then(data => {
      setPapers(data.papers);
      setPageCount(data.total/searchParams.per_page);
      // setPapers(data);

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
    setSearchParams(prevParams => ({
      ...prevParams,
      page: page
    }));

    getPapers(page, searchParams.per_page, searchParams.query, searchParams.sorting);
    window.page = page;
    navigate(`?page=${page}&per_page=${searchParams.per_page}&query=${searchParams.query}&sort=${searchParams.sorting}`);
  };

  const changePaper = (paperId) => {
    let doi = paperId.replace(/\//g, "-");
    navigate(`/papers/${doi}`);
  }

  const handlePageClick = (data) => {
    let selectedPage = data.selected;
    setPapers([]);
    changePage(selectedPage+1);
  };

  return (
    <div>
      <Search />
      <div className='page-container'>
        <div className='filters'>
          <Filters searchParams={searchParams} papers={papers} />
        </div>
        <div className='content-area'>
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
            forcePage={searchParams.page-1} 
          />
          <ul className="list">
            {papers.length !== 0 ?
              papers.map((paper, index) => (
                <div className={index === expandedIndex ? 'expanded-container' : 'container'} key={index}>
                  <div onClick={() => changePaper(paper.doi)}>
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
                    <div onClick={() => changePaper(paper.doi)}>
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
      </div>
    </div>
  );
}