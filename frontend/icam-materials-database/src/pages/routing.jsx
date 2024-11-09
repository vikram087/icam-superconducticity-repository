import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Papers from "./papers.jsx";
import HomePage from "./homepage.jsx";
import { useState } from "react";
import PaperDetail from "./paper-detail.jsx";
import Favorites from "./favorites.jsx";
import About from "./about.jsx";
import Table from "./material-search.jsx";

function App() {
	const currentDate = new Date();
	const now = currentDate.toISOString().slice(0, 10).replaceAll(/-/g, "");

	const [searchParams, setSearchParams] = useState({
		per_page: 20,
		page: 1,
		query: "all",
		sorting: "Most-Relevant",
		term: "Abstract",
		date: `00000000-${now}`,
	});

	const [tableParams, setTableParams] = useState({
		per_page: 20,
		page: 1,
		query: "all",
		sorting: "Most-Relevant",
		term: "material",
		date: `00000000-${now}`,
	});

	const [prevUrl, setPrevUrl] = useState("");
	const [paperToUse, setPaperToUse] = useState({});

	return (
		<Router>
			<Routes>
				<Route path="/" element={<HomePage />} />
				<Route
					path="/papers"
					element={
						<Papers
							setPrevUrl={setPrevUrl}
							searchParams={searchParams}
							setSearchParams={setSearchParams}
							setPaperToUse={setPaperToUse}
						/>
					}
					exact
				/>
				<Route
					path="/paper/:id"
					element={<PaperDetail prevUrl={prevUrl} paper={paperToUse} />}
				/>
				<Route
					path="/favorites"
					element={<Favorites setPrevUrl={setPrevUrl} />}
				/>
				<Route path="/about" element={<About />} />
				<Route
					path="/material-search"
					element={
						<Table
							setPrevUrl={setPrevUrl}
							tableParams={tableParams}
							setTableParams={setTableParams}
						/>
					}
				/>
			</Routes>
		</Router>
	);
}

export default App;
