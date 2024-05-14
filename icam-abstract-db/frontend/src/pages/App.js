import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { PaperDetail, Papers } from './papers'
import { HomePage } from './homepage'
import React, { useState } from 'react';

function App() {
  const [searchParams, setSearchParams] = useState({
    per_page: 20,
    page: 1,
    query: "all",
    sorting: "Most-Relevant",
  });

  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage searchParams={searchParams} />} />
        <Route path="/papers" element={<Papers searchParams={searchParams} setSearchParams={setSearchParams}/>} exact />
        <Route path="/papers/:id" element={<PaperDetail searchParams={searchParams} />} />
      </Routes>
    </Router>
  );
}

export default App;