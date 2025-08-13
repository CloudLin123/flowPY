// frontend/src/components/Executions.js
import { useState, useEffect } from 'react';
import { Table, Typography, Input, Space, Button, Tag } from 'antd';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

function Executions() {
  const [executions, setExecutions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // 加载执行历史数据
    fetchExecutions();
  }, []);

  const fetchExecutions = async () => {
    setLoading(true);
    // 这里将来可以调用API获取数据
    setTimeout(() => {
      setExecutions([]);
      setLoading(false);
    }, 500);
  };

  const columns = [
    {
      title: '执行ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: '工作流',
      dataIndex: 'workflow_name',
      key: 'workflow_name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: status => {
        let color = status === 'completed' ? 'success' : 
                    status === 'failed' ? 'error' : 'processing';
        return <Tag color={color}>{status}</Tag>;
      }
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
    },
    {
      title: '结束时间',
      dataIndex: 'end_time',
      key: 'end_time',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Button type="link" onClick={() => navigate(`/executions/${record.id}`)}>
          查看详情
        </Button>
      ),
    },
  ];

  return (
    <div className="executions-page">
      <div className="page-header">
        <Typography.Title level={2}>执行历史</Typography.Title>
        <Typography.Paragraph>
          查看所有工作流的执行历史记录
        </Typography.Paragraph>
      </div>

      <div className="action-bar">
        <Input
          placeholder="搜索执行ID或工作流名称"
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
        />
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchExecutions}
            loading={loading}
          >
            刷新
          </Button>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={executions}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />
    </div>
  );
}

export default Executions;
