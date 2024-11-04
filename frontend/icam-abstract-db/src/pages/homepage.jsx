import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/homepage.css";
import Search from "../components/search.jsx";
import NavBar from "../components/navbar.jsx";
import SearchSyntax from "../components/search-syntax.jsx";

function HomePage({ searchParams }) {
	const navigate = useNavigate();

	const goToSearch = (query) => {
		let quer = query;
		if (query === "") {
			quer = "all";
		}
		navigate(
			`/papers?page=${searchParams.page}&per_page=${searchParams.per_page}` +
				`&query=${quer}&sort=${searchParams.sorting}` +
				`&pages=${searchParams.pages}&term=${searchParams.term}` +
				`&date=${searchParams.date}`,
		);
	};

	return (
		<div>
			<NavBar searchParams={searchParams} />
			<div className="main">
				<p className="home-title" onClick={() => navigate("/")}>
					ICAM Superconductivity Database
				</p>
				<br />
				<div onClick={() => goToSearch("all")}>
					<GoTo />
				</div>
				<br />
				<Search searchParams={searchParams} />
				<SearchSyntax />
				<section className="overview" style={{ marginTop: "40px" }}>
					<h2>Overview</h2>
					<p>
						This search engine provides an efficient and user-friendly way to
						explore scientific literature in the field of superconductivity.
						Utilize advanced search options and natural language processing to
						find relevant papers.
					</p>
				</section>
				<section className="features">
					<h2>Features</h2>
					<ul>
						<li>
							<strong>Vector Search:</strong> Find papers using natural language
							queries.
						</li>
						<li>
							<strong>Fuzzy Search:</strong> Improved search flexibility for
							authors and categories.
						</li>
						<li>
							<strong>Performance:</strong> Optimized for fast retrieval of
							frequently accessed papers.
						</li>
						<li>
							<strong>Property Extraction:</strong> View material properties
							based on paper abstracts.
						</li>
						<li>
							<strong>Custom Search Parameters:</strong> Customize search
							parameters to view results unique to your needs.
						</li>
						<li>
							<strong>Favorites:</strong> Favorite research papers to revisit
							them later.
						</li>
					</ul>
				</section>
				<section className="usage">
					<h2>Usage</h2>
					<ul>
						<li>Search by Abstract, titles, authors, and categories</li>
						<li>
							Use natural language queries for titles and abstracts to get the
							best results.
						</li>
						<li>Use keywords for authors and categories.</li>
						<li>Sort results by relevance or publication date.</li>
						<li>Customize number of results per page and page limit.</li>
						<li>Filter papers by date range using the date picker.</li>
					</ul>
				</section>
				<section className="performance">
					<h2>Performance Tips</h2>
					<ul>
						<li>
							Frequently searched queries will load faster due to caching.
						</li>
						<li>
							Reduce the number of pages and results per page for faster
							loading.
						</li>
						<li>
							Earlier pages will load faster than later pages for vector
							searching.
						</li>
					</ul>
				</section>
				<section className="contact">
					<h2>Contact</h2>
					<p>
						<strong>Lead Developer:</strong> Vikram Penumarti
						(vpenumarti@ucdavis.edu)
					</p>
				</section>
				<p>Funded by the Institute for Complex Adaptive Matter</p>
				<p>Thank you to arXiv for use of its open access interoperability.</p>
			</div>
		</div>
	);
}

function GoTo() {
	return (
		<button className="learn-more" type="button">
			<span className="circle" aria-hidden="true">
				<span className="icon arrow" />
			</span>
			<span className="button-text">Go To Papers</span>
		</button>
	);
}

export default HomePage;
