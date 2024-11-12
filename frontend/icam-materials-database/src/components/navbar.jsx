import React from "react";
import { Link } from "react-router-dom";
import "../styles/navbar.css";

function NavBar() {
	const currentDate = new Date();
	const now = currentDate.toISOString().slice(0, 10).replaceAll(/-/g, "");

	const papers = `/papers?page=1&per_page=20&query=all&sort=Most-Relevant&term=Abstract&date=00000000-${now}`;
	const material = `/properties?page=1&per_page=20&query=all&sort=Most-Relevant&term=Material&date=00000000-${now}`;

	return (
		<nav className="navbar">
			<div className="navbar-container">
				<Link to="/" className="navbar-logo">
					ICAM Materials Database
				</Link>
				<ul className="navbar-menu">
					<li className="navbar-item">
						<Link to={papers} className="navbar-link">
							Papers
						</Link>
					</li>
					<li className="navbar-item">
						<Link to={material} className="navbar-link">
							Properties
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
