import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Papers from './papers.jsx';
import HomePage from './homepage.jsx';
import { useState } from 'react';
import PaperDetail from './paper-detail.jsx';

function App() {
  const currentDate = new Date();
  const now = currentDate.toISOString().slice(0, 10).replaceAll(/-/g, '');

  const [searchParams, setSearchParams] = useState({
    per_page: 20,
    page: 1,
    query: 'all',
    sorting: 'Most-Relevant',
    pages: 30,
    term: 'Abstract',
    date: `00000000-${now}`,
  });

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
            />
          }
          exact
        />
        <Route
          path="/papers/:id"
          element={<PaperDetail searchParams={searchParams} />}
        />
      </Routes>
    </Router>
  );
}

export default App;
