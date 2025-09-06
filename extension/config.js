// Configuration for the Info Reeler extension
const CONFIG = {
    // API URL - Update this to your deployed Vercel URL after deployment
    API_URL: "http://localhost:8000", // Change this to your Vercel URL
    
    // Alternative: Use environment-based configuration
    // API_URL: window.location.hostname === 'localhost' ? "http://localhost:8000" : "https://your-project.vercel.app",
    
    // API endpoints
    ENDPOINTS: {
        GENERATE_REEL: "/generate-reel",
        HEALTH: "/health",
        DOWNLOAD: "/download"
    }
};

// Helper function to get full API URL
function getApiUrl(endpoint = "") {
    return CONFIG.API_URL + endpoint;
}
