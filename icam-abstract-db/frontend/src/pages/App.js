import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { PaperDetail, Papers } from './papers'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/papers" element={<Papers />} exact />
        <Route path="/papers/:id" element={<PaperDetail />} />
      </Routes>
    </Router>
  );
}

export default App;