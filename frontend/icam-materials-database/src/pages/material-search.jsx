import NavBar from "../components/navbar";
import "../styles/material-search.css";
import { ScrollToBottom, ScrollToTop } from "./papers";
import { useEffect, useState } from "react";

function Table({ tableParams, setTableParams, setPrevUrl }) {
	const [time, setTime] = useState(0);
	const [loading, setLoading] = useState(false);
	const [papers, setPapers] = useState([]);
	const [total, setTotal] = useState(0);
	const [pageCount, setPageCount] = useState(0);
	const [highlightedStars, setHighlightedStars] = useState({});

	const columns = [
		{ header: "Material", key: "MAT" },
		{ header: "Description", key: "DSC" },
		{ header: "Symmetry", key: "SPL" },
		{ header: "Synthesis", key: "SMT" },
		{ header: "Characterization", key: "CMT" },
		{ header: "Property", key: "PRO" },
		{ header: "Application", key: "APL" },
	];

	useEffect(() => {
		const query = new URLSearchParams(location.search);
		const page = Number(query.get("page")) || tableParams.page;
		const perPage = Number(query.get("per_page")) || tableParams.per_page;
		const search = query.get("query") || tableParams.query;
		const sorting = query.get("sort") || tableParams.sorting;
		const term = query.get("term") || tableParams.term;
		const date = query.get("date") || tableParams.date;

		const storedStars =
			JSON.parse(localStorage.getItem("highlightedStars")) || [];
		setHighlightedStars(Array.isArray(storedStars) ? storedStars : []);

		setTableParams({
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
	}, [location.search]);

	const getPapers = (
		page,
		results,
		query,
		sorting,
		startTime,
		term,
		dateRange,
	) => {
		const backend_url = import.meta.env.VITE_BACKEND_URL;

		fetch(`${backend_url}/api/materials/${term}/${query}`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				page: page,
				results: results,
				sorting: sorting,
				date: dateRange,
			}),
		})
			.then((response) => response.json())
			.then((data) => {
				const endTime = performance.now();
				const totalTimeS = (endTime - startTime) / 1000;
				const totalTime = totalTimeS.toFixed(2);

				setTime(totalTime);
				setLoading(false);

				// console.log(data.papers);

				setPapers(data.papers);
				setTotal(data.total);
				setPageCount(Math.ceil(data.total / tableParams.per_page));
			})
			.catch((error) => {
				setTotal(0);
				setPapers([]);
				setPageCount(0);
			});
	};

	return (
		<>
			<NavBar />
			<div className="mat-search-container">
				<h1>Search Materials</h1>
				<table className="materials-table">
					<thead>
						<tr>
							{columns.map((column) => (
								<th key={column.key}>{column.header}</th>
							))}
						</tr>
					</thead>
					<tbody>
						{papers?.map((row, index) => (
							<tr key={index}>
								{columns.map((column) => (
									<td key={column.key}>
										{Array.isArray(row[column.key])
											? row[column.key].join(", ")
											: row[column.key] || "N/A"}
									</td>
								))}
							</tr>
						))}
					</tbody>
				</table>
			</div>
			<ScrollToBottom />
			<ScrollToTop />
		</>
	);
}

export default Table;
