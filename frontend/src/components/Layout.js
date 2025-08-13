// 布局组件

import { useState} from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header.js';

function Layout() {
    const [collapsed, setCollapsed] = useState(false);
    const [darkmode, setDarkmode] = useState(false);

    return (
        <div className={`app-container ${darkmode ? 'dark' : 'light'}`}>
            <Sidebar collapsed={collapsed}></Sidebar>
            <div className="main-content">
                <Header 
                    toggleSidebar = {() => setCollapsed(!collapsed)}
                    toggleTheme = {() => setDarkmode(!darkmode)}
                    darkMode={darkmode}
                    collapsed={collapsed}
                />
                <div className='page-content'>
                    <Outlet />
                </div>
            </div>
        </div>
    );
}

export default Layout;