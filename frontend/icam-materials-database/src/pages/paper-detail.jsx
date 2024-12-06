import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { TailSpin } from "react-loader-spinner";
import Content from "../components/mathjax";
import "../styles/paper-detail.css";
import NavBar from "../components/navbar";

function PaperDetail({ prevUrl, selectedPaper }) {
	const [highlightedStars, setHighlightedStars] = useState([]);
	const [paper, setPaper] = useState(selectedPaper);
	const { id } = useParams();

	useEffect(() => {
		const storedStars =
			JSON.parse(localStorage.getItem("highlightedStars")) || [];
		setHighlightedStars(Array.isArray(storedStars) ? storedStars : []);

		if (!selectedPaper?.id) {
			console.log("Fetching paper");
			const backend_url = import.meta.env.VITE_BACKEND_URL;

			fetch(`${backend_url}/api/papers/${id}`)
				.then((response) => response.json())
				.then((data) => {
					setPaper(data);
				});
		}
	}, [id, selectedPaper]);

	const goBack = () => {
		if (prevUrl) {
			window.location.href = prevUrl;
		} else {
			window.location.href = "/";
		}
	};

	const replaceID = (id) => {
		if (!id) return "";
		const lastIndex = id.lastIndexOf("-");

		if (lastIndex !== -1) {
			return `${id.substring(0, lastIndex)}/${id.substring(lastIndex + 1)}`;
		}

		return id;
	};

	const numToDate = (date) => {
		const monthsReversed = {
			"01": "January,",
			"02": "February,",
			"03": "March,",
			"04": "April,",
			"05": "May,",
			"06": "June,",
			"07": "July,",
			"08": "August,",
			"09": "September,",
			10: "October,",
			11: "November,",
			12: "December,",
		};
		const year = date.substring(0, 4);
		const month = monthsReversed[date.substring(4, 6)];
		const day = date.substring(6);

		return `${day} ${month} ${year}`;
	};

	const toggleStar = (paper) => {
		setHighlightedStars((prev) => {
			const isStarred = prev.some((p) => p.id === paper?.id);

			const newStars = isStarred
				? prev.filter((p) => p.id !== paper?.id)
				: [...prev, paper];

			localStorage.setItem("highlightedStars", JSON.stringify(newStars));
			return newStars;
		});
	};

	return paper ? (
		<div>
			<NavBar />
			<div className="page-main">
				<div className="paper">
					<div className="button">
						<button className="return" type="button" onClick={goBack}>
							Go Back
						</button>
					</div>
					<div className="title-container">
						<h3
							style={{
								textAlign: "center",
								paddingBottom: "10px",
							}}
						>
							<Content content={paper?.title} />
						</h3>
						<img
							width={20}
							height={20}
							src={
								highlightedStars.some((p) => p.id === paper?.id)
									? "/filled_star.png"
									: "/empty_star.png"
							}
							onClick={() => toggleStar(paper)}
							className="star-icon"
							alt="star icon"
						/>
					</div>
					<p>
						<strong>Authors:</strong>{" "}
						{paper?.authors?.map((author, index) => (
							<span key={`${author}_detail`}>
								{author}
								{index < paper?.authors?.length - 1 ? ", " : ""}
							</span>
						))}
					</p>
					<p>
						<strong>arXiv ID:</strong> {replaceID(paper?.id)}
					</p>
					<p>
						<strong>DOI:</strong> {paper?.doi}
					</p>
					<strong>Links:</strong>
					{paper?.links?.map((link) => (
						<a href={link} key={link} target="_blank" rel="noreferrer">
							<br />
							{link}
						</a>
					))}
					<p>
						<strong>Categories:</strong>{" "}
						{paper?.categories?.map((category, index) => (
							<span key={category}>
								{category}
								{index < paper?.categories?.length - 1 ? ", " : ""}
							</span>
						))}
					</p>
					<p>
						<strong>Submission Date:</strong> {numToDate(String(paper?.date))}
					</p>
					<p>
						<strong>Update Date:</strong> {numToDate(String(paper?.updated))}
					</p>
					<p>
						<strong>Comments:</strong> {paper?.comments}
					</p>
					<p>
						<strong>Primary Category:</strong> {paper?.primary_category}
					</p>
					<p>
						<strong>Journal Ref:</strong> {paper?.journal_ref}
					</p>
					<div className="abstract">
						<strong>Abstract:</strong> <br />
						<Content content={paper?.summary} />
					</div>
					<p>
						<strong>Materials:</strong>{" "}
						{Array.isArray(paper?.MAT) ? (
							paper?.MAT?.map((item, index) => (
								<span key={index}>
									{item}
									{index < paper?.MAT.length - 1 ? ", " : ""}
								</span>
							))
						) : (
							<span>N/A</span>
						)}
					</p>
					<p>
						<strong>Descriptions of Sample:</strong>{" "}
						{Array.isArray(paper?.DSC) ? (
							paper?.DSC?.map((item, index) => (
								<span key={index}>
									{item}
									{index < paper?.DSC.length - 1 ? ", " : ""}
								</span>
							))
						) : (
							<span>N/A</span>
						)}
					</p>
					<p>
						<strong>Symmetry or Phase Labels:</strong>{" "}
						{Array.isArray(paper?.SPL) ? (
							paper?.SPL?.map((item, index) => (
								<span key={index}>
									{item}
									{index < paper?.SPL.length - 1 ? ", " : ""}
								</span>
							))
						) : (
							<span>N/A</span>
						)}
					</p>
					<p>
						<strong>Synthesis Methods:</strong>{" "}
						{Array.isArray(paper?.SMT) ? (
							paper?.SMT?.map((item, index) => (
								<span key={index}>
									{item}
									{index < paper?.SMT.length - 1 ? ", " : ""}
								</span>
							))
						) : (
							<span>N/A</span>
						)}
					</p>
					<p>
						<strong>Characterization Methods:</strong>{" "}
						{Array.isArray(paper?.CMT) ? (
							paper?.CMT?.map((item, index) => (
								<span key={index}>
									{item}
									{index < paper?.CMT.length - 1 ? ", " : ""}
								</span>
							))
						) : (
							<span>N/A</span>
						)}
					</p>
					<p>
						<strong>Properties:</strong>{" "}
						{[
							...(Array.isArray(paper?.PRO) ? paper?.PRO : []),
							...(Array.isArray(paper?.PVL) ? paper?.PVL : []),
							...(Array.isArray(paper?.PUT) ? paper?.PUT : []),
						].length > 0 ? (
							[
								...(Array.isArray(paper?.PRO) ? paper?.PRO : []),
								...(Array.isArray(paper?.PVL) ? paper?.PVL : []),
								...(Array.isArray(paper?.PUT) ? paper?.PUT : []),
							].map((item, index, array) => (
								<span key={index}>
									{item}
									{index < array.length - 1 ? ", " : ""}
								</span>
							))
						) : (
							<span>N/A</span>
						)}
					</p>
					<p>
						<strong>Applications:</strong>{" "}
						{Array.isArray(paper?.APL) ? (
							paper?.APL?.map((item, index) => (
								<span key={index}>
									{item}
									{index < paper?.APL.length - 1 ? ", " : ""}
								</span>
							))
						) : (
							<span>N/A</span>
						)}
					</p>
				</div>
			</div>
		</div>
	) : (
		<div className="detail-loader">
			<p>Loading ...</p>
			<TailSpin color="#00BFFF" height={100} width={100} />
		</div>
	);
}

export default PaperDetail;

// MAT: material
// DSC: description of sample
// SPL: symmetry or phase label
// SMT: synthesis method
// CMT: characterization method
// PRO: property - may also include PVL (property value) or PUT (property unit)
// APL: application
