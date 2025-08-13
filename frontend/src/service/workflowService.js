// frontend/src/service/workflowService.js
import httpClient from './axios';
import { handleApiError } from './errorHandler';

const WorkflowService = {
  getAllWorkflows: async () => {
    try {
      console.log('正在请求工作流列表...');
      const response = await httpClient.get('workflows/');
      console.log('请求成功:', response);
      return response.data;
    } catch (error) {
      console.error('获取工作流列表错误详情:', error.response || error);
      handleApiError(error, '获取工作流列表失败');
      return [];
    }
  },
  
  getWorkflow: async (id) => {
    try {
      const response = await httpClient.get(`workflows/${id}/`);
      return response.data;
    } catch (error) {
      handleApiError(error, '获取工作流详情失败');
      return null;
    }
  },
  
  createWorkflow: async (data) => {
    try {
      const response = await httpClient.post('workflows/', data);
      return response.data;
    } catch (error) {
      handleApiError(error, '创建工作流失败');
      throw error; // 重新抛出错误以便调用者知道操作失败
    }
  },
  
  updateWorkflow: async (id, data) => {
    try {
      const response = await httpClient.put(`workflows/${id}/`, data);
      return response.data;
    } catch (error) {
      handleApiError(error, '更新工作流失败');
      throw error;
    }
  },
  
  deleteWorkflow: async (id) => {
    try {
      const response = await httpClient.delete(`workflows/${id}/`);
      return response.data;
    } catch (error) {
      handleApiError(error, '删除工作流失败');
      throw error;
    }
  },
  
  executeWorkflow: async (id, inputs) => {
    try {
      const response = await httpClient.post(`workflows/${id}/execute/`, { inputs });
      return response.data;
    } catch (error) {
      handleApiError(error, '执行工作流失败');
      throw error;
    }
  }
};

export default WorkflowService;