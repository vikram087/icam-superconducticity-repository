import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Papers from "./papers.jsx";
import HomePage from "./homepage.jsx";
import { useState } from "react";
import PaperDetail from "./paper-detail.jsx";
import Favorites from "./favorites.jsx";
import About from "./about.jsx";

function App() {
	const currentDate = new Date();
	const now = currentDate.toISOString().slice(0, 10).replaceAll(/-/g, "");

	const [searchParams, setSearchParams] = useState({
		per_page: 20,
		page: 1,
		query: "all",
		sorting: "Most-Relevant",
		pages: 30,
		term: "Abstract",
		date: `00000000-${now}`,
	});

	const [prevUrl, setPrevUrl] = useState("");

	return (
		<Router>
			<Routes>
				<Route path="/" element={<HomePage searchParams={searchParams} />} />
				<Route
					path="/papers"
					element={
						<Papers
							searchParams={searchParams}
							setSearchParams={setSearchParams}
							setPrevUrl={setPrevUrl}
						/>
					}
					exact
				/>
				<Route
					path="/papers/:id"
					element={
						<PaperDetail searchParams={searchParams} prevUrl={prevUrl} />
					}
				/>
				<Route
					path="/favorites"
					element={
						<Favorites searchParams={searchParams} setPrevUrl={setPrevUrl} />
					}
				/>
				<Route path="/about" element={<About searchParams={searchParams} />} />
			</Routes>
		</Router>
	);
}

export default App;
