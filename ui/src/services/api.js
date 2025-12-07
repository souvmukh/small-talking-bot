import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

class VoiceAssistantAPI {
    async startConversation() {
        try {
            const response = await axios.post(`${API_BASE_URL}/conversation/start`);
            return response.data;
        } catch (error) {
            console.error('Error starting conversation:', error);
            throw error;
        }
    }

    async stopConversation() {
        try {
            const response = await axios.post(`${API_BASE_URL}/conversation/stop`);
            return response.data;
        } catch (error) {
            console.error('Error stopping conversation:', error);
            throw error;
        }
    }

    async getStatus() {
        try {
            const response = await axios.get(`${API_BASE_URL}/status`);
            return response.data;
        } catch (error) {
            console.error('Error getting status:', error);
            throw error;
        }
    }
}

export default new VoiceAssistantAPI();
