// Configuration for environment variables
window.ENV = {
  API_BASE_URL: window.location.hostname === 'localhost' 
    ? 'http://localhost:8080' 
    : 'https://nongbuxxbackend-production.up.railway.app'
};
