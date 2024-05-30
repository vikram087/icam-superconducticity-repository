import React, { useState } from "react";
import '../styles/homepage.css'
import { useNavigate } from 'react-router-dom';

export function HomePage({ searchParams }) {
    let navigate = useNavigate();

    const goToSearch = (query) => {
        if(query === "") {
            query = "all";
        }
        navigate(`/papers?page=${searchParams.page}&per_page=${searchParams.per_page}&query=${query}&sort=${searchParams.sorting}&pages=${searchParams.pages}`);
    };

    return (
        <div className="main">
            <p className='home-title' onClick={() => navigate("/")}>ICAM Superconductivity Database</p>
            <br></br>
            <div className="go-to-papers" onClick={() => goToSearch("all")}>
                <button className="go-to-button">Go to Papers</button>
            </div>
            <br></br>
            <Search searchParams={searchParams} />
            <p>Funded by the Institute for Complex Adaptive Matter</p>
            <p>Powered with Elasticsearch</p>
        </div>
    );
}

export function Search({ searchParams }) {
    const [inputValue, setInputValue] = useState('');

    let navigate = useNavigate();

    const goToSearch = (query) => {
        if(query === "") {
            query = "all";
        }
        navigate(`/papers?page=1&per_page=${searchParams.per_page}&query=${query}&sort=${searchParams.sorting}&pages=${searchParams.pages}`);
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
    )
}