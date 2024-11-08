import React from "react";
import "../styles/about.css";
import NavBar from "../components/navbar";

function About() {
	return (
		<div>
			<NavBar />
			<div className="about-container">
				<h1 style={{ marginTop: "-10px" }}>About Us</h1>
				<p className="mission-statement">
					Our mission is to provide a comprehensive and user-friendly search
					engine to explore the scientific literature in the field of materials
					science. We aim to make research more accessible and efficient for
					scientists and researchers worldwide.
				</p>
				<div className="people-cards">
					<div className="card">
						<img
							src="/vikram.jpg"
							alt="Vikram Penumarti"
							className="card-img"
						/>
						<h2>Vikram Penumarti</h2>
						<p>
							Vikram Penumarti is a 3rd year undergraduate student at UC Davis
							studying Computer Science. With the guidance of Dr. Rajiv Singh,
							he created this website utilizing knowledge of computer science
							and materials science.
						</p>
					</div>
					<div className="card">
						<img src="/singh.jpg" alt="Dr. Rajiv Singh" className="card-img" />
						<h2>Dr. Rajiv Singh</h2>
						<p>
							In the study of Solid State Physics, Professor Singh's work has
							focused on magnetism and superconductivity, where he has developed
							and studied statistical models that exhibit exotic and novel
							paradigms of cooperative many-body behavior.
						</p>
					</div>
				</div>
			</div>
		</div>
	);
}

export default About;
