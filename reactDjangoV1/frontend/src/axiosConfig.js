import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000', // Assurez-vous que l'URL correspond à celle de votre backend
  timeout: 600000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

export default axiosInstance;


