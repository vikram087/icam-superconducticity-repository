import NavBar from "../components/navbar";
import { useState, useEffect } from "react";
import "../styles/favorites.css";

function Favorites({ searchParams }) {
    const [highlightedStars, setHighlightedStars] = useState({});

    useEffect(() => {
        const storedStars = localStorage.getItem('highlightedStars');

        if (storedStars) {
          setHighlightedStars(JSON.parse(storedStars));
        }
    }, []);

    return (
        <div>
            <NavBar searchParams={searchParams}/>
            <div className="fav-main">

            </div>
        </div>
    );
}

export default Favorites;