import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '../styles/filters.css';

function Filters({ searchParams }) {
  const navigate = useNavigate();
  const location = useLocation();

  const [pageNumber, setPageNumber] = useState(searchParams.pages || 30);
  const [sortVal, setSortVal] = useState(
    searchParams.sorting || 'Most-Relevant',
  );
  const [numResults, setNumResults] = useState(searchParams.per_page || 20);
  const [term, setTerm] = useState(searchParams.term || 'Abstract');

  const [results, setResults] = useState([20, 10, 50, 100]);
  const [order, setOrder] = useState([
    'Most-Relevant',
    'Most-Recent',
    'Oldest-First',
  ]);
  const [terms, setTerms] = useState([
    'Abstract',
    'Title',
    'Authors',
    'Category',
  ]);

  useEffect(() => {
    const query = new URLSearchParams(location.search);
    const perPage = Number(query.get('per_page')) || numResults;
    let sorting = query.get('sort') || sortVal;
    const pages = Number(query.get('pages')) || pageNumber;
    let searchTerm = query.get('term') || term;

    const updatedResults = results.filter((r) => r !== perPage);
    updatedResults.unshift(perPage);

    if (
      sorting !== 'Most-Recent' &&
      sorting !== 'Oldest-First' &&
      sorting !== 'Most-Relevant'
    ) {
      sorting = 'Most-Relevant';
    }

    if (
      searchTerm !== 'Abstract' &&
      searchTerm !== 'Title' &&
      searchTerm !== 'Category' &&
      searchTerm !== 'Authors'
    ) {
      searchTerm = 'Abstract';
    }

    const updatedOrder = order.filter((r) => r !== sorting);
    updatedOrder.unshift(sorting);

    const updatedTerms = terms.filter((r) => r !== searchTerm);
    updatedTerms.unshift(searchTerm);

    setNumResults(perPage);
    setSortVal(sorting);
    setPageNumber(pages);
    setTerm(searchTerm);

    setResults(updatedResults);
    setOrder(updatedOrder);
    setTerms(updatedTerms);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.search]);

  const handleButton = () => {
    let pageValue = pageNumber;
    if (pageNumber === '') {
      setPageNumber(30);
      pageValue = 30;
    }
    navigate(
      `?page=${searchParams.page}&per_page=${numResults}` +
        `&query=${searchParams.query}&sort=${sortVal}` +
        `&pages=${pageValue}&term=${term}`,
    );
  };

  const handleInputChange = (event) => {
    const val = event.target.value;
    if (val > 0 || val === '') {
      setPageNumber(val);
    }
  };

  return (
    <div>
      <b>Search Term</b>
      <br></br>
      <br></br>
      <select onChange={(e) => setTerm(e.target.value)}>
        {terms.map((option, index) => (
          <option key={index} value={option}>
            {option}
          </option>
        ))}
      </select>
      <br></br>
      <br></br>
      <b>Sort</b>
      <br></br>
      <div className="results-per-page">
        <select onChange={(e) => setSortVal(e.target.value.replace(' ', '-'))}>
          {order.map((option, index) => (
            <option key={index} value={option}>
              {option.replace('-', ' ')}
            </option>
          ))}
        </select>
      </div>
      <br></br>
      <b>Results Per Page</b>
      <br></br>
      <div className="results-per-page">
        <select onChange={(e) => setNumResults(e.target.value)}>
          {results.map((option, index) => (
            <option key={index} value={option}>
              {option}
            </option>
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
      <button onClick={handleButton} style={{ cursor: 'pointer' }}>
        Submit
      </button>
    </div>
  );
}

export default Filters;
