import React, { useEffect, useState } from 'react';
import axiosInstance from './axiosConfig';
import './History.css'; // Ensure you have the corresponding CSS file

const History = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          alert('You need to log in first');
          return;
        }

        const response = await axiosInstance.get('/api/history/', {
          headers: {
            'Authorization': `Token ${token}`
          }
        });

        setHistory(response.data);
      } catch (error) {
        console.error('Failed to fetch history:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="history-container">
      <h1>Historique des Scraps</h1>
      <table className="history-table">
        <thead>
          <tr>
            <th>Ville</th>
            <th>Magasin</th>
            <th>Tickets en Cours</th>
            <th>Type de Scrap</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          {history.map((entry, index) => (
            <tr key={index}>
              <td>{entry.ville}</td>
              <td>{entry.magasin}</td>
              <td>{entry.nb_ticket_en_cours}</td>
              <td>{entry.type_scrap}</td>
              <td>{new Date(entry.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default History;
