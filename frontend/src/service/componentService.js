// frontend/src/service/componentService.js
import httpClient from './axios';

const ComponentService = {
  getAllComponents: async () => {
    const response = await httpClient.get('components/');
    return response.data;
  },
  
  getComponentsByType: async (type) => {
    const response = await httpClient.get(`components/?type=${type}`);
    return response.data;
  },
  
  getComponentTypes: async () => {
    const response = await httpClient.get('components/types/');
    return response.data;
  },
  
  getComponentCategories: async () => {
    const response = await httpClient.get('components/categories/');
    return response.data;
  }
};

export default ComponentService;