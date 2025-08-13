// frontend/src/components/Header.js
import { MenuFoldOutlined, MenuUnfoldOutlined, BulbOutlined, BulbFilled } from '@ant-design/icons';
import { Button, Space } from 'antd';

function Header({ toggleSidebar, toggleTheme, darkMode, collapsed }) {
  return (
    <header className="app-header">
      <Button 
        type="text" 
        icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
        onClick={toggleSidebar}
        className="sidebar-toggle"
      />
      
      <div className="header-right">
        <Space>
          <Button 
            type="text" 
            icon={darkMode ? <BulbFilled /> : <BulbOutlined />}
            onClick={toggleTheme}
            className="theme-toggle"
          />
        </Space>
      </div>
    </header>
  );
}

export default Header;