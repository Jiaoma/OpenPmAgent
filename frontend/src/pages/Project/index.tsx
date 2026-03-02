import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Card, Button, Space, Table, Modal, Form, Input, message, Popconfirm, Statistic, Row, Col, Select, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, ProjectOutlined, TeamOutlined, FileTextOutlined, ScheduleOutlined, BarChartOutlined } from '@ant-design/icons';
import { versionApi, iterationApi, taskApi, achievementApi, type Version, type Iteration, type Task } from '@/api/project';
import { achievementExportApi } from '@/api/team';
import GanttChart from './GanttChart';
import TaskGraph from './TaskGraph';
import ReactECharts from 'echarts-for-react';

const { Option } = Select;

const VersionList = () => {
  const [versions, setVersions] = useState<Version[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingVersion, setEditingVersion] = useState<Partial<Version> | null>(null);
  const [form] = Form.useForm();
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [viewType, setViewType] = useState<'list' | 'detail'>('list');

  useEffect(() => {
    fetchVersions();
  }, [pagination.current, pagination.pageSize]);

  const fetchVersions = async () => {
    setLoading(true);
    try {
      const data = await versionApi.getVersions();
      setVersions(data);
      setPagination(prev => ({ ...prev, total: data.length }));
    } catch (error: any) {
      message.error('获取版本列表失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingVersion(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (version: Version) => {
    setEditingVersion(version);
    form.setFieldsValue(version);
    setModalVisible(true);
    setViewType('detail');
  };

  const handleDelete = async (id: number) => {
    try {
      await versionApi.deleteVersion(id);
      message.success('删除成功');
      fetchVersions();
    } catch (error: any) {
      message.error('删除失败: ' + error.message);
    }
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingVersion) {
        await versionApi.updateVersion(editingVersion.id!, values);
        message.success('更新成功');
      } else {
        await versionApi.createVersion(values);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchVersions();
    } catch (error: any) {
      if (error.errorFields) {
        return;
      }
      message.error('操作失败: ' + error.message);
    }
  };

  const listColumns = [
    {
      title: '版本名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: '项目经理',
      dataIndex: 'pm_name',
      key: 'pm_name',
      width: 120,
    },
    {
      title: '软件经理',
      dataIndex: 'sm_name',
      key: 'sm_name',
      width: 120,
    },
    {
      title: '测试经理',
      dataIndex: 'tm_name',
      key: 'tm_name',
      width: 120,
    },
    {
      title: '迭代数',
      dataIndex: 'iterations',
      key: 'iteration_count',
      width: 100,
      render: (iterations: any[]) => iterations?.length || 0,
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
            title="确定要删除这个版本吗？"
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

  const detailColumns = [
    {
      title: '迭代名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: '开始日期',
      dataIndex: 'start_date',
      key: 'start_date',
      width: 150,
    },
    {
      title: '结束日期',
      dataIndex: 'end_date',
      key: 'end_date',
      width: 150,
    },
    {
      title: '预估工作量',
      dataIndex: 'estimated_man_months',
      key: 'estimated_man_months',
      width: 150,
      render: (val: number) => val.toFixed(2),
    },
  ];

  return (
    <div>
      <Card
        title="版本管理"
        extra={
          <Space>
            <Input.Search
              placeholder="搜索版本名称"
              allowClear
              style={{ width: 200 }}
              onSearch={(value) => {
                // Implement search
              }}
            />
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增版本
            </Button>
          </Space>
        }
      >
        {viewType === 'list' ? (
          <Table
            columns={listColumns}
            dataSource={versions}
            rowKey="id"
            loading={loading}
            pagination={{
              current: pagination.current,
              pageSize: pagination.pageSize,
              total: pagination.total,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 条`,
              onChange: (page, pageSize) => {
                setPagination({ current: page, pageSize, pageSize, total: pagination.total });
              },
            }}
            expandable={{
              expandedRowRender: (record: Version) => (
                <div style={{ padding: '16px' }}>
                  <h3>迭代列表</h3>
                  {record.iterations && record.iterations.length > 0 ? (
                    <Table
                      columns={detailColumns}
                      dataSource={record.iterations}
                      rowKey="id"
                      pagination={false}
                      size="small"
                    />
                  ) : (
                    <p style={{ color: '#999' }}>暂无迭代</p>
                  )}
                </div>
              ),
            }}
          />
        ) : (
          <div style={{ padding: '16px' }}>
            <Button
              icon={<ProjectOutlined />}
              onClick={() => setViewType('list')}
              style={{ marginBottom: 16 }}
            >
              返回列表
            </Button>
            <h2>{editingVersion?.name} - 版本详情</h2>
            <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
              <Col span={8}>
                <Card title="版本信息">
                  <Statistic title="版本名称" value={editingVersion?.name} />
                  <Statistic title="项目经理" value={editingVersion?.pm_name} />
                  <Statistic title="软件经理" value={editingVersion?.sm_name} />
                  <Statistic title="测试经理" value={editingVersion?.tm_name} />
                </Card>
              </Col>
              <Col span={16}>
                <Card title="迭代列表" extra={
                  <Button type="primary" icon={<ScheduleOutlined />}>
                    新增迭代
                  </Button>
                }>
                  {editingVersion?.iterations && editingVersion.iterations.length > 0 ? (
                    <Table
                      columns={detailColumns}
                      dataSource={editingVersion.iterations}
                      rowKey="id"
                      pagination={false}
                      size="small"
                    />
                  ) : (
                    <p style={{ color: '#999' }}>暂无迭代</p>
                  )}
                </Card>
              </Col>
            </Row>
          </div>
        )}
      </Card>

      <Modal
        title={editingVersion ? '编辑版本' : '新增版本'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        okText="确定"
        cancelText="取消"
        width={600}
      >
        <Form form={form} layout="vertical" name="versionForm">
          <Form.Item
            label="版本名称"
            name="name"
            rules={[{ required: true, message: '请输入版本名称' }]}
          >
            <Input placeholder="请输入版本名称" />
          </Form.Item>
          <Form.Item
            label="项目经理"
            name="pm_name"
            rules={[{ required: true, message: '请输入项目经理姓名' }]}
          >
            <Input placeholder="请输入项目经理姓名" />
          </Form.Item>
          <Form.Item
            label="软件经理"
            name="sm_name"
            rules={[{ required: true, message: '请输入软件经理姓名' }]}
          >
            <Input placeholder="请输入软件经理姓名" />
          </Form.Item>
          <Form.Item
            label="测试经理"
            name="tm_name"
            rules={[{ required: true, message: '请输入测试经理姓名' }]}
          >
            <Input placeholder="请输入测试经理姓名" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

const IterationList = () => {
  const [iterations, setIterations] = useState<Iteration[]>([]);
  const [versions, setVersions] = useState<Version[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingIteration, setEditingIteration] = useState<Partial<Iteration> | null>(null);
  const [form] = Form.useForm();
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });

  useEffect(() => {
    fetchIterations();
    fetchVersions();
  }, [pagination.current, pagination.pageSize]);

  const fetchIterations = async () => {
    setLoading(true);
    try {
      const data = await iterationApi.getIterations();
      setIterations(data);
      setPagination(prev => ({ ...prev, total: data.length }));
    } catch (error: any) {
      message.error('获取迭代列表失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchVersions = async () => {
    try {
      const data = await versionApi.getVersions();
      setVersions(data);
    } catch (error: any) {
      message.error('获取版本列表失败: ' + error.message);
    }
  };

  const handleAdd = () => {
    setEditingIteration(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (iteration: Iteration) => {
    setEditingIteration(iteration);
    form.setFieldsValue(iteration);
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await iterationApi.deleteIteration(id);
      message.success('删除成功');
      fetchIterations();
    } catch (error: any) {
      message.error('删除失败: ' + error.message);
    }
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingIteration) {
        await iterationApi.updateIteration(editingIteration.id!, values);
        message.success('更新成功');
      } else {
        await iterationApi.createIteration(values);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchIterations();
    } catch (error: any) {
      if (error.errorFields) {
        return;
      }
      message.error('操作失败: ' + error.message);
    }
  };

  const columns = [
    {
      title: '迭代名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: '所属版本',
      dataIndex: 'version_id',
      key: 'version_id',
      width: 150,
      render: (versionId: number) => {
        const version = versions.find(v => v.id === versionId);
        return version?.name || '-';
      },
    },
    {
      title: '开始日期',
      dataIndex: 'start_date',
      key: 'start_date',
      width: 120,
    },
    {
      title: '结束日期',
      dataIndex: 'end_date',
      key: 'end_date',
      width: 120,
    },
    {
      title: '预估工作量',
      dataIndex: 'estimated_man_months',
      key: 'estimated_man_months',
      width: 120,
      render: (val: number) => val?.toFixed(2) || '-',
    },
    {
      title: '任务数',
      dataIndex: 'task_count',
      key: 'task_count',
      width: 80,
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
            title="确定要删除这个迭代吗？"
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
        title="迭代管理"
        extra={
          <Space>
            <Input.Search
              placeholder="搜索迭代名称"
              allowClear
              style={{ width: 200 }}
              onSearch={(value) => {
                // Implement search
              }}
            />
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增迭代
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={iterations}
          rowKey="id"
          loading={loading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => {
              setPagination({ current: page, pageSize, pageSize, total: pagination.total });
            },
          }}
        />
      </Card>

      <Modal
        title={editingIteration ? '编辑迭代' : '新增迭代'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        okText="确定"
        cancelText="取消"
        width={600}
      >
        <Form form={form} layout="vertical" name="iterationForm">
          <Form.Item
            label="迭代名称"
            name="name"
            rules={[{ required: true, message: '请输入迭代名称' }]}
          >
            <Input placeholder="请输入迭代名称" />
          </Form.Item>
          <Form.Item
            label="所属版本"
            name="version_id"
            rules={[{ required: true, message: '请选择所属版本' }]}
          >
            <Select placeholder="请选择所属版本">
              {versions.map(v => (
                <Option key={v.id} value={v.id}>{v.name}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            label="开始日期"
            name="start_date"
            rules={[{ required: true, message: '请输入开始日期' }]}
          >
            <Input type="date" />
          </Form.Item>
          <Form.Item
            label="结束日期"
            name="end_date"
            rules={[{ required: true, message: '请输入结束日期' }]}
          >
            <Input type="date" />
          </Form.Item>
          <Form.Item
            label="预估工作量（人月）"
            name="estimated_man_months"
            rules={[{ required: true, message: '请输入预估工作量' }]}
          >
            <Input type="number" placeholder="请输入预估工作量" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

const TaskList = () => {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [iterations, setIterations] = useState<Iteration[]>([]);
    const [versions, setVersions] = useState<Version[]>([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingTask, setEditingTask] = useState<Partial<Task> | null>(null);
    const [selectedIterationId, setSelectedIterationId] = useState<number | undefined>();
    const [selectedVersionId, setSelectedVersionId] = useState<number | undefined>();
    const [form] = Form.useForm();
    const [viewType, setViewType] = useState<'list' | 'dependencies' | 'relations'>('list');
    const [dependencyModalVisible, setDependencyModalVisible] = useState(false);
    [relationModalVisible, setRelationModalVisible] = useState(false);
    const [form] = Form.useForm();

    useEffect(() => {
      fetchVersions();
    }, []);

    useEffect(() => {
      if (selectedVersionId) {
        fetchIterations(selectedVersionId);
        fetchTasks();
      }
    }, [selectedVersionId, selectedIterationId]);

    const fetchVersions = async () => {
      try {
        const data = await versionApi.getVersions();
        setVersions(data);
      } catch (error: any) {
        message.error('获取版本列表失败: ' + error.message);
      }
    };

    const fetchIterations = async (versionId: number) => {
      try {
        const data = await iterationApi.getIterations(versionId);
        setIterations(data);
      } catch (error: any) {
        message.error('获取迭代列表失败: ' + error.message);
      }
    };

    const fetchTasks = async () => {
      setLoading(true);
      try {
        const params: any = {};
        if (selectedVersionId) params.version_id = selectedVersionId;
        if (selectedIterationId) params.iteration_id = selectedIterationId;

        const data = await taskApi.getTasks(params);
        setTasks(data);
      } catch (error: any) {
        message.error('获取任务列表失败: ' + error.message);
      } finally {
        setLoading(false);
      }
    };

    const handleAdd = () => {
      setEditingTask(null);
      form.resetFields();
      setModalVisible(true);
    };

    const handleEdit = (task: Task) => {
      setEditingTask(task);
      form.setFieldsValue(task);
      setModalVisible(true);
    };

    const handleDelete = async (id: number) => {
      try {
        await taskApi.deleteTask(id);
        message.success('删除成功');
        fetchTasks();
      } catch (error: any) {
        message.error('删除失败: ' + error.message);
      }
    };

    const handleModalOk = async () => {
      try {
        const values = await form.validateFields();
        if (editingTask) {
          await taskApi.updateTask(editingTask.id!, values);
          message.success('更新成功');
        } else {
          await taskApi.createTask({
            ...values,
            iteration_id: selectedIterationId!,
          });
          message.success('创建成功');
        }
        setModalVisible(false);
        fetchTasks();
      } catch (error: any) {
        if (error.errorFields) {
          return;
        }
        message.error('操作失败: ' + error.message);
      }
    };

    const listColumns = [
      {
        title: '任务名称',
        dataIndex: 'name',
        key: 'name',
        width: 200,
      },
      {
        title: '开始时间',
        dataIndex: 'start_date',
        key: 'start_date',
        width: 150,
      },
      {
        title: '结束时间',
        dataIndex: 'end_date',
        key: 'end_date',
        width: 150,
      },
      {
        title: '工作量',
        dataIndex: 'man_months',
        key: 'man_months',
        width: 100,
      },
      {
        title: '状态',
        dataIndex: 'status',
        key: 'status',
        width: 100,
        render: (status: string) => {
          const statusMap: {
            pending: '待开始',
            in_progress: '进行中',
            completed: '已完成',
          };
          return <Tag color={status === 'completed' ? 'green' : status === 'in_progress' ? 'blue' : 'default'}>
            {statusMap[status] || status}
          </Tag>;
        },
      },
      {
        title: '开发人员',
        dataIndex: 'developer_name',
        key: 'developer_name',
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
            <Button
              type="link"
              onClick={() => setViewType('dependencies')}
            >
              依赖
            </Button>
            <Button
              type="link"
              onClick={() => setViewType('relations')}
            >
              关联
            </Button>
            <Popconfirm
              title="确定要删除这个任务吗？"
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

    const dependencyColumns = [
      {
        title: '任务名称',
        dataIndex: 'name',
        key: 'name',
        width: 200,
      },
      {
        title: '依赖任务',
        dataIndex: 'depends_on_name',
        key: 'depends_on_name',
        width: 200,
      },
      {
        title: '依赖类型',
        dataIndex: 'type',
        key: 'type',
        width: 120,
        render: (type: string) => {
          const typeMap: {
            finish_to_start: '完成→开始',
            start_to_start: '开始→开始',
            finish_to_finish: '完成→完成',
            start_to_finish: '开始→完成',
          };
          return typeMap[type] || type;
        },
      },
      {
        title: '操作',
        key: 'action',
        width: 100,
        fixed: 'right',
        render: (_, record: any) => (
          <Popconfirm
            title="确定要删除这个依赖吗？"
            onConfirm={async () => {
              try {
                await taskDependencyApi.deleteTaskDependency(editingTask!.id!, record.id);
                message.success('删除成功');
                // Reload task details
              } catch (error: any) {
                message.error('删除失败: ' + error.message);
              }
            }}
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

    const relationColumns = [
      {
        title: '任务名称',
        dataIndex: 'name',
        key: 'name',
        width: 200,
      },
      {
        title: '关联任务',
        dataIndex: 'related_task_name',
        key: 'related_task_name',
        width: 200,
      },
      {
        title: '操作',
        key: 'action',
        width: 100,
        fixed: 'right',
        render: (_, record: any) => (
          <Popconfirm
            title="确定要删除这个关联吗？"
            onConfirm={async () => {
              try {
                await taskRelationApi.deleteTaskRelation(editingTask!.id!, record.id);
                message.success('删除成功');
              } catch (error: any) {
                message.error('删除失败: ' + error.message);
              }
            }}
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
      <div>
        <Card
          title="任务管理"
          extra={
            <Space>
              <Select
                style={{ width: 150 }}
                placeholder="选择版本"
                value={selectedVersionId}
                onChange={(value) => {
                  setSelectedVersionId(value);
                  setSelectedIterationId(undefined);
                  setTasks([]);
                }}
              >
                {versions.map(v => (
                  <Option key={v.id} value={v.id}>{v.name}</Option>
                ))}
              </Select>
              <Select
                style={{ width: 150 }}
                placeholder="选择迭代"
                value={selectedIterationId}
                onChange={value => {
                  setSelectedIterationId(value);
                  setTasks([]);
                }}
                disabled={!selectedVersionId}
              >
                {iterations.map(i => (
                  <Option key={i.id} value={i.id}>{i.name}</Option>
                ))}
              </Select>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
                新增任务
              </Button>
            </Space>
          }
        >
          {viewType === 'list' ? (
            <Table
              columns={listColumns}
              dataSource={tasks}
              rowKey="id"
              loading={loading}
              pagination={{
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${tasks.length} 条`,
              }}
            />
          ) : (
            <div style={{ padding: '16px' }}>
              <Space style={{ marginBottom: 16 }}>
                <Button icon={<FileTextOutlined />} onClick={() => setViewType('list')}>
                  返回列表
                </Button>
                <h3>{editingTask?.name} - 任务详情</h3>
              </Space>
              <Row gutter={[16, 16]}>
                <Col span={24}>
                  <Card title="基本信息">
                    <Descriptions column={2} bordered size="small">
                      <Descriptions.Item label="任务名称">{editingTask?.name}</Descriptions.Item>
                      <Descriptions.Item label="开始时间">{editingTask?.start_date}</Descriptions.Item>
                      <Descriptions.Item label="结束时间">{editingTask?.end_date}</Descriptions.Item>
                      <Descriptions.Item label="工作量">{editingTask?.man_months} 人月</Descriptions.Item>
                      <Descriptions.Item label="状态">
                        <Tag color={editingTask?.status === 'completed' ? 'green' : editingTask?.status === 'in_progress' ? 'blue' : 'default'}>
                          {editingTask?.status}
                        </Tag>
                      </Descriptions.Item>
                    </Descriptions>
                    <Descriptions.Item label="开发人员">{editingTask?.developer_name || '未分配'}</Descriptions.Item>
                    <Descriptions.Item label="交付负责人">{editingTask?.delivery_owner_name || '未分配'}</Descriptions.Item>
                    <Descriptions.Item label="测试人员">{editingTask?.tester_name || '未分配'}</Descriptions.Item>
                  </Card>
                </Col>
              </Row>
              <Row gutter={[16, 16]}>
                <Col span={12}>
                  <Card
                    title="依赖关系"
                    extra={
                      <Button type="primary" icon={<PlusOutlined />}>
                        添加依赖
                      </Button>
                    }
                  >
                    <Table
                      columns={dependencyColumns}
                      dataSource={editingTask?.dependencies || []}
                      rowKey="id"
                      pagination={false}
                      size="small"
                      locale={{ emptyText: '暂无依赖' }}
                    />
                  </Card>
                </Col>
                <Col span={12}>
                  <Card
                    title="关联关系"
                    extra={
                      <Button type="primary" icon={<PlusOutlined />}>
                        添加关联
                      </Button>
                    }
                  >
                    <Table
                      columns={relationColumns}
                      dataSource={editingTask?.relations || []}
                      rowKey="id"
                      pagination={false}
                      size="small"
                      locale={{ emptyText: '暂无关联' }}
                    />
                  </Card>
                </Col>
              </Row>
            </div>
          )}
        </Card>
      </div>
    );
  };

const TaskGraph = () => {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });

  return (
    <Card
      title="任务图分析"
      extra={
        <Space>
          <Button icon={<TeamOutlined />}>刷新</Button>
          <Button>分析最长路径</Button>
          <Button>查看负载最高人员</Button>
        </Space>
      }
    >
      <div style={{ height: 400, overflow: 'auto', padding: '20px' }}>
        <p style={{ color: '#999', textAlign: 'center', marginTop: '100px' }}>
          任务依赖图分析功能开发中...
        </p>
        <p style={{ textAlign: 'center', color: '#666' }}>
          将支持任务依赖关系可视化、关键路径分析、负载分析
        </p>
      </div>
    </Card>
  );
};

const TaskAchievement = () => {
  const [stats, setStats] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [versions, setVersions] = useState<Version[]>([]);
  const [iterations, setIterations] = useState<Iteration[]>([]);
  const [selectedVersionId, setSelectedVersionId] = useState<number | undefined>();
  const [selectedIterationId, setSelectedIterationId] = useState<number | undefined>();
  const [viewType, setViewType] = useState<'person' | 'version' | 'iteration'>('person');

  useEffect(() => {
    fetchVersions();
    fetchStats();
  }, []);

  useEffect(() => {
    if (selectedVersionId) {
      fetchIterations(selectedVersionId);
    }
  }, [selectedVersionId]);

  const fetchVersions = async () => {
    try {
      const data = await versionApi.getVersions();
      setVersions(data);
    } catch (error: any) {
      message.error('获取版本列表失败: ' + error.message);
    }
  };

  const fetchIterations = async (versionId: number) => {
    try {
      const data = await iterationApi.getIterations(versionId);
      setIterations(data);
    } catch (error: any) {
      message.error('获取迭代列表失败: ' + error.message);
    }
  };

  const fetchStats = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (selectedVersionId) params.version_ids = String(selectedVersionId);
      if (selectedIterationId) params.iteration_ids = String(selectedIterationId);

      const data = await achievementApi.getAchievementStats(params);
      setStats(data);
    } catch (error: any) {
      message.error('获取统计数据失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const params: any = {};
      if (selectedVersionId) params.version_ids = String(selectedVersionId);
      if (selectedIterationId) params.iteration_ids = String(selectedIterationId);

      const response = await achievementExportApi.exportAchievementExcel(params);
      const url = window.URL.createObjectURL(new Blob([response as BlobPart]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `achievement_${new Date().getTime()}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      message.success('导出成功');
    } catch (error: any) {
      message.error('导出失败: ' + error.message);
    }
  };

  const columns = [
    {
      title: '人员姓名',
      dataIndex: 'person_name',
      key: 'person_name',
      width: 150,
    },
    {
      title: '职位',
      dataIndex: 'person_role',
      key: 'person_role',
      width: 120,
    },
    {
      title: '总任务数',
      dataIndex: 'total_tasks',
      key: 'total_tasks',
      width: 100,
      render: (val: number) => <Tag color="blue">{val}</Tag>,
    },
    {
      title: '已完成',
      dataIndex: 'completed',
      key: 'completed',
      width: 100,
      render: (val: number) => <Tag color="green">{val}</Tag>,
    },
    {
      title: '提前完成',
      dataIndex: 'early',
      key: 'early',
      width: 100,
      render: (val: number) => <Tag color="cyan">{val}</Tag>,
    },
    {
      title: '准时完成',
      dataIndex: 'on_time',
      key: 'on_time',
      width: 100,
      render: (val: number) => <Tag color="green">{val}</Tag>,
    },
    {
      title: '轻微超期',
      dataIndex: 'slightly_late',
      key: 'slightly_late',
      width: 100,
      render: (val: number) => <Tag color="orange">{val}</Tag>,
    },
    {
      title: '严重超期',
      dataIndex: 'severely_late',
      key: 'severely_late',
      width: 100,
      render: (val: number) => <Tag color="red">{val}</Tag>,
    },
    {
      title: '准时率',
      key: 'on_time_rate',
      width: 100,
      render: (_: any, record: any) => {
        const rate = record.completed > 0 ? ((record.early + record.on_time) / record.completed * 100).toFixed(1) : 0;
        return <Tag color={parseFloat(rate) >= 80 ? 'green' : parseFloat(rate) >= 60 ? 'orange' : 'red'}>{rate}%</Tag>;
      },
    },
  ];

  const getChartOption = () => {
    const names = stats.map(s => s.person_name);
    const onTimeRates = stats.map(s => s.completed > 0 ? ((s.early + s.on_time) / s.completed * 100).toFixed(1) : 0);

    return {
      title: {
        text: '任务准时完成率',
        left: 'center',
      },
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          return `
            <div style="padding: 8px;">
              <div><strong>${params[0].name}</strong></div>
              <div>准时率: ${params[0].value}%</div>
            </div>
          `;
        },
      },
      xAxis: {
        type: 'category',
        data: names,
        axisLabel: {
          rotate: 45,
        },
      },
      yAxis: {
        type: 'value',
        max: 100,
        name: '准时率 (%)',
      },
      series: [
        {
          type: 'bar',
          data: onTimeRates,
          itemStyle: {
            color: (params: any) => {
              const value = parseFloat(params.value);
              if (value >= 80) return '#52c41a';
              if (value >= 60) return '#faad14';
              return '#f5222d';
            },
          },
        },
      ],
    };
  };

  return (
    <Card
      title="任务达成统计"
      extra={
        <Space>
          <Select
            style={{ width: 150 }}
            placeholder="选择版本"
            allowClear
            value={selectedVersionId}
            onChange={(val) => {
              setSelectedVersionId(val);
              setSelectedIterationId(undefined);
            }}
          >
            {versions.map(v => (
              <Select.Option key={v.id} value={v.id}>{v.name}</Select.Option>
            ))}
          </Select>
          <Select
            style={{ width: 150 }}
            placeholder="选择迭代"
            allowClear
            value={selectedIterationId}
            onChange={setSelectedIterationId}
            disabled={!selectedVersionId}
          >
            {iterations.map(i => (
              <Select.Option key={i.id} value={i.id}>{i.name}</Select.Option>
            ))}
          </Select>
          <Button icon={<BarChartOutlined />} onClick={fetchStats} loading={loading}>
            查询
          </Button>
          <Button type="primary" onClick={handleExport}>
            导出Excel
          </Button>
        </Space>
      }
    >
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {stats.length > 0 && (
          <ReactECharts
            option={getChartOption()}
            style={{ height: 400 }}
          />
        )}
        <Table
          columns={columns}
          dataSource={stats}
          rowKey="person_id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
          summary={(pageData) => {
            const totalTasks = pageData.reduce((sum, item) => sum + item.total_tasks, 0);
            const totalCompleted = pageData.reduce((sum, item) => sum + item.completed, 0);
            const totalOnTime = pageData.reduce((sum, item) => sum + item.early + item.on_time, 0);
            const onTimeRate = totalCompleted > 0 ? ((totalOnTime / totalCompleted) * 100).toFixed(1) : 0;

            return (
              <Table.Summary fixed>
                <Table.Summary.Row>
                  <Table.Summary.Cell index={0} colSpan={3}>
                    <strong>总计</strong>
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={3}>
                    <strong>{totalTasks}</strong>
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={4}>
                    <strong>{totalCompleted}</strong>
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={5}>
                    <strong>{totalOnTime}</strong>
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={6}>
                    <strong>-</strong>
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={7}>
                    <strong>-</strong>
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={8}>
                    <Tag color={parseFloat(onTimeRate) >= 80 ? 'green' : parseFloat(onTimeRate) >= 60 ? 'orange' : 'red'}>
                      <strong>{onTimeRate}%</strong>
                    </Tag>
                  </Table.Summary.Cell>
                </Table.Summary.Row>
              </Table.Summary>
            );
          }}
        />
      </Space>
    </Card>
  );
};

const ProjectPages = () => {
  const [activeTab, setActiveTab] = useState('versions');

  const items = [
    {
      key: 'versions',
      label: '版本管理',
      icon: <ProjectOutlined />,
      children: <VersionList />,
    },
    {
      key: 'iterations',
      label: '迭代管理',
      icon: <ScheduleOutlined />,
      children: <IterationList />,
    },
    {
      key: 'tasks',
      label: '任务管理',
      icon: <FileTextOutlined />,
      children: <TaskList />,
    },
    {
      key: 'gantt',
      label: '甘特图',
      icon: <BarChartOutlined />,
      children: <GanttChart />,
    },
    {
      key: 'graph',
      label: '任务图分析',
      icon: <TeamOutlined />,
      children: <TaskGraph />,
    },
    {
      key: 'achievement',
      label: '任务达成统计',
      icon: <BarChartOutlined />,
      children: <TaskAchievement />,
    },
  ];

  return (
    <Routes>
      <Route path="/" element={<VersionList />} />
      <Route path="/versions" element={<VersionList />} />
      <Route path="/iterations" element={<IterationList />} />
      <Route path="/tasks" element={<TaskList />} />
      <Route path="/gantt" element={<GanttChart />} />
      <Route path="/graph" element={<TaskGraph />} />
      <Route path="/achievement" element={<TaskAchievement />} />
    </Routes>
  );
};

export default ProjectPages;
