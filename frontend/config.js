// Configuration for environment variables
window.ENV = {
  API_BASE_URL: window.location.hostname === 'localhost' 
    ? 'http://localhost:8081' 
    : 'https://nongbuxxbackend-production.up.railway.app'
};
