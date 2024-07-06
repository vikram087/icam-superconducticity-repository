import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '../styles/filters.css';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

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

  const [startDate, setStartDate] = useState(new Date(0));
  const [endDate, setEndDate] = useState(new Date());
  const formattedStart = startDate.toISOString().split('T')[0].replaceAll("-", "");
  const formattedEnd = endDate.toISOString().split('T')[0].replaceAll("-", "");

  const [dateRange, setDateRange] = useState(`${formattedStart}-${formattedEnd}`);

  useEffect(() => {
    const query = new URLSearchParams(location.search);
    const perPage = Number(query.get('per_page')) || numResults;
    let sorting = query.get('sort') || sortVal;
    const pages = Number(query.get('pages')) || pageNumber;
    let searchTerm = query.get('term') || term;
    let date = query.get('date') || dateRange;
    let startDate = date.split("-")[0];
    let endDate = date.split("-")[1];

    const updatedResults = results.filter((r) => r !== perPage);
    updatedResults.unshift(perPage);

    const currentDate = new Date();
    const now = currentDate.toISOString().slice(0, 10).replaceAll(/-/g, '');

    if(dateRange.split("-").length !== 2) {
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
    setDateRange(date);
    setStartDate(convertIntToDate(startDate));
    setEndDate(convertIntToDate(endDate));

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
        `&pages=${pageValue}&term=${term}` 
        + `&date=${dateRange}`,
    );
    window.location.reload();
  };

  const convertIntToDate = (dateNum) => {
    const dateString = String(dateNum);
    const year = dateString.substring(0, 4);
    const month = dateString.substring(4, 6) - 1;
    const day = dateString.substring(6, 8);

    let dateTime = new Date(year, month, day);
    if(year + month + day === "00000000") {
      dateTime = new Date(0);
    }

    return dateTime;
  };

  const handleInputChange = (event) => {
    const val = event.target.value;
    if (val > 0 || val === '') {
      setPageNumber(val);
    }
  };

  const updateDateVal = (date, type) => {
    const formattedDate = date.toISOString().split('T')[0].replaceAll('-', "");
    let formattedStart = startDate.toISOString().split('T')[0].replaceAll("-", "");
    const formattedEnd = endDate.toISOString().split('T')[0].replaceAll("-", "");

    if (type === 'start') {
      setStartDate(date);
      setDateRange(`${formattedDate}-${formattedEnd}`);
    } else if (type === 'end') {
      setEndDate(date);
      setDateRange(`${formattedStart}-${formattedDate}`);
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
      <input
        type="number"
        min={1}
        value={pageNumber}
        onChange={handleInputChange}
      ></input>
      <br></br>
      <br></br>
      <b>Date Range</b>
      <div>
        <p>Start Date:</p>
        <DatePicker
          id="startDate"
          dateFormat="yyyy-MM-dd"
          selected={startDate}
          onChange={(date) => updateDateVal(date, 'start')}
        />
      </div>
      <div>
        <p>End Date:</p>
        <DatePicker
          id="endDate"
          dateFormat="yyyy-MM-dd"
          selected={endDate}
          onChange={(date) => updateDateVal(date, 'end')}
        />
      </div>
      <br></br>
      <br></br>
      <button onClick={handleButton} style={{ cursor: 'pointer' }}>
        Submit
      </button>
    </div>
  );
}

export default Filters;
