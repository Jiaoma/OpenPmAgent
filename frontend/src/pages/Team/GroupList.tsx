import { useState, useEffect } from 'react';
import { Button, Table, Modal, Form, Input, message, Popconfirm, Space, Card, Row, Col, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { groupApi, type Group, type Person } from '@/api/team';
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table';

const GroupList = () => {
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingGroup, setEditingGroup] = useState<Partial<Group> | null>(null);
  const [form] = Form.useForm();
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });

  // Fetch groups on mount
  useEffect(() => {
    fetchGroups();
  }, [pagination.current, pagination.pageSize]);

  const fetchGroups = async () => {
    setLoading(true);
    try {
      const data = await groupApi.getGroups({
        skip: (pagination.current - 1) * pagination.pageSize,
        limit: pagination.pageSize,
      });
      setGroups(data);
      setPagination(prev => ({ ...prev, total: data.length }));
    } catch (error: any) {
      message.error('获取小组列表失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingGroup(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (group: Group) => {
    setEditingGroup(group);
    form.setFieldsValue(group);
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await groupApi.deleteGroup(id);
      message.success('删除成功');
      fetchGroups();
    } catch (error: any) {
      message.error('删除失败: ' + error.message);
    }
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingGroup) {
        await groupApi.updateGroup(editingGroup.id!, values);
        message.success('更新成功');
      } else {
        await groupApi.createGroup(values);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchGroups();
    } catch (error: any) {
      if (error.errorFields) {
        return;
      }
      message.error('操作失败: ' + error.message);
    }
  };

  const handleTableChange = (page: number, pageSize: number) => {
    setPagination({
      current: page,
      pageSize,
      total: pagination.total,
    });
  };


  const columns: ColumnsType<Group> = [
    {
      title: '小组名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: '组长',
      dataIndex: ['leader', 'name'],
      key: 'leader_name',
      width: 120,
    },
    {
      title: '成员数',
      dataIndex: 'member_count',
      key: 'member_count',
      width: 100,
      render: (_, record) => record.members?.length || 0,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
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
            title="确定要删除这个小组吗？"
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
      <Card
        title="小组管理"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新增小组
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={groups}
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
          expandable={{
            expandedRowRender: (record: Group) => (
              <div style={{ padding: '16px' }}>
                <p><strong>成员列表:</strong></p>
                <Row gutter={[16, 16]}>
                  {record.members?.map((member: Person) => (
                    <Col key={member.id} span={8}>
                      <Tag color="blue">{member.name} ({member.emp_id})</Tag>
                    </Col>
                  )) || <Tag>暂无成员</Tag>}
                </Row>
              </div>
            ),
          }}
        />
      </Card>

      <Modal
        title={editingGroup ? '编辑小组' : '新增小组'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          name="groupForm"
        >
          <Form.Item
            label="小组名称"
            name="name"
            rules={[{ required: true, message: '请输入小组名称' }]}
          >
            <Input placeholder="请输入小组名称" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default GroupList;

