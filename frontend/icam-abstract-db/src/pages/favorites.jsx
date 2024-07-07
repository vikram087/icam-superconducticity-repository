import NavBar from "../components/navbar";
import { useState, useEffect } from "react";
import "../styles/favorites.css";
import { useNavigate } from "react-router-dom";
import Content from "../components/mathjax";
import { ScrollToBottom, ScrollToTop } from "./papers";

function Favorites({ searchParams }) {
    const [highlightedStars, setHighlightedStars] = useState({});
    const [papers, setPapers] = useState([]);
    const [expandedIndex, setExpandedIndex] = useState(-1);
    const navigate = useNavigate();

    useEffect(() => {
        const storedStars = localStorage.getItem('highlightedStars');
        setHighlightedStars(JSON.parse(storedStars));

        fetch('http://localhost:8080/api/papers/fetch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: storedStars,
        })
        .then((response) => response.json())
        .then((data) => {
            setPapers(data);
            console.log(data);
        })
        .catch((error) => {
            console.log(error);
        });

    }, []);

    const changePaper = (paperId) => {
        navigate(`/papers/${paperId}`);
    };

    const toggleStar = (id) => {
        const uid = id.replaceAll("-", "_");
        setHighlightedStars((prev) => {
          const newStars = { ...prev, [uid]: !prev[uid] };
          localStorage.setItem('highlightedStars', JSON.stringify(newStars));
          return newStars;
        });
    };

    const toggleExpand = (index) => {
        if (expandedIndex === index) {
          setExpandedIndex(-1);
        } else {
          setExpandedIndex(index);
        }
    };

    return (
        <div>
            <NavBar searchParams={searchParams} />
            <div className="page-main">
                <h1 style={{ textAlign: "center" }}>Favorites</h1>
                <div className="page-container">
                    <div className="content-area">
                        <ul className="list" style={{ paddingLeft: "100px" }}>
                        {papers.map((paper, index) => (
                            <div
                            className={
                                index === expandedIndex ? 'expanded-container' : 'container'
                            }
                            key={index}
                            >
                            <div className='title-container'>
                                <div onClick={() => changePaper(paper.id.replace('/-/g', '/'))}>
                                <u className="paper-title">
                                    <Content content={paper.title} />
                                </u>
                                </div>
                                <img
                                width={20}
                                height={20}
                                src={highlightedStars[paper.id.replaceAll("-", "_")] ? '/filled_star.png' : '/empty_star.png'}
                                onClick={() => toggleStar(paper.id)}
                                className="star-icon"
                                alt="star icon">
                                </img>
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
                    </div>
                </div>
            </div>
            <ScrollToBottom />
            <ScrollToTop />
        </div>
    );
}

export default Favorites;