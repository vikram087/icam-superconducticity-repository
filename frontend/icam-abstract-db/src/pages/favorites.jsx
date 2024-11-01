import NavBar from "../components/navbar";
import { useState, useEffect } from "react";
import "../styles/favorites.css";
import { useNavigate } from "react-router-dom";
import Content from "../components/mathjax";
import { ScrollToBottom, ScrollToTop } from "./papers";
import "../styles/search.css";
import Fuse from "fuse.js";

function Favorites({ searchParams, setPrevUrl }) {
	const [highlightedStars, setHighlightedStars] = useState({});
	const [papers, setPapers] = useState([]);
	const [papersCopy, setPapersCopy] = useState([]);
	const [expandedIndex, setExpandedIndex] = useState(-1);
	const [query, setQuery] = useState("");
	const navigate = useNavigate();

	useEffect(() => {
		setQuery("all");
		const storedStars = localStorage.getItem("highlightedStars");
		setHighlightedStars(JSON.parse(storedStars));

		const backend_url = import.meta.env.VITE_BACKEND_URL;

		fetch(`${backend_url}/api/papers/fetch`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: storedStars,
		})
			.then((response) => response.json())
			.then((data) => {
				setPapers(data);
				setPapersCopy(data);
			})
			.catch((error) => {
				console.log(error);
			});
	}, []);

	const changePaper = (paperId) => {
		setPrevUrl(window.location.href);
		navigate(`/papers/${paperId}`);
	};

	const toggleStar = (id) => {
		const uid = id.replaceAll("-", "_");
		setHighlightedStars((prev) => {
			const newStars = { ...prev, [uid]: !prev[uid] };
			localStorage.setItem("highlightedStars", JSON.stringify(newStars));
			return newStars;
		});

		window.location.reload();
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
				<Search
					papers={papers}
					setPapers={setPapers}
					papersCopy={papersCopy}
					setQuery={setQuery}
				/>
				<div style={{ textAlign: "center" }}>
					<b style={{ fontSize: "large", paddingBottom: "10px" }}>
						Displaying Results for: "{query}"
					</b>
				</div>
				<div className="page-container">
					<div className="content-area">
						{papers ? (
							<ul className="list" style={{ paddingLeft: "100px" }}>
								{papers.map((paper, index) => (
									<div
										className={
											index === expandedIndex
												? "expanded-container"
												: "container"
										}
										key={`${paper.id}_favs`}
									>
										<div className="title-container">
											<div
												onClick={() =>
													changePaper(paper.id.replace("/-/g", "/"))
												}
											>
												<u className="paper-title">
													<Content content={paper.title} />
												</u>
											</div>
											<img
												width={20}
												height={20}
												src={
													highlightedStars[paper.id.replaceAll("-", "_")]
														? "/filled_star.png"
														: "/empty_star.png"
												}
												onClick={() => toggleStar(paper.id)}
												className="star-icon"
												alt="star icon"
											/>
										</div>
										<p>
											by&nbsp;
											{paper.authors.map((author, index) => (
												<span key={`${paper.id}_authors`}>
													<em>
														{author}
														{index < paper.authors.length - 1 ? ", " : ""}
													</em>
												</span>
											))}
										</p>
										<div
											className={
												expandedIndex === index ? "text expanded" : "text"
											}
										>
											<Content content={paper.summary} />
											<div
												className="expand-button"
												onClick={() => toggleExpand(index)}
											>
												{expandedIndex === index ? "⌃" : "⌄"}
											</div>
										</div>
									</div>
								))}
							</ul>
						) : (
							<p style={{ fontSize: "x-large" }}>
								No Favorites Currently Selected
							</p>
						)}
					</div>
				</div>
			</div>
			<ScrollToBottom />
			<ScrollToTop />
		</div>
	);
}

function Search({ papers, setPapers, papersCopy, setQuery }) {
	const [inputValue, setInputValue] = useState("");

	const goToSearch = (query) => {
		if (!papers) {
			setQuery(query);
			if (query === "") {
				setQuery("all");
			}
			return;
		}
		if (query === "" || query === "all") {
			setQuery("all");
			setPapers(papersCopy);
			return;
		}
		setQuery(query);

		const options = {
			keys: ["title", "authors", "summary"],
			threshold: 0.3,
		};

		const fuse = new Fuse(papers, options);
		const result = fuse.search(query);
		setPapers(result.map(({ item }) => item));
	};

	const handleChange = (event) => {
		setInputValue(event.target.value);
	};

	const handleKeyDown = (event) => {
		if (event.key === "Enter") {
			submitValue(inputValue);
		}
	};

	const submitValue = (value) => {
		goToSearch(value);
		setInputValue("");
	};

	return (
		<div className="cont">
			<div className="searchBox">
				<input
					className="searchInput"
					type="text"
					value={inputValue}
					onChange={handleChange}
					onKeyDown={handleKeyDown}
					placeholder="Search favorites"
				/>
				<button
					type="button"
					className="searchButton"
					href="#"
					onClick={() => submitValue(inputValue)}
				>
					<svg
						role="img"
						aria-label="search"
						xmlns="http://www.w3.org/2000/svg"
						width="29"
						height="29"
						viewBox="0 0 29 29"
						fill="none"
					>
						<g clipPath="url(#clip0_2_17)">
							<g filter="url(#filter0_d_2_17)">
								<path
									d="M23.7953 23.9182L19.0585 19.1814M19.0585 19.1814C19.8188 18.4211 20.4219 17.5185 20.8333 16.5251C21.2448 15.5318 21.4566 14.4671 21.4566 13.3919C21.4566 12.3167 21.2448 11.252 20.8333 10.2587C20.4219 9.2653 19.8188 8.36271 19.0585 7.60242C18.2982 6.84214 17.3956 6.23905 16.4022 5.82759C15.4089 5.41612 14.3442 5.20435 13.269 5.20435C12.1938 5.20435 11.1291 5.41612 10.1358 5.82759C9.1424 6.23905 8.23981 6.84214 7.47953 7.60242C5.94407 9.13789 5.08145 11.2204 5.08145 13.3919C5.08145 15.5634 5.94407 17.6459 7.47953 19.1814C9.01499 20.7168 11.0975 21.5794 13.269 21.5794C15.4405 21.5794 17.523 20.7168 19.0585 19.1814Z"
									stroke="white"
									strokeWidth="3"
									strokeLinecap="round"
									strokeLinejoin="round"
									shapeRendering="crispEdges"
								/>
							</g>
						</g>
						<defs>
							<filter
								id="filter0_d_2_17"
								x="-0.418549"
								y="3.70435"
								width="29.7139"
								height="29.7139"
								filterUnits="userSpaceOnUse"
								colorInterpolationFilters="sRGB"
							>
								<feFlood floodOpacity="0" result="BackgroundImageFix" />
								<feColorMatrix
									in="SourceAlpha"
									type="matrix"
									values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
									result="hardAlpha"
								/>
								<feOffset dy="4" />
								<feGaussianBlur stdDeviation="2" />
								<feComposite in2="hardAlpha" operator="out" />
								<feColorMatrix
									type="matrix"
									values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.25 0"
								/>
								<feBlend
									mode="normal"
									in2="BackgroundImageFix"
									result="effect1_dropShadow_2_17"
								/>
								<feBlend
									mode="normal"
									in="SourceGraphic"
									in2="effect1_dropShadow_2_17"
									result="shape"
								/>
							</filter>
							<clipPath id="clip0_2_17">
								<rect
									width="28.0702"
									height="28.0702"
									fill="white"
									transform="translate(0.403503 0.526367)"
								/>
							</clipPath>
						</defs>
					</svg>
				</button>
			</div>
		</div>
	);
}

export default Favorites;
