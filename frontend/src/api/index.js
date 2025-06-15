import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // Adjust the base URL as needed

export const fetchExperts = async (query, page = 1, pageSize = 10, filterSkill = null, experience = null, sortBy = null) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/search`, {
            query,
            page,
            page_size: pageSize,
            filter_skill: filterSkill,
            experience,
            sort_by: sortBy
        });
        return response.data;
    } catch (error) {
        console.error('Error fetching experts:', error);
        throw error;
    }
};

export const fetchExpertSkills = async (username) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/experts/${username}/skills`);
        return response.data;
    } catch (error) {
        console.error('Error fetching expert skills:', error);
        throw error;
    }
};

export const fetchExpertProjects = async (username) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/experts/${username}/projects`);
        return response.data;
    } catch (error) {
        console.error('Error fetching expert projects:', error);
        throw error;
    }
};

export const fetchAllExperts = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/experts`);
        return response.data;
    } catch (error) {
        console.error('Error fetching all experts:', error);
        throw error;
    }
};

export const fetchAllSkills = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/skills`);
        return response.data;
    } catch (error) {
        console.error('Error fetching all skills:', error);
        throw error;
    }
};

export const fetchAllProjects = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/projects`);
        return response.data;
    } catch (error) {
        console.error('Error fetching all projects:', error);
        throw error;
    }
};