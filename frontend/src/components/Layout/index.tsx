import { Layout as AntLayout, Menu } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  HomeOutlined,
  TeamOutlined,
  ProjectOutlined,
  UserOutlined,
  LogoutOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '@/stores/authStore';

import { useState } from 'react';
const { Header, Content, Sider } = AntLayout;

const MainLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const [collapsed, setCollapsed] = useState(false);

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '仪表盘',
    },
    {
      key: '/team',
      icon: <TeamOutlined />,
      label: '团队管理',
      children: [
        { key: '/team/persons', label: '人员列表' },
        { key: '/team/groups', label: '小组管理' },
        { key: '/team/workload', label: '负载分析' },
        { key: '/team/capability', label: '能力模型' },
      ],
    },
    {
      key: '/architecture',
      icon: <ProjectOutlined />,
      label: '技术架构',
      children: [
        { key: '/architecture/modules', label: '模块管理' },
        { key: '/architecture/functions', label: '功能管理' },
        { key: '/architecture/responsibilities', label: '责任田' },
      ],
    },
    {
      key: '/project',
      icon: <ProjectOutlined />,
      label: '项目管理',
      children: [
        { key: '/project/versions', label: '版本管理' },
        { key: '/project/iterations', label: '迭代管理' },
        { key: '/project/tasks', label: '任务管理' },
        { key: '/project/gantt', label: '甘特图' },
        { key: '/project/graph', label: '任务图' },
      ],
    },
    {
      key: '/backup',
      icon: <FileTextOutlined />,
      label: '备份恢复',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    if (key.startsWith('/team') || key.startsWith('/architecture') || key.startsWith('/project')) {
      navigate(key);
    } else {
      navigate(key);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getSelectedKey = () => {
    const path = location.pathname;
    if (path.startsWith('/team/persons')) return '/team';
    if (path.startsWith('/team/groups')) return '/team';
    if (path.startsWith('/team/workload')) return '/team';
    if (path.startsWith('/team/capability')) return '/team';
    if (path.startsWith('/architecture')) return '/architecture';
    if (path.startsWith('/project')) return '/project';
    return path;
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
        <div style={{ height: 32, margin: 16, textAlign: 'center' }}>
          <span style={{ color: 'white', fontWeight: 'bold' }}>
            {collapsed ? 'PM' : 'OpenPM'}
          </span>
        </div>
        <Menu
          theme="dark"
          selectedKeys={[getSelectedKey()]}
          mode="inline"
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <AntLayout>
        <Header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 24px', background: '#fff' }}>
          <div style={{ fontSize: 16, fontWeight: 500 }}>
            项目和团队管理平台
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <span>
              {user?.emp_id} {user?.is_admin && '(管理员)'}
            </span>
            <LogoutOutlined
              style={{ cursor: 'pointer', fontSize: 18 }}
              onClick={handleLogout}
              title="退出登录"
            />
          </div>
        </Header>
        <Content style={{ margin: '24px 16px', padding: 24, minHeight: 280, background: '#fff' }}>
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default MainLayout;
