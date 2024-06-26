import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { TailSpin } from 'react-loader-spinner';
import Content from '../components/mathjax';
import '../styles/paper-detail.css';

function PaperDetail({ searchParams }) {
  const [paper, setPaper] = useState(null);

  const navigate = useNavigate();
  const { id } = useParams();

  useEffect(() => {
    fetch(`http://localhost:8080/api/papers/${id}`)
      .then((response) => response.json())
      .then((data) => {
        setPaper(data);
      });
  }, [id]);

  const goBack = () => {
    const startDate = new Date(0);
    const endDate = new Date();
    const formattedStart = startDate.toISOString().split('T')[0].replaceAll("-", "");
    const formattedEnd = endDate.toISOString().split('T')[0].replaceAll("-", "");
  
    const dateRange = `${formattedStart}-${formattedEnd}`;

    navigate(
      `/papers?page=${searchParams.page}&per_page=${searchParams.per_page}` +
        `&query=${searchParams.query}&sort=${searchParams.sorting}` +
        `&pages=${searchParams.pages}&term=${searchParams.term}` 
        +`&date=${searchParams.date}`,
    );
  };

  const replaceID = (id) => {
    const lastIndex = id.lastIndexOf('-');

    if (lastIndex !== -1) {
      return id.substring(0, lastIndex) + '/' + id.substring(lastIndex + 1);
    } else {
      return id;
    }
  };

  const numToDate = (date) => {
    const monthsReversed = {
      '01': 'January,',
      '02': 'February,',
      '03': 'March,',
      '04': 'April,',
      '05': 'May,',
      '06': 'June,',
      '07': 'July,',
      '08': 'August,',
      '09': 'September,',
      10: 'October,',
      11: 'November,',
      12: 'December,',
    };
    const year = date.substring(0, 4);
    const month = monthsReversed[date.substring(4, 6)];
    const day = date.substring(6);

    return day + ' ' + month + ' ' + year;
  };

  return paper ? (
    <div className="paper">
      <div className="button">
        <button className="return" onClick={goBack}>
          Go Back
        </button>
      </div>
      <u>
        <Content content={paper.title} />
      </u>
      <p>
        <strong>Authors:</strong>{' '}
        {paper.authors.map((author, index) => (
          <span key={index}>
            {author}
            {index < paper.authors.length - 1 ? ', ' : ''}
          </span>
        ))}
      </p>
      <p>
        <strong>arXiv ID:</strong> {replaceID(paper.id)}
      </p>
      <p>
        <strong>DOI:</strong> {paper.doi}
      </p>
      <strong>Links:</strong>
      {paper.links.map((link, index) => (
        <a href={link} key={index} target="_blank" rel="noreferrer">
          <br></br>
          {link}
        </a>
      ))}
      <p>
        <strong>Categories:</strong>{' '}
        {paper.categories.map((category, index) => (
          <span key={index}>
            {category}
            {index < paper.categories.length - 1 ? ', ' : ''}
          </span>
        ))}
      </p>
      <p>
        <strong>Submission Date:</strong> {numToDate(String(paper.date))}
      </p>
      <p>
        <strong>Update Date:</strong> {numToDate(String(paper.updated))}
      </p>
      <p>
        <strong>Comments:</strong> {paper.comments}
      </p>
      <p>
        <strong>Primary Category:</strong> {paper.primary_category}
      </p>
      <p>
        <strong>Journal Ref:</strong> {paper.journal_ref}
      </p>
      <div className="abstract">
        <strong>Abstract:</strong> <br></br>
        <Content content={paper.summary} />
      </div>
    </div>
  ) : (
    <div className="detail-loader">
      <p>Loading ...</p>
      <TailSpin color="#00BFFF" height={100} width={100} />
    </div>
  );
}

export default PaperDetail;
