import '../styles/homepage.css';
import Search from '../components/search.jsx';
import { useNavigate } from 'react-router-dom';

function HomePage({ searchParams }) {
  const navigate = useNavigate();

  const goToSearch = (query) => {
    if (query === '') {
      query = 'all';
    }
    navigate(
      `/papers?page=${searchParams.page}&per_page=${searchParams.per_page}` +
        `&query=${query}&sort=${searchParams.sorting}` +
        `&pages=${searchParams.pages}&term=${searchParams.term}` +
        `&date=${searchParams.date}`,
    );
  };

  return (
    <div className="main">
      <p className="home-title" onClick={() => navigate('/')}>
        ICAM Superconductivity Database
      </p>
      <br></br>
      <div className="go-to-papers" onClick={() => goToSearch('all')}>
        <button className="go-to-button">Go to Papers</button>
      </div>
      <br></br>
      <Search searchParams={searchParams} />
      <p>Funded by the Institute for Complex Adaptive Matter</p>
      <p>Powered with Elasticsearch</p>
    </div>
  );
}

export default HomePage;
