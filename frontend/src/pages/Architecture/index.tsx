import { Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Card, Button, Table, Space, Select, Modal, Form, message, Popconfirm, Transfer } from 'antd';
import { PlusOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import ModuleEditor from './ModuleEditor';
import FunctionEditor from './FunctionEditor';
import { relationApi, functionApi, type Responsibility, type Function } from '@/api/architecture';

const ResponsibilityEditor = () => {
  const [relations, setRelations] = useState<any[]>([]);
  const [functions, setFunctions] = useState<Function[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedFunctionId, setSelectedFunctionId] = useState<number | null>(null);
  const [selectedResponsibilityId, setSelectedResponsibilityId] = useState<number | null>(null);
  const [responsibilities, setResponsibilities] = useState<Responsibility[]>([]);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchRelations();
    fetchFunctions();
    fetchResponsibilities();
  }, []);

  const fetchRelations = async () => {
    setLoading(true);
    try {
      const data = await relationApi.getResponsibilityFunctionRelations();
      setRelations(data);
    } catch (error: any) {
      message.error('获取关联关系失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchFunctions = async () => {
    try {
      const data = await functionApi.getFunctions();
      setFunctions(data);
    } catch (error: any) {
      message.error('获取功能列表失败: ' + error.message);
    }
  };

  const fetchResponsibilities = async () => {
    try {
      const data = await functionApi.getFunctions();
      const uniqueResponsibilities = Array.from(
        new Set(data.map(f => f.responsibility_id).filter(Boolean))
      ).map(id => {
        const func = data.find(f => f.responsibility_id === id);
        return { id, name: func?.responsibility?.name || `责任田 ${id}` };
      });
      setResponsibilities(uniqueResponsibilities);
    } catch (error: any) {
      message.error('获取责任田列表失败: ' + error.message);
    }
  };

  const handleAdd = () => {
    setSelectedFunctionId(null);
    setSelectedResponsibilityId(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await relationApi.deleteResponsibilityFunctionRelation(id);
      message.success('删除成功');
      fetchRelations();
    } catch (error: any) {
      message.error('删除失败: ' + error.message);
    }
  };

  const handleModalOk = async () => {
    try {
      if (!selectedFunctionId || !selectedResponsibilityId) {
        message.error('请选择功能与责任田');
        return;
      }
      await relationApi.createResponsibilityFunctionRelation({
        function_id: selectedFunctionId,
        responsibility_id: selectedResponsibilityId,
      });
      message.success('创建成功');
      setModalVisible(false);
      fetchRelations();
    } catch (error: any) {
      message.error('操作失败: ' + error.message);
    }
  };

  const columns = [
    {
      title: '责任田名称',
      dataIndex: 'responsibility_name',
      key: 'responsibility_name',
      width: 200,
    },
    {
      title: '功能名称',
      dataIndex: 'function_name',
      key: 'function_name',
      width: 200,
    },
    {
      title: '功能ID',
      dataIndex: 'function_id',
      key: 'function_id',
      width: 100,
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      fixed: 'right' as const,
      render: (_, record) => (
        <Popconfirm
          title="确定要删除这个关联吗？"
          onConfirm={() => handleDelete(record.id)}
          okText="确定"
          cancelText="取消"
        >
          <Button type="link" danger icon={<DeleteOutlined />}>
            删除
          </Button>
        </Popconfirm>
      ),
    },
  ];

  return (
    <Card
      title="责任田-功能关联"
      extra={
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchRelations} loading={loading}>
            刷新
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新增关联
          </Button>
        </Space>
      }
    >
      <Table
        columns={columns}
        dataSource={relations}
        rowKey="id"
        loading={loading}
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
        }}
      />

      <Modal
        title="新增责任田-功能关联"
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        okText="确定"
        cancelText="取消"
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="选择功能" required>
            <Select
              placeholder="请选择功能"
              value={selectedFunctionId || undefined}
              onChange={setSelectedFunctionId}
            >
              {functions.map(f => (
                <Select.Option key={f.id} value={f.id}>
                  {f.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item label="选择责任田" required>
            <Select
              placeholder="请选择责任田"
              value={selectedResponsibilityId || undefined}
              onChange={setSelectedResponsibilityId}
            >
              {responsibilities.map(r => (
                <Select.Option key={r.id} value={r.id}>
                  {r.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

const ArchitecturePages = () => {
  return (
    <Routes>
      <Route path="/" element={<ModuleEditor />} />
      <Route path="/modules" element={<ModuleEditor />} />
      <Route path="/functions" element={<FunctionEditor />} />
      <Route path="/responsibilities" element={<ResponsibilityEditor />} />
    </Routes>
  );
};

export default ArchitecturePages;
