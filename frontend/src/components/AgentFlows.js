// frontend/src/components/AgentFlows.js
import { useState, useEffect } from 'react';
import { Input, Button, Card, Row, Col, Typography, Space } from 'antd';
import { PlusOutlined, AppstoreOutlined, UnorderedListOutlined, SearchOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

function AgentFlows() {
  const [agentflows, setAgentflows] = useState([]);
  const [viewMode, setViewMode] = useState('grid');
  const [searchText, setSearchText] = useState('');
  const navigate = useNavigate();
  
  useEffect(() => {
    // 这里将来可以调用API获取数据
    setAgentflows([]);
  }, []);
  
  return (
    <div className="agentflows-page">
      <div className="page-header">
        <Typography.Title level={2}>Agent Flows</Typography.Title>
        <Typography.Paragraph>
          Build multi-agent systems and complex agent workflows
        </Typography.Paragraph>
      </div>
      
      <div className="action-bar">
        <Input 
          placeholder="搜索名称或类别 ( Ctrl + F )"
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
        />
        <Space>
          <Button 
            icon={<AppstoreOutlined />} 
            type={viewMode === 'grid' ? 'primary' : 'default'}
            onClick={() => setViewMode('grid')}
          />
          <Button 
            icon={<UnorderedListOutlined />}
            type={viewMode === 'list' ? 'primary' : 'default'}
            onClick={() => setViewMode('list')}
          />
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => navigate('/agentflows/new')}
          >
            添加
          </Button>
        </Space>
      </div>
      
      <div className="workflows-container">
        <Typography.Text>暂无Agent Flow</Typography.Text>
      </div>
    </div>
  );
}

export default AgentFlows;