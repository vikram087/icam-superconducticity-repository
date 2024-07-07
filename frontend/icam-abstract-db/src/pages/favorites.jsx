import NavBar from "../components/navbar";
import { useState, useEffect } from "react";
import "../styles/favorites.css";

function Favorites({ searchParams }) {
    const [papers, setPapers] = useState([]);

    useEffect(() => {
        const storedStars = localStorage.getItem('highlightedStars');

        fetch('http://localhost:8080/api/papers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: storedStars,
        })
        .then((response) => response.json())
        .then((data) => {
            setPapers(data);
        })
        .catch((error) => {
            console.log(error);
        });

    }, []);

    return (
        <div>
            <NavBar searchParams={searchParams}/>
            <div className="fav-main">
                {papers}
            </div>
        </div>
    );
}

export default Favorites;