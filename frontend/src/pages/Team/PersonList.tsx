import { useState, useEffect } from 'react';
import { Button, Table, Modal, Form, Input, Select, message, Popconfirm, Space, Card, Row, Col } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons';
import { personApi, groupApi, type Person, type Group } from '@/api/team';
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table';

const { Option } = Select;

const PersonList = () => {
  const [persons, setPersons] = useState<Person[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [editingPerson, setEditingPerson] = useState<Partial<Person> | null>(null);
  const [form] = Form.useForm();
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });

  // Fetch persons and groups on mount
  useEffect(() => {
    fetchPersons();
    fetchGroups();
  }, [pagination.current, pagination.pageSize, searchText]);

  const fetchPersons = async () => {
    setLoading(true);
    try {
      const data = await personApi.getPersons({
        skip: (pagination.current - 1) * pagination.pageSize,
        limit: pagination.pageSize,
        search: searchText || undefined,
      });
      setPersons(data);
      setPagination(prev => ({ ...prev, total: data.length }));
    } catch (error: any) {
      message.error('获取人员列表失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchGroups = async () => {
    try {
      const data = await groupApi.getGroups({ limit: 100 });
      setGroups(data);
    } catch (error: any) {
      message.error('获取小组列表失败: ' + error.message);
    }
  };

  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handleTableChange = (page: number, pageSize: number) => {
    setPagination({
      current: page,
      pageSize,
      total: pagination.total,
    });
  };


  const handleAdd = () => {
    setEditingPerson(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (person: Person) => {
    setEditingPerson(person);
    form.setFieldsValue(person);
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await personApi.deletePerson(id);
      message.success('删除成功');
      fetchPersons();
    } catch (error: any) {
      message.error('删除失败: ' + error.message);
    }
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingPerson) {
        await personApi.updatePerson(editingPerson.id!, values);
        message.success('更新成功');
      } else {
        await personApi.createPerson(values);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchPersons();
    } catch (error: any) {
      if (error.errorFields) {
        return; // Form validation error
      }
      message.error('操作失败: ' + error.message);
    }
  };

  const columns: ColumnsType<Person> = [
    {
      title: '工号',
      dataIndex: 'emp_id',
      key: 'emp_id',
      width: 100,
    },
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
      width: 120,
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: 180,
    },
    {
      title: '电话',
      dataIndex: 'phone',
      key: 'phone',
      width: 120,
    },
    {
      title: '职位',
      dataIndex: 'position',
      key: 'position',
      width: 120,
    },
    {
      title: '所属小组',
      dataIndex: ['group', 'name'],
      key: 'group_name',
      width: 120,
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button 
            type="link" 
            icon={<EditOutlined />} 
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个人吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card>
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col span={8}>
            <Input
              placeholder="搜索姓名或工号"
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
          </Col>
          <Col span={4}>
            <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
              搜索
            </Button>
          </Col>
          <Col span={12} style={{ textAlign: 'right' }}>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增人员
            </Button>
          </Col>
        </Row>

        <Table
          columns={columns}
          dataSource={persons}
          rowKey="id"
          loading={loading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: handleTableChange,
          }}
          scroll={{ x: 1000 }}
        />
      </Card>

      <Modal
        title={editingPerson ? '编辑人员' : '新增人员'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          name="personForm"
        >
          <Form.Item
            label="工号"
            name="emp_id"
            rules={[{ required: true, message: '请输入工号' }]}
          >
            <Input placeholder="请输入工号" disabled={!!editingPerson} />
          </Form.Item>

          <Form.Item
            label="姓名"
            name="name"
            rules={[{ required: true, message: '请输入姓名' }]}
          >
            <Input placeholder="请输入姓名" />
          </Form.Item>

          <Form.Item label="邮箱" name="email">
            <Input placeholder="请输入邮箱" />
          </Form.Item>

          <Form.Item label="电话" name="phone">
            <Input placeholder="请输入电话" />
          </Form.Item>

          <Form.Item label="职位" name="position">
            <Input placeholder="请输入职位" />
          </Form.Item>

          <Form.Item label="所属小组" name="group_id">
            <Select placeholder="请选择小组" allowClear>
              {groups.map(group => (
                <Option key={group.id} value={group.id}>
                  {group.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default PersonList;
