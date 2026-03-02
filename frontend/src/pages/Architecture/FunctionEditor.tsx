import { useState, useEffect } from 'react';
import { Card, Tree, Button, Modal, Form, Input, Select, message, Space, Typography, Tabs } from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ExportOutlined,
  AppstoreOutlined,
  ArrowRightOutlined,
  LinkOutlined,
} from '@ant-design/icons';
import type { DataNode, TreeProps } from 'antd/es/tree';
import { functionApi, moduleApi, type Function, type Module, type Responsibility } from '@/api/architecture';
import { responsibilityApi } from '@/api/team';

const { } = Typography;
const { Option } = Select;

interface FunctionTreeData extends DataNode {
  id: number;
  name: string;
  parent_id?: number;
  responsibility_id?: number;
  isLeaf?: boolean;
}

const FunctionEditor = () => {
  const [functions, setFunctions] = useState<Function[]>([]);
  const [modules] = useState<Module[]>([]);
  const [responsibilities, setResponsibilities] = useState<Responsibility[]>([]);
  const [treeData, setTreeData] = useState<FunctionTreeData[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingFunction, setEditingFunction] = useState<FunctionTreeData | null>(null);
  const [parentFunctionId, setParentFunctionId] = useState<number | undefined>();
  const [selectedFunctionId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState('tree');
  const [form] = Form.useForm();
  const [expandedKeys, setExpandedKeys] = useState<React.Key[]>([]);
  const [, setSelectedKeys] = useState<React.Key[]>([]);

  // Fetch data on mount
  useEffect(() => {
    fetchFunctions();
    fetchModules();
    fetchResponsibilities();
  }, []);

  const fetchFunctions = async () => {
    setLoading(true);
    try {
      const data = await functionApi.getFunctions();
      setFunctions(data);
      const tree = buildTree(data);
      setTreeData(tree);
    } catch (error: any) {
      message.error('获取功能列表失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchModules = async () => {
    try {
      const data = await moduleApi.getModules();
      setModules(data);
    } catch (error: any) {
      message.error('获取模块列表失败: ' + error.message);
    }
  };

  const fetchResponsibilities = async () => {
    try {
      const data = await responsibilityApi.getResponsibilities();
      setResponsibilities(data);
    } catch (error: any) {
      message.error('获取责任田列表失败: ' + error.message);
    }
  };

  const buildTree = (functions: Function[]): FunctionTreeData[] => {
    const map = new Map<number, FunctionTreeData>();
    const roots: FunctionTreeData[] = [];

    // First pass: create all nodes
    functions.forEach(func => {
      map.set(func.id, {
        key: func.id.toString(),
        id: func.id,
        name: func.name,
        parent_id: func.parent_id,
        responsibility_id: func.responsibility_id,
        title: func.name,
        children: [],
      });
    });

    // Second pass: build hierarchy
    functions.forEach(func => {
      const node = map.get(func.id)!;
      if (func.parent_id) {
        const parent = map.get(func.parent_id);
        if (parent) {
          parent.children = parent.children || [];
          parent.children.push(node);
        }
      } else {
        roots.push(node);
      }
    });

    return roots;
  };

  const handleAdd = () => {
    setEditingFunction(null);
    setParentFunctionId(undefined);
    form.resetFields();
    setModalVisible(true);
  };

  const handleAddChild = (parentId: number) => {
    setEditingFunction(null);
    setParentFunctionId(parentId);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (node: FunctionTreeData) => {
    setEditingFunction(node);
    setParentFunctionId(node.parent_id);
    form.setFieldsValue({
      name: node.name,
      responsibility_id: node.responsibility_id,
    });
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '删除功能会同时删除其所有子功能，确定要继续吗？',
      onOk: async () => {
        try {
          await functionApi.deleteFunction(id);
          message.success('删除成功');
          fetchFunctions();
        } catch (error: any) {
          message.error('删除失败: ' + error.message);
        }
      },
    });
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingFunction) {
        await functionApi.updateFunction(editingFunction.id, values);
        message.success('更新成功');
      } else {
        await functionApi.createFunction({
          ...values,
          parent_id: parentFunctionId,
        });
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchFunctions();
    } catch (error: any) {
      if (error.errorFields) {
        return;
      }
      message.error('操作失败: ' + error.message);
    }
  };

  const onDrop: TreeProps['onDrop'] = async (info) => {
    const dropKey = info.node.key as string;
    const dragKey = info.dragNode.key as string;
    const dropPos = info.node.pos.split('-');
    const dropPosition = info.dropPosition - Number(dropPos[dropPos.length - 1]);

    if (!dropKey || !dragKey) return;

    const newParentId = dropPosition === 0 ? parseInt(dropKey) : undefined;

    try {
      await functionApi.moveFunction(parseInt(dragKey), newParentId || 0);
      message.success('移动成功');
      fetchFunctions();
    } catch (error: any) {
      message.error('移动失败: ' + error.message);
    }
  };

  const handleExportMermaid = async () => {
    try {
      const mermaid = await functionApi.exportFunctionsMermaid();
      Modal.info({
        title: 'Mermaid 代码',
        width: 800,
        content: (
          <div>
            <Paragraph code copyable>
              {mermaid}
            </Paragraph>
            <Text type="secondary">
              您可以将此代码复制到 Mermaid Live Editor 中查看流程图
            </Text>
          </div>
        ),
      });
    } catch (error: any) {
      message.error('导出失败: ' + error.message);
    }
  };

  const handleSelect = (selectedKeys: React.Key[], info: any) => {
    if (selectedKeys.length > 0) {
      setSelectedFunctionId(parseInt(selectedKeys[0] as string));
    }
  };

  // Build menu items for each node
  const buildTreeDataWithActions = (nodes: FunctionTreeData[]): FunctionTreeData[] => {
    return nodes.map(node => ({
      ...node,
      children: node.children ? buildTreeDataWithActions(node.children) : [],
      title: (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            width: '100%',
            paddingRight: 50,
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <span>{node.name}</span>
          <Space size="small" style={{ marginLeft: 8 }}>
            <Button
              type="text"
              size="small"
              icon={<PlusOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                handleAddChild(node.id);
              }}
              title="添加子功能"
            />
            <Button
              type="text"
              size="small"
              icon={<EditOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                handleEdit(node);
              }}
              title="编辑"
            />
            <Button
              type="text"
              size="small"
              danger
              icon={<DeleteOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                handleDelete(node.id);
              }}
              title="删除"
            />
          </Space>
        </div>
      ),
    }));
  };

  const treeTabContent = (
    <Card
      title="功能管理"
      extra={
        <Space>
          <Button icon={<ExportOutlined />} onClick={handleExportMermaid}>
            导出 Mermaid
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新增根功能
          </Button>
        </Space>
      }
    >
      <Tree
        showLine
        treeData={buildTreeDataWithActions(treeData)}
        draggable
        onDrop={onDrop}
        loading={loading}
        expandedKeys={expandedKeys}
        onExpand={setExpandedKeys}
        selectedKeys={selectedKeys}
        onSelect={handleSelect}
        blockNode
      />
    </Card>
  );

  const moduleAssociationTabContent = (
    <Card
      title="模块关联"
      extra={
        <Button type="primary" icon={<LinkOutlined />}>
          管理关联
        </Button>
      }
    >
      <div style={{ height: 400, overflow: 'auto', padding: '20px' }}>
        <p style={{ color: '#999', textAlign: 'center', marginTop: '100px' }}>
          模块关联管理功能开发中...
        </p>
        <p style={{ textAlign: 'center', color: '#666' }}>
          将支持拖拽关联、顺序管理
        </p>
      </div>
    </Card>
  );

  const dataFlowTabContent = (
    <Card
      title="数据流定义"
      extra={
        <Button type="primary" icon={<ArrowRightOutlined />}>
          新增数据流
        </Button>
      }
    >
      <div style={{ height: 400, overflow: 'auto', padding: '20px' }}>
        <p style={{ color: '#999', textAlign: 'center', marginTop: '100px' }}>
          数据流定义功能开发中...
        </p>
        <p style={{ textAlign: 'center', color: '#666' }}>
          将支持定义功能间数据流向
        </p>
      </div>
    </Card>
  );

  const tabItems = [
    {
      key: 'tree',
      label: '功能树',
      icon: <AppstoreOutlined />,
      children: treeTabContent,
    },
    {
      key: 'modules',
      label: '模块关联',
      icon: <LinkOutlined />,
      children: moduleAssociationTabContent,
    },
    {
      key: 'dataflows',
      label: '数据流',
      icon: <ArrowRightOutlined />,
      children: dataFlowTabContent,
    },
  ];

  return (
    <div>
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={tabItems}
      />

      <Modal
        title={editingFunction ? '编辑功能' : '新增功能'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        okText="确定"
        cancelText="取消"
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="功能名称"
            rules={[{ required: true, message: '请输入功能名称' }]}
          >
            <Input placeholder="请输入功能名称" />
          </Form.Item>
          <Form.Item
            name="responsibility_id"
            label="责任田"
          >
            <Select
              placeholder="请选择责任田（可选）"
              allowClear
            >
              {responsibilities.map(resp => (
                <Option key={resp.id} value={resp.id}>
                  {resp.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          {parentFunctionId && (
            <Form.Item label="父功能">
              <Input value={functions.find(f => f.id === parentFunctionId)?.name} disabled />
            </Form.Item>
          )}
        </Form>
      </Modal>
    </div>
  );
};

export default FunctionEditor;
