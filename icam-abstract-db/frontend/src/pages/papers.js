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
    navigate(`/papers?page=${searchParams.page}&per_page=${searchParams.per_page}&query=${searchParams.query}&sort=${searchParams.sorting}&journals=${searchParams.journals}`);
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
  const [selected, setSelected] = useState([]);

  const navigate = useNavigate();
  
  const journals = {
    "Phys. Rev. B": "PRB",
    "Phys. Rev. Lett.": "PRL",
    "Phys. Rev.": "PR",
    "Phys. Rev. D": "PRD",
    "Phys. Rev. Materials": "PRMATERIALS",
    "Phys. Rev. Research": "PRRESEARCH",
    "Phys. Rev. X": "PRX",
    "Rev. Mod. Phys.": "RMP",
    "Phys. Rev. A": "PRA",
    "Phys. Rev. C": "PRC",
    "Phys. Rev. Applied": "PRAPPLIED",
    "Physics": "PHYSICS",
    "Phys. Rev. E": "PRE",
    "Phys. Rev. Focus": "FOCUS",
    "Phys. Rev. Accel. Beams": "PRAB",
    "Phys. Rev. ST Accel. Beams": "PRSTAB",
    "Physics Physique Fizika": "PPF",
    "PRX Quantum": "PRXQUANTUM",
    "PRX Energy": "PRXENERGY",
    "PRX Life": "PRXLIFE",
    "Phys. Rev. Fluids": "PRFLUIDS",
    "Phys. Rev. Phys. Educ. Res.": "PRPER",
    "Phys. Rev. ST Phys. Educ. Res.": "PRSTPER",
    "Phys. Rev. (Series I)": "PRI"
  };

  //FIXME: Add support to searchParams for journals selection
  const handleJournals = (value, isChecked) => {
    setSelected(prevParams => {
      const newSelected = isChecked ? [...prevParams, value] : prevParams.filter(item => item !== value);
      const journalsParam = newSelected.join(',');

      const newUrl = newSelected.length > 0
        ? `?page=${searchParams.page}&per_page=${searchParams.per_page}&query=${searchParams.query}&sort=${searchParams.sorting}&journals=${journalsParam}`
        : `?page=${searchParams.page}&per_page=${searchParams.per_page}&query=${searchParams.query}&sort=${searchParams.sorting}&journals=None`;

      navigate(newUrl);

      return newSelected;
    });
  };

  const results = ["No Selection", "20", '10', "50", "100"];

  const order = ["No Selection", "Most Recent", "Oldest First", "Most Relevant"];

  const sort = (e) => {
    let sorting = e.target.value;

    if(sorting === "Most Relevant" || sorting === "No Selection") {
      sorting = "Most Recent";
    }

    const modified = sorting.replace(" ", "-");

    navigate(`?page=${searchParams.page}&per_page=${searchParams.per_page}&query=${searchParams.query}&sort=${modified}&journals=${searchParams.journals}`);
  };

  const changeResultsPerPage = (e) => {
    let resultsPerPage = e.target.value;
    if(resultsPerPage === "No Selection") {
      resultsPerPage = "20";
    }

    navigate(`?page=${searchParams.page}&per_page=${resultsPerPage}&query=${searchParams.query}&sort=${searchParams.sorting}&journals=${searchParams.journals}`);
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
      {Object.entries(journals).map(([key, value], index) => (
        <div key={index} className='journals'>
          <input onClick={(e) => handleJournals(value, e.target.checked)} type="checkbox"></input>
          {key}
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
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

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
    let journals = query.get('journals') || searchParams.journals;

    setSearchParams({
      per_page: perPage,
      page: page,
      query: search,
      sorting: sorting,
      journals: journals
    });

    setLoading(true);

    getPapers(page, perPage, search, sorting, journals);
  }, [location.search]);

  const getPapers = (page, results, query, sorting, journals) => {
    fetch("http://localhost:8080/api/papers", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ "page": page, "results": results, "query": query, "sorting": sorting, "journals": journals }),
    })
    .then(response => response.json())
    .then(data => {
      setPapers(data.papers);
      setTotal(data.total);
      setPageCount(data.total/searchParams.per_page);

      if (window.MathJax) {
        window.MathJax.typesetPromise().then(() => {
          console.log("MathJax typesetting complete");
        }).catch((err) => console.error('MathJax typesetting failed: ', err));
      }

      setLoading(false);
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

    getPapers(page, searchParams.per_page, searchParams.query, searchParams.sorting, searchParams.journals);
    window.page = page;
    navigate(`?page=${page}&per_page=${searchParams.per_page}&query=${searchParams.query}&sort=${searchParams.sorting}&journals=${searchParams.journals}`);
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

  const chooseBody = () => {
    if(!loading && total === undefined) {
      return <div>No Results Found or Incorrect Search Query</div>;
    }
    else if(!loading) {
      console.log(total);
      return papers.map((paper, index) => (
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
      ))
    }
    else if(loading) {
      return <div className='loader'>
        <p>Loading ...</p>
        <TailSpin color="#00BFFF" height={100} width={100} />
      </div>
    }
  }

  return (
    <div>
      <p className='title' onClick={() => navigate("/")}>ICAM Superconductivity Database</p>
      <Search searchParams={searchParams} papers={papers}/>
      <div className='page-container'>
        <div className='filters'>
          <Filters searchParams={searchParams} />
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
          {!loading && (<p>{total} Results</p>)}
          <ul className="list">
            {chooseBody()}
          </ul>
        </div>
      </div>
    </div>
  );
}