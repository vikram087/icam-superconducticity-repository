import { useState } from "react";
import "../styles/pagination.css";

function Pagination({ handlePageClick, totalPages }) {
	const query = new URLSearchParams(location.search);
	let page = Number(query.get("page")) || searchParams.page;
	if (page < 0) {
		page = 1;
	}
	const [pageNumber, setPageNumber] = useState(page);

	const handleBack = () => {
		if (page >= 2) {
			handlePageClick(page - 1);
			setPageNumber(page - 1);
		}
	};

	const handleFront = () => {
		if (page <= totalPages - 1) {
			handlePageClick(Number(page) + 1);
			setPageNumber(Number(page) + 1);
		}
	};

	const handleNumber = (pageNumber) => {
		if (Number(page) !== pageNumber) {
			handlePageClick(pageNumber);
			setPageNumber(pageNumber);
		}
	};

	const handleSubmit = (event) => {
		if (event.key === "Enter" && page !== pageNumber) {
			if (pageNumber < 2 && page > 1) {
				handlePageClick(1);
				setPageNumber(1);
			} else if (pageNumber > totalPages - 1 && page < totalPages) {
				handlePageClick(totalPages);
				setPageNumber(totalPages);
			} else if (pageNumber <= totalPages - 1 && pageNumber >= 2) {
				handlePageClick(pageNumber);
				setPageNumber(pageNumber);
			}
		}
	};

	const handleInputChange = (event) => {
		setPageNumber(event.target.value);
	};

	return (
		<div className="pagination-wrapper">
			<div className="pagination-container">
				<span style={{ cursor: "pointer" }} onClick={() => handleNumber(1)}>
					&lt;&lt;&nbsp;
				</span>
				<span style={{ cursor: "pointer" }} onClick={handleBack}>
					&nbsp;&lt;&nbsp;
				</span>
				<input
					type="number"
					onKeyDown={handleSubmit}
					value={pageNumber}
					onChange={handleInputChange}
				/>
				<span style={{ cursor: "pointer" }} onClick={handleFront}>
					&nbsp;&gt;&nbsp;
				</span>
				<span
					style={{ cursor: "pointer" }}
					onClick={() => handleNumber(totalPages)}
				>
					&nbsp;&gt;&gt;&nbsp;
				</span>
			</div>
		</div>
	);
}

export default Pagination;
