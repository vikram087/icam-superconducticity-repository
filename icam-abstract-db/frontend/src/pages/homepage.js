import React, { useState } from "react";
import '../styles/homepage.css'
import { useNavigate } from 'react-router-dom';

export function HomePage() {
    let navigate = useNavigate();

    const goToSearch = (query) => {
        navigate(`/papers?page=1&per_page=20&query=${query}&sort=Most-Recent&journals=None`);
    };

    return (
        <div className="main">
            This is the HomePage
            <br></br>
            <button onClick={() => goToSearch("all")}>Go to Papers</button>
            <br></br>
            <Search />
        </div>
    );
}

export function Search() {
    const [inputValue, setInputValue] = useState('');

    let navigate = useNavigate();

    const goToSearch = (query) => {
        navigate(`/papers?page=1&per_page=20&query=${query}&sort=Most-Recent&journals=None`);
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
        <input
            type="text"
            value={inputValue}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="Type something and press Enter"
        />        
    )
}