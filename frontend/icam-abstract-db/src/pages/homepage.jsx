import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/homepage.css';
import Search from '../components/search.jsx';
import NavBar from '../components/navbar.jsx';

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
        `&date=${searchParams.date}`
    );
  };

  return (
    <div>
      <NavBar searchParams={searchParams}/>
      <div className="main">
        <p className="home-title" onClick={() => navigate('/')}>
          ICAM Superconductivity Database
        </p>
        <br />
        <div onClick={() => goToSearch('all')}>
          <GoTo />
        </div>
        <br />
        <Search searchParams={searchParams} />
        <section className="overview" style={{ marginTop: "40px" }}>
          <h2>Overview</h2>
          <p>
            This search engine provides an efficient and user-friendly way to explore scientific literature in the field of superconductivity. Utilize advanced search options and natural language processing to find relevant papers.
          </p>
        </section>
        <section className="features">
          <h2>Features</h2>
          <ul>
            <li><strong>Advanced Search:</strong> Find papers using natural language queries.</li>
            <li><strong>Sorting and Filtering:</strong> Sort results by relevance or date, and filter based on various criteria including date range.</li>
            <li><strong>Pagination:</strong> View results with easy navigation and customizable results per page.</li>
            <li><strong>Answer Generation:</strong> Get answers to specific questions based on paper abstracts.</li>
            <li><strong>Performance:</strong> Optimized for fast retrieval of frequently accessed papers.</li>
            <li><strong>Fuzzy Search:</strong> Improved search flexibility for authors and categories.</li>
          </ul>
        </section>
        <section className="architecture">
          <h2>Architecture</h2>
          <h3>Backend</h3>
          <ul>
            <li><strong>Data Management:</strong> Efficient storage and retrieval of paper metadata.</li>
            <li><strong>Query Processing:</strong> Advanced algorithms for accurate and fast search results.</li>
            <li><strong>Performance Optimization:</strong> Techniques to ensure fast and reliable access to data.</li>
          </ul>
          <h3>Frontend</h3>
          <ul>
            <li><strong>User Interface:</strong> Intuitive and responsive design for easy navigation and use.</li>
          </ul>
          <h3>Deployment</h3>
          <ul>
            <li><strong>Scalable Hosting:</strong> Ensures reliability and performance.</li>
          </ul>
        </section>
        <section className="usage">
          <h2>Usage</h2>
          <h3>Searching</h3>
          <p>Use natural language queries for titles and abstracts to get the best results.</p>
          <p>Use keywords for authors and categories.</p>
          <h3>Filtering</h3>
          <p>Filter papers by date range using the date picker.</p>
          <h3>Sorting</h3>
          <p>Sort results by relevance or publication date using the dropdown menu.</p>
          <h3>Pagination</h3>
          <p>Customize results per page and navigate through pages easily.</p>
          <h3>Performance Tips</h3>
          <p>For optimal performance, refine your search queries to find relevant results quickly. Frequently accessed papers load faster.</p>
        </section>
        <section className="performance">
          <h2>Performance</h2>
          <p>Fast retrieval of results, especially for frequently accessed papers.</p>
        </section>
        <section className="contact">
          <h2>Contact</h2>
          <p><strong>Lead Developer:</strong> Vikram Penumarti (vpenumarti@ucdavis.edu)</p>
        </section>
        <p>Funded by the Institute for Complex Adaptive Matter</p>
        <p>Thank you to arXiv for use of its open access interoperability.</p>
        <p>Powered with Elasticsearch & Meta Llama 3</p>
      </div>
    </div>
  );
}

function GoTo() {
  return (
    <button className="learn-more">
      <span className="circle" aria-hidden="true">
        <span className="icon arrow"></span>
      </span>
      <span className="button-text">Go To Papers</span>
    </button>
  );
}

export default HomePage;
