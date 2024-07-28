import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "../styles/filters.css";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

function Filters({ searchParams }) {
	const navigate = useNavigate();
	const location = useLocation();

	const [pageNumber, setPageNumber] = useState(searchParams.pages || 30);
	const [sortVal, setSortVal] = useState(
		searchParams.sorting || "Most-Relevant",
	);
	const [numResults, setNumResults] = useState(searchParams.per_page || 20);
	const [term, setTerm] = useState(searchParams.term || "Abstract");

	const results = [10, 20, 50, 100];
	const order = ["Most-Relevant", "Most-Recent", "Oldest-First"];
	const terms = ["Abstract", "Title", "Authors", "Category"];

	const [startDate, setStartDate] = useState(new Date(0));
	const [endDate, setEndDate] = useState(new Date());
	const formattedStart = startDate
		.toISOString()
		.split("T")[0]
		.replaceAll("-", "");
	const formattedEnd = endDate.toISOString().split("T")[0].replaceAll("-", "");

	const [dateRange, setDateRange] = useState(
		`${formattedStart}-${formattedEnd}`,
	);

	useEffect(() => {
		const query = new URLSearchParams(location.search);
		let searchTerm = query.get("term") || term;
		let sorting = query.get("sort") || sortVal;
		let perPage = Number(query.get("per_page")) || numResults; // need to add
		let pages = Number(query.get("pages")) || pageNumber; // need to add
		let date = query.get("date") || dateRange;
		let startDate = date.split("-")[0];
		let endDate = date.split("-")[1];

		const currentDate = new Date();
		const now = currentDate.toISOString().slice(0, 10).replaceAll(/-/g, "");

		if (perPage >= 100) {
			perPage = 100;
		} else if (perPage >= 50) {
			perPage = 50;
		} else if (perPage >= 20) {
			perPage = 20;
		} else {
			perPage = 10;
		}

		if (!Number.isInteger(pages) || pages <= 0) {
			pages = 30;
		}

		if (dateRange.split("-").length !== 2) {
			date = `00000000-${now}`;
		}

		if (Number.isNaN(Number(startDate)) || startDate.length !== 8) {
			startDate = "00000000";
			date = `${startDate}-${endDate}`;
		}
		if (Number.isNaN(Number(endDate)) || endDate.length !== 8) {
			endDate = now;
			date = `${startDate}-${endDate}`;
		}

		if (
			sorting !== "Most-Recent" &&
			sorting !== "Oldest-First" &&
			sorting !== "Most-Relevant"
		) {
			sorting = "Most-Relevant";
		}

		if (
			searchTerm !== "Abstract" &&
			searchTerm !== "Title" &&
			searchTerm !== "Category" &&
			searchTerm !== "Authors"
		) {
			searchTerm = "Abstract";
		}

		setNumResults(perPage);
		setSortVal(sorting);
		setPageNumber(pages);
		setTerm(searchTerm);
		setDateRange(date);
		setStartDate(convertIntToDate(startDate));
		setEndDate(convertIntToDate(endDate));
	}, [location.search /*,numResults, sortVal, pageNumber, term, dateRange*/]); // FIXME: make sure this works well

	const handleButton = () => {
		let pageValue = pageNumber;
		if (pageNumber === "") {
			setPageNumber(30);
			pageValue = 30;
		}

		navigate(
			`?page=${searchParams.page}&per_page=${numResults}` +
				`&query=${searchParams.query}&sort=${sortVal}` +
				`&pages=${pageValue}&term=${term}` +
				`&date=${dateRange}`,
		);
	};

	const handleReset = () => {
		const currentDate = new Date();
		const now = currentDate.toISOString().slice(0, 10).replaceAll(/-/g, "");

		navigate(
			`?page=1&per_page=20&query=all&sort=Most-Relevant&pages=30&term=Abstract&date=00000000-${now}`,
		);
	};

	const convertIntToDate = (dateNum) => {
		const dateString = String(dateNum);
		const year = dateString.substring(0, 4);
		const month = dateString.substring(4, 6) - 1;
		const day = dateString.substring(6, 8);

		let dateTime = new Date(year, month, day);
		if (year + month + day === "00000000") {
			dateTime = new Date(0);
		}

		return dateTime;
	};

	const handleInputChange = (event) => {
		const val = event.target.value;
		if (val > 0 || val === "") {
			setPageNumber(val);
		}
	};

	const updateDateVal = (date, type) => {
		const formattedDate = date.toISOString().split("T")[0].replaceAll("-", "");
		const formattedStart = startDate
			.toISOString()
			.split("T")[0]
			.replaceAll("-", "");
		const formattedEnd = endDate
			.toISOString()
			.split("T")[0]
			.replaceAll("-", "");

		if (type === "start") {
			setStartDate(date);
			setDateRange(`${formattedDate}-${formattedEnd}`);
		} else if (type === "end") {
			setEndDate(date);
			setDateRange(`${formattedStart}-${formattedDate}`);
		}
	};

	return (
		<div>
			<button
				type="button"
				className="submitBtn"
				onClick={handleReset}
				style={{ cursor: "pointer", marginBottom: "10px" }}
			>
				Reset Filters
			</button>
			<Dropdown terms={terms} setTerm={setTerm} value={"Term"} term={term} />
			<Sort order={order} setSortVal={setSortVal} sort={sortVal} />
			<Dropdown
				terms={results}
				setTerm={setNumResults}
				value={"Per Page"}
				term={numResults}
			/>
			<p className="bold">Page Limit</p>
			<input
				type="number"
				min={1}
				value={pageNumber}
				onChange={handleInputChange}
				className="styled-input"
			/>
			<p className="bold">Date Range</p>
			<div>
				<p>Start Date:</p>
				<DatePicker
					id="startDate"
					dateFormat="yyyy-MM-dd"
					selected={startDate}
					onChange={(date) => updateDateVal(date, "start")}
				/>
			</div>
			<div>
				<p>End Date:</p>
				<DatePicker
					id="endDate"
					dateFormat="yyyy-MM-dd"
					selected={endDate}
					onChange={(date) => updateDateVal(date, "end")}
				/>
			</div>
			<button
				type="button"
				className="submitBtn"
				onClick={handleButton}
				style={{ cursor: "pointer", marginTop: "20px" }}
			>
				Submit
				<svg
					aria-label="submit button"
					role="img"
					fill="white"
					viewBox="0 0 448 512"
					height="1em"
					className="arrow"
				>
					<path d="M438.6 278.6c12.5-12.5 12.5-32.8 0-45.3l-160-160c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L338.8 224 32 224c-17.7 0-32 14.3-32 32s14.3 32 32 32l306.7 0L233.4 393.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0l160-160z" />
				</svg>
			</button>
		</div>
	);
}

function Dropdown({ terms, setTerm, value, term }) {
	return (
		<div className="paste-button" style={{ paddingBottom: "10px" }}>
			<button className="but" type="button">
				{value}: {term}&nbsp; ▼
			</button>
			<div className="dropdown-content">
				{terms.map((option) => (
					<option key={option} value={option} onClick={() => setTerm(option)}>
						{option}
					</option>
				))}
			</div>
		</div>
	);
}

function Sort({ order, setSortVal, sort }) {
	return (
		<div className="paste-button" style={{ paddingBottom: "10px" }}>
			<button className="but" type="button">
				Sort: {sort.replace("-", " ")}&nbsp; ▼
			</button>
			<div className="dropdown-content">
				{order.map((option, index) => (
					<option
						key={option}
						value={option}
						onClick={() => setSortVal(option.replace(" ", "-"))}
					>
						{option.replace("-", " ")}
					</option>
				))}
			</div>
		</div>
	);
}

export default Filters;
