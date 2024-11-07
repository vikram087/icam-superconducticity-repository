import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { TailSpin } from "react-loader-spinner";
import Search from "../components/search.jsx";
import Content from "../components/mathjax.jsx";
import Pagination from "../components/pagination.jsx";
import Filters from "../components/filters.jsx";
import "../styles/papers.css";
import NavBar from "../components/navbar.jsx";

function Papers({ searchParams, setSearchParams, setPrevUrl }) {
	const location = useLocation();

	const [papers, setPapers] = useState([]);
	const [pageCount, setPageCount] = useState(0);
	const [expandedIndex, setExpandedIndex] = useState(-1);
	const [total, setTotal] = useState(0);
	const [loading, setLoading] = useState(true);
	const [accuracy, setAccuracy] = useState({});
	const [time, setTime] = useState("");
	const [highlightedStars, setHighlightedStars] = useState([]);

	const navigate = useNavigate();

	const toggleExpand = (index) => {
		if (expandedIndex === index) {
			setExpandedIndex(-1);
		} else {
			setExpandedIndex(index);
		}
	};

	const getPapers = (
		page,
		results,
		query,
		sorting,
		startTime,
		term,
		dateRange,
	) => {
		const search = parseInput(query).search;
		const parsed = parseInput(query).boolean;

		const backend_url = import.meta.env.VITE_BACKEND_URL;

		fetch(`${backend_url}/api/papers/${term}/${query}`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				page: page,
				results: results,
				sorting: sorting,
				date: dateRange,
				parsedInput: parsed,
			}),
		})
			.then((response) => response.json())
			.then((data) => {
				const endTime = performance.now();

				const totalTimeS = (endTime - startTime) / 1000;
				const totalTime = totalTimeS.toFixed(2);

				setTime(totalTime);
				setLoading(false);

				setExpandedIndex(-1);
				setPapers(data.papers);
				setTotal(data.total);
				setAccuracy(data.accuracy);
				setPageCount(Math.ceil(data.total / searchParams.per_page));
			})
			.catch((error) => {
				setExpandedIndex(-1);
				setTotal(0);
				setPapers([]);
				setAccuracy({});
				setPageCount(0);
			});
	};

	const parseInput = (que) => {
		const allOccur = (arr, searchString) => {
			const indices = [];
			for (let i = 0; i < arr.length; i++) {
				if (arr[i] === searchString) {
					indices.push(i);
				}
			}
			return indices;
		};

		const removeDups = (list) => {
			return [...new Set(list)];
		};

		const query = que.toLowerCase();
		const beforeIndex = query.indexOf("|");
		let orTerms = [];
		const andTerms = [];
		let notTerms = [];
		let mustTerms = [];
		const indices = [];

		if (beforeIndex === -1) {
			return {
				search: query,
				boolean: { or: orTerms, not: notTerms, must: mustTerms },
			};
		}

		const before = query.substring(0, beforeIndex).trim();
		const after = query.substring(beforeIndex + 1, query.length).trim();
		const quer = before.split(" ");

		const or = allOccur(quer, "or");
		const and = allOccur(quer, "and");
		const not = allOccur(quer, "not");
		const must = allOccur(quer, "must");

		if (or !== -1) {
			for (let i = 0; i < or.length; i++) {
				orTerms.push(quer[or[i] - 1]);
				orTerms.push(quer[or[i] + 1]);
				indices.push(or[i] - 1);
				indices.push(or[i] + 1);
			}
		}
		if (and !== -1) {
			for (let i = 0; i < and.length; i++) {
				andTerms.push(quer[and[i] - 1]);
				andTerms.push(quer[and[i] + 1]);
				indices.push(and[i] - 1);
				indices.push(and[i] + 1);
			}
		}
		if (not !== -1) {
			for (let i = 0; i < not.length; i++) {
				notTerms.push(quer[not[i] + 1]);
				indices.push(not[i] + 1);
			}
		}
		if (must !== -1) {
			for (let i = 0; i < must.length; i++) {
				mustTerms.push(quer[must[i] + 1]);
				indices.push(must[i] + 1);
			}
		}

		orTerms = removeDups(orTerms);
		notTerms = removeDups(notTerms);
		mustTerms = removeDups(mustTerms.concat(andTerms));

		const boolean = { or: orTerms, not: notTerms, must: mustTerms };

		return { search: after, boolean: boolean };
	};

	useEffect(() => {
		const query = new URLSearchParams(location.search);
		const page = Number(query.get("page")) || searchParams.page;
		const perPage = Number(query.get("per_page")) || searchParams.per_page;
		const search = query.get("query") || searchParams.query;
		const sorting = query.get("sort") || searchParams.sorting;
		const term = query.get("term") || searchParams.term;
		const date = query.get("date") || searchParams.date;

		const storedStars =
			JSON.parse(localStorage.getItem("highlightedStars")) || [];
		setHighlightedStars(Array.isArray(storedStars) ? storedStars : []);

		setSearchParams({
			per_page: perPage,
			page: page,
			query: search,
			sorting: sorting,
			term: term,
			date: date,
		});

		const startTime = performance.now();

		setLoading(true);

		getPapers(page, perPage, search, sorting, startTime, term, date);
	}, [
		location.search,
		/*searchParams.page,
		searchParams.per_page,
		searchParams.query,
		searchParams.sorting,
		searchParams.term,
		searchParams.date,
		searchParams,
		setSearchParams,
		getPapers,*/
	]);

	const changePage = (page) => {
		setSearchParams((prevParams) => ({
			...prevParams,
			page: page,
		}));

		navigate(
			`?page=${page}&per_page=${searchParams.per_page}` +
				`&query=${searchParams.query}&sort=${searchParams.sorting}` +
				`&term=${searchParams.term}&` +
				`${searchParams.date}`,
		);
	};

	const changePaper = (paperId) => {
		setPrevUrl(window.location.href);
		navigate(`/papers/${paperId}`);
	};

	const handlePageClick = (pageNumber) => {
		setPapers([]);
		changePage(pageNumber);
	};

	const toggleStar = (paper) => {
		setHighlightedStars((prev) => {
			const isStarred = prev.some((p) => p.id === paper.id);

			const newStars = isStarred
				? prev.filter((p) => p.id !== paper.id)
				: [...prev, paper];

			localStorage.setItem("highlightedStars", JSON.stringify(newStars));
			return newStars;
		});
	};

	const chooseBody = () => {
		if (!loading && total === 0) {
			return (
				<div className="content-area">
					<div style={{ marginLeft: "-460px" }}>
						<p className="pag-container results">
							Please adjust search parameters to yield results
						</p>
					</div>
				</div>
			);
		}
		if (!loading) {
			return (
				<div className="content-area">
					<div style={{ marginLeft: "-460px" }}>
						<div className="pag-container results">
							<p>{!loading && `${total} Results in ${time} seconds`}</p>
							<p>
								{total === 10000
									? "Results are Limited to the first 10,000 matching documents"
									: ""}
							</p>
							<b
								style={{
									fontSize: "large",
									paddingBottom: "10px",
									paddingLeft: "25vw",
									maxWidth: "60vw",
								}}
							>
								Displaying Results for: "{searchParams.query}"
							</b>
						</div>
					</div>
					<ul className="list">
						{papers?.map((paper, index) => (
							<div
								className={
									index === expandedIndex ? "expanded-container" : "container"
								}
								key={`${paper.id}_papers`}
							>
								{accuracy[paper.id] != null &&
									Number(accuracy[paper.id]) !== 0 && (
										<div style={{ paddingBottom: "3px" }}>
											Query Match Accuracy:{" "}
											{(accuracy[paper.id] * 100).toFixed(1)}%
										</div>
									)}
								<div className="title-container">
									<div
										onClick={() => changePaper(paper.id.replace("/-/g", "/"))}
									>
										<u className="paper-title">
											<Content content={paper.title} />
										</u>
									</div>
									<img
										width={20}
										height={20}
										src={
											highlightedStars.some((p) => p.id === paper.id)
												? "/filled_star.png"
												: "/empty_star.png"
										}
										onClick={() => toggleStar(paper)}
										className="star-icon"
										alt="star icon"
									/>
								</div>
								<p>
									by&nbsp;
									{paper.authors.map((author, index) => (
										<span key={`${paper.id}_authors_papers`}>
											<em>
												{author}
												{index < paper.authors.length - 1 ? ", " : ""}
											</em>
										</span>
									))}
								</p>
								<div
									className={expandedIndex === index ? "text expanded" : "text"}
								>
									<Content content={paper.summary} />
									<div
										className="expand-button"
										onClick={() => toggleExpand(index)}
									>
										{expandedIndex === index ? "⌃" : "⌄"}
									</div>
								</div>
								{paper.MAT !== "N/A" && (
									<p>
										<strong>Materials:</strong>{" "}
										{paper.MAT.map((item, index) => (
											<span key={index}>
												{item}
												{index < paper.MAT.length - 1 ? ", " : ""}
											</span>
										))}
									</p>
								)}
							</div>
						))}
					</ul>
				</div>
			);
		}
		if (loading) {
			return (
				<div className="papers-loader">
					<p>Loading ...</p>
					<TailSpin color="#00BFFF" height={100} width={100} />
				</div>
			);
		}
	};

	return (
		<div>
			<NavBar searchParams={searchParams} />
			<div className="page-main">
				<h1 style={{ textAlign: "center" }}>Papers</h1>
				<Search searchParams={searchParams} papers={papers} />
				<div className="page-container">
					<div className="filters">
						<Filters searchParams={searchParams} />
					</div>
					<div className="page-wrapper">
						<Pagination
							handlePageClick={handlePageClick}
							totalPages={pageCount}
						/>
						{chooseBody()}
						<ScrollToTop />
						<ScrollToBottom />
					</div>
				</div>
			</div>
		</div>
	);
}

export function ScrollToTop() {
	const scrollToTopButton = () => {
		window.scrollTo({
			top: 0,
			behavior: "smooth",
		});
	};

	return (
		<button
			className="bu scroll-to-top-container"
			onClick={scrollToTopButton}
			type="button"
		>
			<svg
				className="svgIcon"
				viewBox="0 0 384 512"
				role="img"
				aria-label="scroll to top"
			>
				<path d="M214.6 41.4c-12.5-12.5-32.8-12.5-45.3 0l-160 160c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L160 141.2V448c0 17.7 14.3 32 32 32s32-14.3 32-32V141.2L329.4 246.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-160-160z" />
			</svg>
		</button>
	);
}

export function ScrollToBottom() {
	const scrollToBottomButton = () => {
		window.scrollTo({
			top: document.documentElement.scrollHeight,
			behavior: "smooth",
		});
	};

	return (
		<button
			type="button"
			className="bu scroll-to-bottom-container"
			onClick={scrollToBottomButton}
		>
			<svg
				className="svgIcon"
				viewBox="0 0 384 512"
				role="img"
				aria-label="scroll to bottom"
			>
				<path d="M214.6 410.6c-12.5 12.5-32.8 12.5-45.3 0l-160-160c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0L160 310.8V16c0-17.7 14.3-32 32-32s32 14.3 32 32v294.8l115.4-115.4c12.5-12.5 32.8-12.5 45.3 0s12.5 32.8 0 45.3l-160 160z" />
			</svg>
		</button>
	);
}

export default Papers;
