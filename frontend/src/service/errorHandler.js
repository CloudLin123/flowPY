// frontend/src/service/errorHandler.js
import { message } from 'antd';

// 常见HTTP错误状态码对应的友好提示
const HTTP_STATUS_MESSAGES = {
  400: '请求参数错误，请检查输入',
  401: '未授权访问，请先登录',
  403: '您没有权限执行此操作',
  404: '请求的资源不存在',
  500: '服务器错误，请稍后再试',
  502: '网关错误，请检查网络连接',
  503: '服务暂时不可用，请稍后再试',
};

// 通用错误处理函数
export const handleApiError = (error, customMessage = null) => {
  console.error('API错误:', error);
  
  // 获取状态码和错误信息
  const status = error.response?.status;
  const serverMessage = error.response?.data?.error || error.response?.data?.message;
  
  // 确定显示的错误消息
  const displayMessage = customMessage || 
                         serverMessage || 
                         HTTP_STATUS_MESSAGES[status] || 
                         '请求失败，请稍后再试';
  
  // 使用Ant Design的消息组件显示错误
  message.error(displayMessage);
  
  // 对特定错误进行处理
  if (status === 401) {
    // 可以在这里处理未授权，例如重定向到登录页面
    // window.location.href = '/login';
  }
  
  // 返回处理后的错误，便于调用者进行后续处理
  return {
    isError: true,
    status,
    message: displayMessage,
    originalError: error
  };
};