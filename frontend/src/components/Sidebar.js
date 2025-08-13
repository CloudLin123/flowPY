// 侧边组件

import { NavLink } from "react-router-dom";
import {
    MessageOutlined, RobotOutlined, HistoryOutlined,
    UserOutlined, ShopOutlined, ToolOutlined,
    KeyOutlined, CodeOutlined, ApiOutlined, FileOutlined
} from '@ant-design/icons';

function Sidebar({ collapsed}) {
    const menuItems = [
        {path: '/', icon: <MessageOutlined />, label: 'Chatflows'},
        {path: '/agnetflows', icon: <RobotOutlined />, label: 'Agentflows'},
        {path: '/executions', icon: <HistoryOutlined />, label: 'Executions'},
        {path: '/assistants', icon: <UserOutlined />, label: 'Assistants'},
        {path: '/marketplace', icon: <ShopOutlined />, label: 'Marketplaces'},
        {path: '/tools', icon: <ToolOutlined />, label: 'Tools'},
        {path: '/credentials', icon: <KeyOutlined />, label: 'Credentials'},
        {path: '/variables', icon: <CodeOutlined />, label: 'Variables'},
        {path: '/apikeys', icon: <ApiOutlined />, label: 'API Keys'},
        {path: '/documentstores', icon: <FileOutlined />, label: 'Document Stores'},
    ];

    return (
        <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
            <div className='logo-container'>
                <img sec='logo.svg' alt="FlowisePy" />
                {!collapsed && <span className='logo-text'>FlowisePy</span>}
            </div>
            <nav className="menu">
                {menuItems.map(item => (
                    <NavLink key={item.path} to={item.path} className='menu-item'>
                        <span className="menu-icon">{item.icon}</span>
                        {!collapsed && <span className="menu-label">{item.label}</span>}
                    </NavLink>
                ))}
            </nav>
        </div>
    );
}

export default Sidebar;