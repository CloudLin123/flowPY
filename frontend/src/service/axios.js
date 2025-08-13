// frontend/src/service/axios.js - 基础HTTP客户端配置

import axios from 'axios';
import { handleApiError } from './errorHandler';

const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/';

const httpClient = axios.create({
  baseURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
httpClient.interceptors.request.use(
  config => {
    // 如果有token，可以在这里添加到header
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
httpClient.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    // 全局错误处理，但不在这里显示消息，让各个服务决定如何处理
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

export default httpClient;