import NavBar from "../components/navbar";
import "../styles/material-search.css";
import { ScrollToBottom, ScrollToTop } from "./papers";

function Table({ searchParams }) {
	return (
		<>
			<NavBar searchParams={searchParams} />
			<div className="mat-search-container">Search Materials</div>
			<ScrollToBottom />
			<ScrollToTop />
		</>
	);
}

export default Table;
