import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/homepage.css";
import Search from "../components/search.jsx";
import NavBar from "../components/navbar.jsx";
import SearchSyntax from "../components/search-syntax.jsx";

function HomePage() {
	const currentDate = new Date();
	const now = currentDate.toISOString().slice(0, 10).replaceAll(/-/g, "");

	const navigate = useNavigate();

	const goToSearch = (query, page, term) => {
		let quer = query;
		if (query === "") {
			quer = "all";
		}
		navigate(
			`${page}?page=1&per_page=20&query=${quer}&sort=Most-Relevant&term=${term}&date=00000000-${now}`,
		);
		window.scrollTo({ top: 0, behavior: "smooth" });
	};

	return (
		<div>
			<NavBar />
			<div className="main">
				<p className="home-title">ICAM Materials Database</p>
				<div onClick={() => goToSearch("all", "/papers", "Abstract")}>
					<GoTo />
				</div>
				<br />
				<Search
					searchParams={{
						per_page: 20,
						page: 1,
						query: "all",
						sorting: "Most-Relevant",
						term: "Abstract",
						date: `00000000-${now}`,
					}}
					to="/papers"
				/>
				<div style={{ marginTop: "-20px" }}>
					<SearchSyntax />
				</div>

				<section className="media-section media-container">
					<div className="media-placeholder">
						<a
							style={{ cursor: "pointer" }}
							onClick={() => goToSearch("all", "/papers", "Abstract")}
						>
							<img
								alt="Search Papers"
								src="/search-papers.png"
								className="feature-image"
							/>
						</a>
						<a
							style={{ cursor: "pointer" }}
							onClick={() => goToSearch("all", "/properties", "Material")}
						>
							<img
								alt="Search Materials"
								src="/search-properties.png"
								className="feature-image"
							/>
						</a>
					</div>
				</section>

				<section
					id="features"
					className="features-section homepage-container"
					style={{ marginBottom: "40px" }}
				>
					<h3>Features</h3>
					<div className="features-grid">
						<div
							className="feature-card"
							style={{ cursor: "pointer" }}
							onClick={() => goToSearch("all", "/papers", "Abstract")}
						>
							<h4>Search Papers</h4>
							<p>
								Leverage advanced AI technology to locate papers based on their
								semantic relevance, offering a more intuitive search experience
								beyond traditional keyword matching.
							</p>
						</div>
						<div
							className="feature-card"
							style={{ cursor: "pointer" }}
							onClick={() => goToSearch("all", "/properties", "Material")}
						>
							<h4>Search Properties</h4>
							<p>
								Explore research papers through AI-extracted insights, allowing
								you to search by specific materials, synthesis methods, unique
								properties, and potential applications for a deeper
								understanding.
							</p>
						</div>
						<div
							className="feature-card"
							style={{ cursor: "pointer" }}
							onClick={() => {
								navigate("/favorites");
								window.scrollTo({ top: 0, behavior: "smooth" });
							}}
						>
							<h4>Favorites</h4>
							<p>
								Bookmark and save your favorite papers for quick access anytime,
								all without the need to sign in—perfect for seamless, on-the-go
								research.
							</p>
						</div>
					</div>
				</section>

				{/* <section id="about" className="about-section homepage-container">
					<h3>About Us</h3>
					<p>
						Our mission is to make scientific research more accessible by
						creating a user-friendly and robust search platform tailored to
						material science researchers.
					</p>
					<div className="media-placeholder">
						<p>[Insert Team/Platform Overview Image or Video here]</p>
					</div>
				</section> */}

				<section id="contact" className="contact-section">
					<div className="homepage-container text-center">
						<h3>Get in Touch</h3>
						<p style={{ paddingBottom: "10px" }}>
							Have questions? Reach out to us for more information about our
							platform.
						</p>
						<a
							href="mailto:vpenumarti@ucdavis.edu"
							rel="noopener noreferrer"
							className="cta-button"
						>
							Contact Us
						</a>
					</div>
				</section>

				<section
					id="contribute"
					className="contribute-section homepage-container"
				>
					<h3>Contribute</h3>
					<p>
						Interested in contributing to our platform? Check out our GitHub
						repository to learn more and start collaborating with us.
					</p>
					<a
						href="https://github.com/vikram087/icam-materials-database"
						target="_blank"
						rel="noopener noreferrer"
						className="github-link"
					>
						<img
							src="/github-mark/github-mark.png"
							alt="GitHub"
							className="github-image"
						/>
					</a>
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
			<span className="button-text">Search Papers</span>
		</button>
	);
}

export default HomePage;
