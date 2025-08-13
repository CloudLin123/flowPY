// frontend/src/components/Assistants.js
import { useState, useEffect } from 'react';
import { Input, Button, Card, Row, Col, Typography, Space, Avatar } from 'antd';
import { PlusOutlined, AppstoreOutlined, UnorderedListOutlined, SearchOutlined, RobotOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

function Assistants() {
  const [assistants, setAssistants] = useState([]);
  const [viewMode, setViewMode] = useState('grid');
  const [searchText, setSearchText] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // 加载助手数据
    fetchAssistants();
  }, []);

  const fetchAssistants = async () => {
    setLoading(true);
    // 这里将来可以调用API获取数据
    setTimeout(() => {
      setAssistants([]);
      setLoading(false);
    }, 500);
  };

  // 过滤助手
  const filteredAssistants = assistants.filter(assistant =>
    assistant?.name?.toLowerCase().includes(searchText.toLowerCase())
  );

  return (
    <div className="assistants-page">
      <div className="page-header">
        <Typography.Title level={2}>AI 助手</Typography.Title>
        <Typography.Paragraph>
          创建和管理您的AI助手
        </Typography.Paragraph>
      </div>

      <div className="action-bar">
        <Input
          placeholder="搜索助手名称"
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
            onClick={() => navigate('/assistants/new')}
          >
            创建助手
          </Button>
        </Space>
      </div>

      {loading ? (
        <div className="loading-container">
          <Typography.Text>加载中...</Typography.Text>
        </div>
      ) : filteredAssistants.length > 0 ? (
        <div className="assistants-container">
          {viewMode === 'grid' ? (
            <Row gutter={[16, 16]}>
              {filteredAssistants.map(assistant => (
                <Col key={assistant.id} xs={24} sm={12} md={8} lg={6}>
                  <Card
                    hoverable
                    onClick={() => navigate(`/assistants/${assistant.id}`)}
                    className="assistant-card"
                  >
                    <div className="assistant-card-header">
                      <Avatar icon={<RobotOutlined />} size={48} />
                      <Typography.Title level={4}>{assistant.name}</Typography.Title>
                    </div>
                    <Typography.Paragraph ellipsis={{ rows: 2 }}>
                      {assistant.description || '无描述'}
                    </Typography.Paragraph>
                  </Card>
                </Col>
              ))}
            </Row>
          ) : (
            <div className="list-view">
              {filteredAssistants.map(assistant => (
                <div
                  key={assistant.id}
                  className="assistant-list-item"
                  onClick={() => navigate(`/assistants/${assistant.id}`)}
                >
                  <div className="assistant-list-item-content">
                    <Avatar icon={<RobotOutlined />} size={32} />
                    <div className="assistant-list-item-info">
                      <Typography.Text strong>{assistant.name}</Typography.Text>
                      <Typography.Text type="secondary" ellipsis>
                        {assistant.description || '无描述'}
                      </Typography.Text>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="empty-container">
          <Typography.Text>暂无AI助手</Typography.Text>
        </div>
      )}
    </div>
  );
}

export default Assistants;
