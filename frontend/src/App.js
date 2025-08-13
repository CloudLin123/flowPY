// 主应用组件

// frontend/src/App.js
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Chatflows from './components/Chatflows';
import AgentFlows from './components/AgentFlows';
import Executions from './components/Executions';
import Assistants from './components/Assistants';
import Credentials from './components/Credentials';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Chatflows />} />
          <Route path="agentflows" element={<AgentFlows />} />
          <Route path="executions" element={<Executions />} />
          <Route path="assistants" element={<Assistants />} />
          <Route path="credentials" element={<Credentials />} />
          {/* 暂时注释不存在的组件，避免报错 */}
          {/* 
          <Route path="marketplace" element={<div>开发中...</div>} />
          <Route path="tools" element={<div>开发中...</div>} />
          <Route path="variables" element={<div>开发中...</div>} />
          <Route path="apikeys" element={<div>开发中...</div>} />
          <Route path="documentstores" element={<div>开发中...</div>} />
          */}
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
