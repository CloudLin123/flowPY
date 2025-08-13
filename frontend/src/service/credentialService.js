// frontend/src/service/credentialService.js
import httpClient from './axios';
import { handleApiError } from './errorHandler';

const CredentialService = {
  /**
   * 获取所有凭证
   * @returns {Promise<Array>} 凭证列表
   */
  getAllCredentials: async () => {
    try {
      const response = await httpClient.get('credentials/');
      return response.data;
    } catch (error) {
      handleApiError(error, '获取凭证列表失败');
      return [];
    }
  },
  
  /**
   * 获取单个凭证详情
   * @param {string|number} id 凭证ID
   * @returns {Promise<Object|null>} 凭证详情或null
   */
  getCredential: async (id) => {
    try {
      const response = await httpClient.get(`credentials/${id}/`);
      return response.data;
    } catch (error) {
      handleApiError(error, '获取凭证详情失败');
      return null;
    }
  },
  
  /**
   * 创建新凭证
   * @param {Object} data 凭证数据
   * @returns {Promise<Object>} 创建的凭证
   */
  createCredential: async (data) => {
    try {
      const response = await httpClient.post('credentials/', data);
      return response.data;
    } catch (error) {
      handleApiError(error, '创建凭证失败');
      throw error;
    }
  },
  
  /**
   * 更新凭证
   * @param {string|number} id 凭证ID
   * @param {Object} data 更新数据
   * @returns {Promise<Object>} 更新后的凭证
   */
  updateCredential: async (id, data) => {
    try {
      const response = await httpClient.put(`credentials/${id}/`, data);
      return response.data;
    } catch (error) {
      handleApiError(error, '更新凭证失败');
      throw error;
    }
  },
  
  /**
   * 删除凭证
   * @param {string|number} id 凭证ID
   * @returns {Promise<Object>} 响应结果
   */
  deleteCredential: async (id) => {
    try {
      const response = await httpClient.delete(`credentials/${id}/`);
      return response.data;
    } catch (error) {
      handleApiError(error, '删除凭证失败');
      throw error;
    }
  },
  
  /**
   * 获取支持的凭证类型
   * @returns {Promise<Array>} 凭证类型列表
   */
  getCredentialTypes: async () => {
    try {
      const response = await httpClient.get('credentials/types/');
      return response.data;
    } catch (error) {
      handleApiError(error, '获取凭证类型失败');
      return [];
    }
  }
};

export default CredentialService;