import '../styles/papers.css';
import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { TailSpin } from 'react-loader-spinner';
import { Search } from './homepage';
import { MathJax, MathJaxContext } from "better-react-mathjax";

const numToDate = (date) => {
  const monthsReversed = {"01": "January,", "02": "February,", "03": "March,", "04": "April,", "05": "May,", "06": "June,", "07": "July,", "08": "August,", "09": "September,", "10": "October,", "11": "November,", "12": "December,"};
  const year = date.substring(0, 4);
  const month = monthsReversed[date.substring(4, 6)];
  const day = date.substring(6);

  return day + " " + month + " " + year;
};

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
    navigate(`/papers?page=${searchParams.page}&per_page=${searchParams.per_page}&query=${searchParams.query}&sort=${searchParams.sorting}&pages=${searchParams.pages}`);
  };

  const replaceID = (id) => {
    let lastIndex = id.lastIndexOf('-');
    
    if (lastIndex !== -1) {
        return id.substring(0, lastIndex) + '/' + id.substring(lastIndex + 1);
    }
    else {
      return id;
    }
  };

  return (
    paper ? 
      <div className='paper'>
        <div className='button'>
          <button className='return' onClick={goBack}>Go Back</button>
        </div>
        <u><Content content={paper.title}/></u>
        <p><strong>Authors:</strong> {paper.authors.map((author, index) => (
          <span key={index}>
            {author}{index < paper.authors.length - 1 ? ', ' : ''}
          </span>
        ))}</p>       
        <p><strong>arXiv ID:</strong> {replaceID(paper.id)}</p>
        <p><strong>DOI:</strong> {paper.doi}</p>
        <strong>Links:</strong>
        {paper.links.map(link => <a href={link} target='_blank' rel="noreferrer"><br></br>{link}</a>)}
        <p><strong>Categories:</strong> {paper.categories.map((category, index) => (
          <span key={index}>
            {category}{index < paper.categories.length - 1 ? ', ' : ''}
          </span>
        ))}</p>     
        <p><strong>Submission Date:</strong> {numToDate((String) (paper.date))}</p>
        <p><strong>Update Date:</strong> {numToDate((String) (paper.updated))}</p>
        <p><strong>Comments:</strong> {paper.comments}</p>
        <p><strong>Primary Category:</strong> {paper.primary_category}</p>
        <p><strong>Journal Ref:</strong> {paper.journal_ref}</p>
        <div className='abstract'><strong>Abstract:</strong> <br></br><Content content={paper.summary}/></div>
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
  const location = useLocation();

  const [pageNumber, setPageNumber] = useState(searchParams.pages || 30);
  const [sortVal, setSortVal] = useState(searchParams.sorting || 'Most-Relevant');
  const [numResults, setNumResults] = useState(searchParams.per_page || 20);

  const [results, setResults] = useState([20, 10, 50, 100]);
  const [order, setOrder] = useState(["Most-Relevant", "Most-Recent", "Oldest-First"]);

  useEffect(() => {
    const query = new URLSearchParams(location.search);
    let perPage = (Number) (query.get('per_page')) || numResults;
    let sorting = query.get('sort') || sortVal;
    let pages = (Number) (query.get('pages')) || pageNumber;

    const updatedResults = results.filter(r => r !== perPage);
    updatedResults.unshift(perPage);

    if(sorting !== "Most-Recent" && sorting !== "Oldest-First" && sorting !== "Most-Relevant") {
      sorting = "Most-Relevant";
    }

    const updatedOrder = order.filter(r => r !== sorting);
    updatedOrder.unshift(sorting);

    setNumResults(perPage);
    setSortVal(sorting);
    setPageNumber(pages);

    setResults(updatedResults);
    setOrder(updatedOrder);
  }, []);

  const handleButton = () => {
    let pageValue = pageNumber;
    if(pageNumber === "") {
      setPageNumber(30);
      pageValue = 30;
    }
    navigate(`?page=${searchParams.page}&per_page=${numResults}&query=${searchParams.query}&sort=${sortVal}&pages=${pageValue}`);
  };

  const handleInputChange = (event) => {
    const val = event.target.value;
    if(val > 0 || val === "") {
      setPageNumber(val);
    }
  };

  return (
    <div>
      <b>Sort</b>
      <br></br>
      <div className='results-per-page'>
        <select onChange={(e) => setSortVal(e.target.value.replace(" ", "-"))}>
          {order.map((option, index) => (
              <option key={index} value={option}>{option.replace("-", " ")}</option>
          ))}
        </select>
      </div>
      <br></br>
      <b>Results Per Page</b>
      <br></br>
      <div className='results-per-page'>
        <select onChange={(e) => setNumResults(e.target.value)}>
          {results.map((option, index) => (
              <option key={index} value={option}>{option}</option>
          ))}
        </select>
      </div>
      <br></br>
      <b>Page Limit</b>
      <br></br>
      <br></br>
      <input 
        type="number"
        min={1}
        value={pageNumber}
        onChange={handleInputChange}
      ></input>
      <br></br>
      <br></br>
      <button onClick={handleButton} style={{ cursor: "pointer" }}>Submit</button>
    </div>
  );
}

export function Papers ({ searchParams, setSearchParams }) {
  const location = useLocation();

  const [papers, setPapers] = useState([]);
  const [pageCount, setPageCount] = useState(0);
  // const pageCount = 250;
  const [expandedIndex, setExpandedIndex] = useState(-1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [accuracy, setAccuracy] = useState({});
  const [time, setTime] = useState("");

  const navigate = useNavigate();

  const toggleExpand = (index) => {
    if (expandedIndex === index) {
      setExpandedIndex(-1);
    } else {
      setExpandedIndex(index);
    }
  }

  const getPapers = useCallback((page, results, query, sorting, startTime, pages) => {
    fetch("http://localhost:8080/api/papers", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ "page": page, "results": results, "query": query, "sorting": sorting, "pages": pages }),
    })
    .then(response => response.json())
    .then(data => {
      setExpandedIndex(-1);
      setPapers(data.papers);
      setTotal(data.total);
      setAccuracy(data.accuracy);
      setPageCount(Math.ceil(data.total/searchParams.per_page));
      if(data.total === undefined) {
        setTotal(0);
        setPapers([]);
      }

      // if (window.MathJax) {
      //   window.MathJax.typesetPromise().then(() => {
      //     console.log("MathJax typesetting complete");
      //   }).catch((err) => console.error('MathJax typesetting failed: ', err));
      // }

      setLoading(false);

      const endTime = performance.now();

      const totalTimeS = (endTime - startTime)/1000;
      const totalTime = totalTimeS.toFixed(2);
      setTime(totalTime);
    })
    .catch(error => {
      console.error('Error fetching papers:', error);
    });
  }, [searchParams.per_page]);

  useEffect(() => {
    const query = new URLSearchParams(location.search);
    let page = (Number) (query.get('page')) || searchParams.page;
    let perPage = (Number) (query.get('per_page')) || searchParams.per_page;
    let search = query.get('query') || searchParams.query;
    let sorting = query.get('sort') || searchParams.sorting;
    let pages = (Number) (query.get('pages')) || searchParams.pages;

    if(perPage >= 100) { perPage = 100 }
    else if(perPage >= 50) { perPage = 50; }
    else if(perPage >= 20) { perPage = 20; }
    else { perPage = 10; }

    if(sorting !== "Most-Recent" && sorting !== "Oldest-First" && sorting !== "Most-Relevant") {
      sorting = "Most-Relevant";
    }

    if(!Number.isInteger(page) || page <= 0) {
      page = 1;
    }

    if(!Number.isInteger(pages) || pages <= 0) {
      pages = 30;
    }

    navigate(`?page=${page}&per_page=${perPage}&query=${search}&sort=${sorting}&pages=${pages}`);

    // if(page > total/perPage) {
    //   page = total/perPage;
    // }

    setSearchParams({
      per_page: perPage,
      page: page,
      query: search,
      sorting: sorting,
      pages,
    });

    const startTime = performance.now();

    setLoading(true);

    getPapers(page, perPage, search, sorting, startTime, pages);
  }, [location.search, getPapers, searchParams.page, searchParams.per_page, searchParams.query, searchParams.sorting, searchParams.pages, setSearchParams]);

  const changePage = (page) => {
    setSearchParams(prevParams => ({
      ...prevParams,
      page: page
    }));

    const startTime = performance.now();

    getPapers(page, searchParams.per_page, searchParams.query, searchParams.sorting, startTime, searchParams.pages);
    navigate(`?page=${page}&per_page=${searchParams.per_page}&query=${searchParams.query}&sort=${searchParams.sorting}&pages=${searchParams.pages}`);
  };

  const changePaper = (paperId) => {
    navigate(`/papers/${paperId}`);
  }

  const handlePageClick = (pageNumber) => {
    setPapers([]);
    changePage(pageNumber);
  };

  const chooseBody = () => {
    if(!loading && total === 0) {
      return <></>;
    }
    else if(!loading) {
      return papers.map((paper, index) => (
        <div className={index === expandedIndex ? 'expanded-container' : 'container'} key={index}>
          {accuracy[paper.id] && (<div style={{ paddingBottom: "3px" }}>Query Match Accuracy: {(accuracy[paper.id]*100).toFixed(1)}%</div>)}
          <div onClick={() => changePaper(paper.id.replace("/-/g", '/'))}>
              <u><div><Content content={paper.title}/></div></u>
              <p><strong>Authors:</strong> {paper.authors.map((author, index) => (
                <span key={index}>
                  {author}{index < paper.authors.length - 1 ? ', ' : ''}
                </span>
              ))}</p> 
          <strong>Abstract: </strong>
          </div>
          <div className='expand-button'>
            <button onClick={() => toggleExpand(index)}>
              {expandedIndex === index ? '-' : '+'}
            </button>
          </div>
          {expandedIndex === index ?
            <div onClick={() => changePaper(paper.id)} className={expandedIndex === index ? 'text expanded' : 'text'}><Content content={paper.summary}/></div>
            :
            <div className={expandedIndex === index ? 'text expanded' : 'text'}><Content content={paper.summary}/></div>
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
          <Pagination handlePageClick={handlePageClick} page={searchParams.page} totalPages={pageCount} />
          {!loading && (<p>{total} Results in {time} seconds</p>)}
          <ul className="list">
            {chooseBody()}
          </ul>
        </div>
      </div>
    </div>
  );
}

function Pagination({ handlePageClick, page, totalPages }) {

  const [pageNumber, setPageNumber] = useState(page);

  const handleBack = () => {
    if(page >= 2) {
      handlePageClick(page-1);
      setPageNumber(page-1);
    }
  };

  const handleFront = () => {
    if(page <= totalPages-1) {
      handlePageClick((Number)(page)+1);
      setPageNumber((Number)(page)+1);
    }
  };

  const handleNumber = (pageNumber) => {
    if((Number)(page) !== pageNumber) {
      handlePageClick(pageNumber);
      setPageNumber(pageNumber);
    }
  };

  const handleSubmit = (event) => {
    if(event.key === "Enter" && page !== pageNumber) {
      if(pageNumber < 2 && page > 1) {
        handlePageClick(1);
        setPageNumber(1);
      }
      else if(pageNumber > totalPages-1 && page < totalPages) {
        handlePageClick(totalPages);
        setPageNumber(totalPages);
      }
      else if(pageNumber <= totalPages-1 && pageNumber >= 2) {
        handlePageClick(pageNumber);   
        setPageNumber(pageNumber);
      }   
    }
  };

  const handleInputChange = (event) => {
    setPageNumber(event.target.value);
  };  

  return (
    <div className='pagination-container'>
      <span style={{cursor: "pointer" }} onClick={() => handleNumber(1)}>&lt;&lt;&nbsp;</span>
      <span style={{cursor: "pointer" }} onClick={handleBack}>&nbsp;&lt;&nbsp;</span>
      <input 
        type="number"
        onKeyDown={handleSubmit}
        value={pageNumber}
        onChange={handleInputChange}
      ></input>
      <span style={{cursor: "pointer" }} onClick={handleFront}>&nbsp;&gt;&nbsp;</span>
      <span style={{cursor: "pointer" }} onClick={() => handleNumber(totalPages)}>&nbsp;&gt;&gt;&nbsp;</span>
    </div>
  );
}

const Content = ({ content }) => {
  const config = {
    loader: { load: ["[tex]/html"] },
    tex: {
      packages: { "[+]": ["html"] },
      inlineMath: [
        ["$", "$"],
        ["\\(", "\\)"]
      ],
      displayMath: [
        ["$$", "$$"],
        ["\\[", "\\]"]
      ]
    }
  };

  return (
    <MathJaxContext version={3} config={config}>
      <MathJax hideUntilTypeset={"first"}>
          {`${content}`}
      </MathJax>
    </MathJaxContext>
  );
};