   // frontend/src/components/Credentials.js
   import { useState, useEffect } from 'react';
   import { Table, Button, Space, Modal, Form, Input, Typography } from 'antd';
   import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
   import CredentialService from '../service/credentialService';
   
   function Credentials() {
     const [credentials, setCredentials] = useState([]);
     const [loading, setLoading] = useState(false);
     
     useEffect(() => {
       fetchCredentials();
     }, []);
     
     const fetchCredentials = async () => {
       setLoading(true);
       try {
         const data = await CredentialService.getAllCredentials();
         setCredentials(data);
       } finally {
         setLoading(false);
       }
     };
     
     const columns = [
       {
         title: '名称',
         dataIndex: 'name',
         key: 'name',
       },
       {
         title: '类型',
         dataIndex: 'type',
         key: 'type',
       },
       {
         title: '操作',
         key: 'action',
         render: (_, record) => (
           <Space size="middle">
             <Button icon={<EditOutlined />} size="small">编辑</Button>
             <Button icon={<DeleteOutlined />} danger size="small">删除</Button>
           </Space>
         ),
       },
     ];
     
     return (
       <div className="credentials-page">
         <div className="page-header">
           <Typography.Title level={2}>凭证管理</Typography.Title>
           <Typography.Paragraph>
             管理连接到外部服务的API密钥和认证信息
           </Typography.Paragraph>
         </div>
         
         <div className="action-bar">
           <Button type="primary" icon={<PlusOutlined />}>
             添加凭证
           </Button>
         </div>
         
         <Table 
           columns={columns} 
           dataSource={credentials} 
           rowKey="id"
           loading={loading}
         />
       </div>
     );
   }
   
   export default Credentials;