import { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { TailSpin } from 'react-loader-spinner';
import Search from '../components/search.jsx';
import Content from '../components/mathjax.jsx';
import Pagination from '../components/pagination.jsx';
import Filters from '../components/filters.jsx';
import '../styles/papers.css';

function Papers({ searchParams, setSearchParams }) {
  const location = useLocation();

  const [papers, setPapers] = useState([]);
  const [pageCount, setPageCount] = useState(0);
  // const pageCount = 250;
  const [expandedIndex, setExpandedIndex] = useState(-1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [accuracy, setAccuracy] = useState({});
  const [time, setTime] = useState('');

  const navigate = useNavigate();

  const toggleExpand = (index) => {
    if (expandedIndex === index) {
      setExpandedIndex(-1);
    } else {
      setExpandedIndex(index);
    }
  };

  const getPapers = useCallback(
    (page, results, query, sorting, startTime, pages, term, dateRange) => {
      fetch('http://localhost:8080/api/papers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          page: page,
          results: results,
          query: query,
          sorting: sorting,
          pages: pages,
          term: term,
          date: dateRange,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          setExpandedIndex(-1);
          setPapers(data.papers);
          setTotal(data.total);
          setAccuracy(data.accuracy);
          setPageCount(Math.ceil(data.total / searchParams.per_page));
          if (data.total === undefined) {
            setTotal(0);
            setPapers([]);
          }

          setLoading(false);

          const endTime = performance.now();

          const totalTimeS = (endTime - startTime) / 1000;
          const totalTime = totalTimeS.toFixed(2);
          setTime(totalTime);
        })
        .catch((error) => {
          console.error('Error fetching papers:', error);
        });
    },
    [searchParams.per_page],
  );

  useEffect(() => {
    const query = new URLSearchParams(location.search);
    let page = Number(query.get('page')) || searchParams.page;
    let perPage = Number(query.get('per_page')) || searchParams.per_page;
    const search = query.get('query') || searchParams.query;
    let sorting = query.get('sort') || searchParams.sorting;
    let pages = Number(query.get('pages')) || searchParams.pages;
    let term = query.get('term') || searchParams.term;

    let date = query.get('date') || searchParams.date;
    let startDate = date.split("-")[0];
    let endDate = date.split("-")[1];

    const currentDate = new Date();
    const now = currentDate.toISOString().slice(0, 10).replaceAll(/-/g, '');

    if(date.split("-").length !== 2) {
      date = `00000000-${now}`;
    }

    if(isNaN(Number(startDate)) || startDate.length !== 8) {
      startDate = `00000000`;
      date = `${startDate}-${endDate}`;
    }
    if(isNaN(Number(endDate)) || endDate.length !== 8) {
      endDate = now;
      date = `${startDate}-${endDate}`;
    }

    if (perPage >= 100) {
      perPage = 100;
    } else if (perPage >= 50) {
      perPage = 50;
    } else if (perPage >= 20) {
      perPage = 20;
    } else {
      perPage = 10;
    }

    if (
      sorting !== 'Most-Recent' &&
      sorting !== 'Oldest-First' &&
      sorting !== 'Most-Relevant'
    ) {
      sorting = 'Most-Relevant';
    }

    if (
      term !== 'Abstract' &&
      term !== 'Title' &&
      term !== 'Category' &&
      term !== 'Authors'
    ) {
      term = 'Abstract';
    }

    if (!Number.isInteger(page) || page <= 0) {
      page = 1;
    }

    if (!Number.isInteger(pages) || pages <= 0) {
      pages = 30;
    }

    navigate(
      `?page=${page}&per_page=${perPage}&query=${search}` +
        `&sort=${sorting}&pages=${pages}&term=${term}` 
        + `&date=${date}`,
    );

    // if(page > total/perPage) {
    //   page = total/perPage;
    // }

    setSearchParams({
      per_page: perPage,
      page: page,
      query: search,
      sorting: sorting,
      pages: pages,
      term: term,
      date: date,
    });

    const startTime = performance.now();

    setLoading(true);

    getPapers(
      page,
      perPage,
      search,
      sorting,
      startTime,
      pages,
      term,
      date,
    );
  }, [
    location.search,
    getPapers,
    navigate,
    searchParams.page,
    searchParams.per_page,
    searchParams.query,
    searchParams.sorting,
    searchParams.pages,
    searchParams.term,
    searchParams.date,
    setSearchParams,
  ]);

  const changePage = (page) => {
    setSearchParams((prevParams) => ({
      ...prevParams,
      page: page,
    }));

    const startTime = performance.now();

    getPapers(
      page,
      searchParams.per_page,
      searchParams.query,
      searchParams.sorting,
      startTime,
      searchParams.pages,
      searchParams.term,
      searchParams.date,
    );
    navigate(
      `?page=${page}&per_page=${searchParams.per_page}` +
        `&query=${searchParams.query}&sort=${searchParams.sorting}` +
        `&pages=${searchParams.pages}&term=${searchParams.term}&` +
        `${searchParams.date}`,
    );
  };

  const changePaper = (paperId) => {
    navigate(`/papers/${paperId}`);
  };

  const handlePageClick = (pageNumber) => {
    setPapers([]);
    changePage(pageNumber);
  };

  const chooseBody = () => {
    if (!loading && total === 0) {
      return <></>;
    } else if (!loading) {
      return (
        <div className="content-area">
          <Pagination
            handlePageClick={handlePageClick}
            page={searchParams.page}
            totalPages={pageCount}
          />
          <p className="pagination-container results">
            {!loading && `${total} Results in ${time} seconds`}
          </p>
          <p
            className="pagination-container results"
            style={{ paddingRight: '200px' }}
          >
            {total === 10000
              ? 'Results are Limited to the first 10,000 matching documents'
              : ''}
          </p>
          <ul className="list">
            {papers.map((paper, index) => (
              <div
                className={
                  index === expandedIndex ? 'expanded-container' : 'container'
                }
                key={index}
              >
                {accuracy[paper.id] != null && Number(accuracy[paper.id]) !== 0 && (
                  <div style={{ paddingBottom: '3px' }}>
                    Query Match Accuracy: {(accuracy[paper.id] * 100).toFixed(1)}%
                  </div>
                )}
                <div onClick={() => changePaper(paper.id.replace('/-/g', '/'))}>
                  <u className="paper-title">
                    <Content content={paper.title} />
                  </u>
                </div>
                <p>
                  by&nbsp;
                  {paper.authors.map((author, index) => (
                    <span key={index}>
                      <em>
                        {author}
                        {index < paper.authors.length - 1 ? ', ' : ''}
                      </em>
                    </span>
                  ))}
                </p>
                <div
                  className={expandedIndex === index ? 'text expanded' : 'text'}
                >
                  <Content content={paper.summary} />
                  <div
                    className="expand-button"
                    onClick={() => toggleExpand(index)}
                  >
                    {expandedIndex === index ? '⌃' : '⌄'}
                  </div>
                </div>
              </div>
            ))}
          </ul>
          <ScrollToTop />
          <ScrollToBottom />
        </div>
      );
    } else if (loading) {
      return (
        <div className="papers-loader">
          <p>Loading ...</p>
          <TailSpin color="#00BFFF" height={100} width={100} />
        </div>
      );
    }
  };

  return (
    <div>
      <p className="title" onClick={() => navigate('/')}>
        ICAM Superconductivity Database
      </p>
      <Search searchParams={searchParams} papers={papers} />
      <div className="page-container">
        <div className="filters">
          <Filters searchParams={searchParams} />
        </div>
        {chooseBody()}
      </div>
    </div>
  );
}

function ScrollToTop() {
  const scrollToTopButton = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };

  return (
    <button className="scroll-to-top-container" onClick={scrollToTopButton}>
      ↑
    </button>
  );
}

function ScrollToBottom() {
  const scrollToBottomButton = () => {
    window.scrollTo({
      top: document.documentElement.scrollHeight,
      behavior: 'smooth',
    });
  };

  return (
    <button
      className="scroll-to-bottom-container"
      onClick={scrollToBottomButton}
    >
      ↓
    </button>
  );
}

export default Papers;
