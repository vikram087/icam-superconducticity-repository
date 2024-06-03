import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/search.css';

function Search({ searchParams }) {
  const [inputValue, setInputValue] = useState('');

  const navigate = useNavigate();

  const goToSearch = (query) => {
    if (query === '') {
      query = 'all';
    }
    navigate(
      `/papers?page=1&per_page=${searchParams.per_page}&query=${query}` +
        `&sort=${searchParams.sorting}` +
        `&pages=${searchParams.pages}&term=${searchParams.term}`,
    );
  };

  const handleChange = (event) => {
    setInputValue(event.target.value);
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      submitValue(inputValue);
    }
  };

  const submitValue = (value) => {
    goToSearch(value);
    setInputValue('');
  };

  return (
    <div className="top-bar">
      <div className="form-container">
        <div className="input-box">
          <input
            className="text-field"
            type="text"
            value={inputValue}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="Search Database"
          />
        </div>
      </div>
    </div>
  );
}

export default Search;
