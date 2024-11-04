import React, { useState, useEffect, useRef } from "react";

// Modal component
const SearchSyntaxModal = ({ isOpen, onClose }) => {
	const modalRef = useRef();

	// Effect to handle clicks outside the modal
	useEffect(() => {
		// Close the modal if the user clicks outside of it
		const handleClickOutside = (event) => {
			if (modalRef.current && !modalRef.current.contains(event.target)) {
				onClose();
			}
		};

		// Add event listener only if the modal is open
		if (isOpen) {
			document.addEventListener("mousedown", handleClickOutside);
		}

		// Cleanup event listener when the modal is closed or component unmounts
		return () => {
			document.removeEventListener("mousedown", handleClickOutside);
		};
	}, [isOpen, onClose]);

	if (!isOpen) return null;

	return (
		<div style={styles.modalOverlay}>
			<div ref={modalRef} style={styles.modalContent}>
				<h2 style={styles.heading}>Search Syntax Guide</h2>
				<p style={styles.text}>
					You can use the following syntax in your searches:
				</p>
				<ul style={styles.list}>
					<li>
						<strong>AND:</strong> Use the word <code>and</code> to require both
						terms.
						<p style={styles.example}>
							Example: <code>apple and banana | fruits</code> <br />
							Searches for "fruits" must include both "apple" and "banana."
						</p>
					</li>
					<li>
						<strong>OR:</strong> Use the word <code>or</code> to include
						alternative terms.
						<p style={styles.example}>
							Example: <code>apple or banana | fruits</code> <br />
							Searches for "fruits" must include either "apple" or "banana."
						</p>
					</li>
					<li>
						<strong>NOT:</strong> Use the word <code>not</code> to exclude a
						term.
						<p style={styles.example}>
							Example: <code>not banana | fruits</code> <br />
							Searches for "fruits" must exclude "banana."
						</p>
					</li>
					<li>
						<strong>MUST:</strong> Use the word <code>must</code> to specify a
						required term.
						<p style={styles.example}>
							Example: <code>must apple | fruits</code> <br />
							Searches for "fruits" must include "apple."
						</p>
					</li>
				</ul>
				<button type="button" onClick={onClose} style={styles.closeButton}>
					Close
				</button>
			</div>
		</div>
	);
};

// Main component to display the button and modal
const SearchSyntax = () => {
	const [isModalOpen, setIsModalOpen] = useState(false);

	const openModal = () => {
		setIsModalOpen(true);
	};

	const closeModal = () => {
		setIsModalOpen(false);
	};

	return (
		<div>
			<button type="button" onClick={openModal} style={styles.openButton}>
				Search Syntax Help
			</button>
			<SearchSyntaxModal isOpen={isModalOpen} onClose={closeModal} />
		</div>
	);
};

// Inline styles for the modal and buttons
const styles = {
	modalOverlay: {
		position: "fixed",
		top: 0,
		left: 0,
		right: 0,
		bottom: 0,
		backgroundColor: "rgba(0, 0, 0, 0.7)",
		display: "flex",
		alignItems: "center",
		justifyContent: "center",
		zIndex: 1000,
	},
	modalContent: {
		backgroundColor: "#fff",
		padding: "20px",
		borderRadius: "8px",
		maxWidth: "500px",
		width: "100%",
		boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
		textAlign: "left",
	},
	heading: {
		textAlign: "left",
	},
	text: {
		textAlign: "left",
		marginBottom: "15px",
	},
	list: {
		paddingLeft: "20px",
		textAlign: "left",
	},
	example: {
		marginTop: "8px",
		fontStyle: "italic",
		textAlign: "left",
	},
	closeButton: {
		marginTop: "20px",
		padding: "10px 20px",
		backgroundColor: "#007bff",
		color: "#fff",
		border: "none",
		borderRadius: "4px",
		cursor: "pointer",
	},
	openButton: {
		padding: "10px 20px",
		backgroundColor: "#007bff",
		color: "#fff",
		border: "none",
		borderRadius: "4px",
		cursor: "pointer",
	},
};

export default SearchSyntax;
