import React from "react";
import { Link } from "react-router-dom";
import "../styles/navbar.css";

function NavBar({ searchParams }) {
	const papers = `/papers?page=${searchParams.page}&per_page=${searchParams.per_page}&query=${searchParams.query}&sort=${searchParams.sorting}&pages=${searchParams.pages}&term=${searchParams.term}&date=${searchParams.date}`;

	return (
		<nav className="navbar">
			<div className="navbar-container">
				<Link to="/" className="navbar-logo">
					ICAM Superconductivity Database
				</Link>
				<ul className="navbar-menu">
					<li className="navbar-item">
						<Link to={papers} className="navbar-link">
							Papers
						</Link>
					</li>
					<li className="navbar-item">
						<Link to="/favorites" className="navbar-link">
							Favorites
						</Link>
					</li>
					<li className="navbar-item">
						<Link to="/about" className="navbar-link">
							About
						</Link>
					</li>
				</ul>
			</div>
		</nav>
	);
}

export default NavBar;
