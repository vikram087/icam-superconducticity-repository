import React from "react";
import '../styles/homepage.css'
import { useNavigate } from 'react-router-dom';

export function HomePage() {
    let navigate = useNavigate();

    const goToSearch = () => {
        navigate("/papers");
    };

    return (
        <div className="main">
            This is the HomePage
            <br></br>
            <button onClick={goToSearch}>Go to Search</button>
        </div>
    );
}