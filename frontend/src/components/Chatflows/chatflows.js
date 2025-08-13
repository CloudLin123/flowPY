// Chatflows页面实现

// /frontend/src/pages/Chatflows.jsx
// 这个文件是Chatflows页面的实现，主要功能是显示工作流列表，并提供搜索、添加、编辑、删除等操作
import styles from './chatflows.module.css';
import { useState, useEffect, useMemo } from 'react';
import { Input, Button, Card, Row, Col, Typography, Space } from 'antd';
import { PlusOutlined, AppstoreOutlined, UnorderedListOutlined, SearchOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import WorkflowService from 'frontend/src/service/workflowService.js';

function Chatflows() {
  // workflows: 后端返回的工作流列表
  // viewMode: 视图模式，'grid' 为网格，'list' 为列表
  // searchText: 搜索输入框内容
  // loading: 是否加载中，用于控制加载状态（可扩展为 Skeleton/Spin）
  // error: 错误信息字符串（可扩展为全局消息提示）
  const [workflows, setWorkflows] = useState([]);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [searchText, setSearchText] = useState('');
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    // 拉取全部工作流数据
    const fetchWorkflows = async () => {
      setLoading(true);
      try {
        const data = await WorkflowService.getAllWorkflows();
        setWorkflows(data);
        setError(null);
      } catch (err) {
        // 这里仅给出简单的错误信息，可接入 antd message/notification 增强体验
        setError('加载工作流失败，请确保后端服务已启动');
      } finally {
        setLoading(false);
      }
    };
    
    fetchWorkflows();
  }, []);
  
  // 使用 useMemo 避免在未变更时重复计算过滤结果
  const filteredWorkflows = useMemo(() => {
    return workflows.filter((workflow) =>
      (workflow?.name || '').toLowerCase().includes(searchText.toLowerCase())
    );
  }, [workflows, searchText]);
  
  // 视图渲染逻辑
  return (
    <div className={styles.chatflowsPage}>
      {/* 页面标题区域 */}
      <div className={styles.pageHeader}>
        <Typography.Title level={2}>Chatflows</Typography.Title>
        <Typography.Paragraph>
          Build single-agent systems, chatbots and simple LLM flows
        </Typography.Paragraph>
      </div>
      
      {/* 工具栏：搜索 + 视图切换 + 新建按钮 */}
      <div className={styles.actionBar}>
        <Input 
          placeholder="Search Name or Category ( Ctrl + F )"
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
        />
        <Space>
          <Button 
            icon={<AppstoreOutlined />} 
            type={viewMode === 'grid' ? 'primary' : 'default'}
            onClick={() => setViewMode('grid')}
            title="切换为网格视图"
          />
          <Button 
            icon={<UnorderedListOutlined />}
            type={viewMode === 'list' ? 'primary' : 'default'}
            onClick={() => setViewMode('list')}
            title="切换为列表视图"
          />
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => navigate('/chatflows/new')}
          >
            Add New
          </Button>
        </Space>
      </div>
      
      {/* 主体容器：根据视图模式渲染网格或列表 */}
      <div className={styles.workflowsContainer}>
        {viewMode === 'grid' ? (
          <Row gutter={[16, 16]}>
            {filteredWorkflows.map((workflow) => (
              <Col key={workflow.id} xs={24} sm={12} md={8} lg={6}>
                <Card 
                  hoverable
                  onClick={() => navigate(`/chatflows/edit/${workflow.id}`)}
                  className={styles.workflowCard}
                >
                  <Typography.Title level={4}>
                    {workflow.name}
                  </Typography.Title>
                  <div className={styles.cardIcons}>
                    {/* 这里可以根据工作流类型显示相应图标，例如根据 workflow.type 渲染 */}
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        ) : (
          <div className={styles.listView}>
            {filteredWorkflows.map((workflow) => (
              <div 
                key={workflow.id} 
                className={styles.workflowListItem}
                onClick={() => navigate(`/chatflows/edit/${workflow.id}`)}
              >
                <Typography.Text strong>{workflow.name}</Typography.Text>
                <div className={styles.listItemIcons}>
                  {/* 显示工作流类型图标 */}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* 错误或加载状态占位：此处简单展示，可替换为 antd 的 Alert/Spin 组件 */}
      {error && (
        <Typography.Text type="danger">{error}</Typography.Text>
      )}
      {loading && (
        <Typography.Text type="secondary">正在加载工作流…</Typography.Text>
      )}
    </div>
  );
}

export default Chatflows;

