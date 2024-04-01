import React, { useState } from "react";
import '../styles/homepage.css'
import { useNavigate } from 'react-router-dom';
import { TailSpin } from 'react-loader-spinner';

export function HomePage({ searchParams }) {
    let navigate = useNavigate();

    const goToSearch = (query) => {
        if(query === "") {
            query = "all";
        }
        navigate(`/papers?page=${searchParams.page}&per_page=${searchParams.per_page}&query=${query}&sort=${searchParams.sorting}&journals=${searchParams.journals}`);
    };

    return (
        <div className="main">
            This is the HomePage
            <br></br>
            <button onClick={() => goToSearch("all")}>Go to Papers</button>
            <br></br>
            <Search searchParams={searchParams} />
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
        navigate(`/papers?page=${searchParams.page}&per_page=${searchParams.per_page}&query=${query}&sort=${searchParams.sorting}&journals=${searchParams.journals}`);
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