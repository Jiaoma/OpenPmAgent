import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Form, Input, Button, Card, Tabs, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useAuthStore } from '@/stores/authStore';

const Login = () => {
  const [activeTab, setActiveTab] = useState('admin');
  const [empId, setEmpId] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, clearError } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleSubmit = async () => {
    setLoading(true);
    clearError();

    try {
      await login(empId, activeTab === 'admin' ? password : undefined);
      message.success('登录成功');
      
      const from = location.state?.from?.pathname || '/';
      navigate(from, { replace: true });
    } catch (error: any) {
      // Error is already handled in the store
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    }}>
      <Card
        title="OpenPmAgent"
        style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}
      >
        <Tabs
          activeKey={activeTab}
          onChange={(key) => {
            setActiveTab(key);
            setPassword('');
          }}
          centered
        >
          <Tabs.TabPane tab="管理员登录" key="admin">
            <Form
              name="admin-login"
              onFinish={handleSubmit}
              autoComplete="off"
              layout="vertical"
            >
              <Form.Item
                name="emp_id"
                rules={[{ required: true, message: '请输入工号' }]}
              >
                <Input
                  prefix={<UserOutlined />}
                  placeholder="工号"
                  size="large"
                  value={empId}
                  onChange={(e) => setEmpId(e.target.value)}
                />
              </Form.Item>
              
              <Form.Item
                name="password"
                rules={[{ required: true, message: '请输入密码' }]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="密码"
                  size="large"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  size="large"
                  loading={loading}
                  block
                >
                  登录
                </Button>
              </Form.Item>
            </Form>
          </Tabs.TabPane>

          <Tabs.TabPane tab="普通用户登录" key="user">
            <Form
              name="user-login"
              onFinish={handleSubmit}
              autoComplete="off"
              layout="vertical"
            >
              <Form.Item
                name="emp_id"
                rules={[{ required: true, message: '请输入工号' }]}
              >
                <Input
                  prefix={<UserOutlined />}
                  placeholder="工号"
                  size="large"
                  value={empId}
                  onChange={(e) => setEmpId(e.target.value)}
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  size="large"
                  loading={loading}
                  block
                >
                  登录
                </Button>
              </Form.Item>
            </Form>
          </Tabs.TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default Login;
