import { useState, useEffect } from 'react';
import { Card, Tree, Button, Modal, Form, Input, message, Space, Typography } from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ExportOutlined,
  FolderOutlined,
  FolderOpenOutlined,
} from '@ant-design/icons';
import type { DataNode, TreeProps } from 'antd/es/tree';
import { moduleApi, type Module } from '@/api/architecture';


const { } = Typography;

interface ModuleTreeData extends DataNode {
  id: number;
  name: string;
  parent_id?: number;
  isLeaf?: boolean;
}

const ModuleEditor = () => {
  const [modules, setModules] = useState<Module[]>([]);
  const [treeData, setTreeData] = useState<ModuleTreeData[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingModule, setEditingModule] = useState<ModuleTreeData | null>(null);
  const [parentModuleId, setParentModuleId] = useState<number | undefined>();
  const [form] = Form.useForm();
  const [expandedKeys, setExpandedKeys] = useState<React.Key[]>([]);
  const [selectedKeys, setSelectedKeys] = useState<React.Key[]>([]);

  // Fetch modules on mount
  useEffect(() => {
    fetchModules();
  }, []);

  const fetchModules = async () => {
    setLoading(true);
    try {
      const data = await moduleApi.getModules();
      setModules(data);
      const tree = buildTree(data);
      setTreeData(tree);
    } catch (error: any) {
      message.error('获取模块列表失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const buildTree = (modules: Module[]): ModuleTreeData[] => {
    const map = new Map<number, ModuleTreeData>();
    const roots: ModuleTreeData[] = [];

    // First pass: create all nodes
    modules.forEach(module => {
      map.set(module.id, {
        key: module.id.toString(),
        id: module.id,
        name: module.name,
        parent_id: module.parent_id,
        title: module.name,
        icon: <FolderOutlined />,
        children: [],
      });
    });

    // Second pass: build hierarchy
    modules.forEach(module => {
      const node = map.get(module.id)!;
      if (module.parent_id) {
        const parent = map.get(module.parent_id);
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
    setEditingModule(null);
    setParentModuleId(undefined);
    form.resetFields();
    setModalVisible(true);
  };

  const handleAddChild = (parentId: number) => {
    setEditingModule(null);
    setParentModuleId(parentId);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (node: ModuleTreeData) => {
    setEditingModule(node);
    setParentModuleId(node.parent_id);
    form.setFieldsValue({
      name: node.name,
    });
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '删除模块会同时删除其所有子模块，确定要继续吗？',
      onOk: async () => {
        try {
          await moduleApi.deleteModule(id);
          message.success('删除成功');
          fetchModules();
        } catch (error: any) {
          message.error('删除失败: ' + error.message);
        }
      },
    });
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingModule) {
        await moduleApi.updateModule(editingModule.id, values);
        message.success('更新成功');
      } else {
        await moduleApi.createModule({
          ...values,
          parent_id: parentModuleId,
        });
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchModules();
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
      await moduleApi.moveModule(parseInt(dragKey), newParentId || 0);
      message.success('移动成功');
      fetchModules();
    } catch (error: any) {
      message.error('移动失败: ' + error.message);
    }
  };

  const handleExportMermaid = async () => {
    try {
      const mermaid = await moduleApi.exportModulesMermaid();
      const modal = Modal.info({
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

  // Build menu items for each node
  const buildTreeDataWithActions = (nodes: ModuleTreeData[]): ModuleTreeData[] => {
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
              title="添加子模块"
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

  return (
    <div>
      <Card
        title="模块管理"
        extra={
          <Space>
            <Button icon={<ExportOutlined />} onClick={handleExportMermaid}>
              导出 Mermaid
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增根模块
            </Button>
          </Space>
        }
      >
        <Tree
          showLine
          switcherIcon={<FolderOpenOutlined />}
          treeData={buildTreeDataWithActions(treeData)}
          draggable
          onDrop={onDrop}
          loading={loading}
          expandedKeys={expandedKeys}
          onExpand={setExpandedKeys}
          selectedKeys={selectedKeys}
          onSelect={setSelectedKeys}
          blockNode
        />
      </Card>

      <Modal
        title={editingModule ? '编辑模块' : '新增模块'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="模块名称"
            rules={[{ required: true, message: '请输入模块名称' }]}
          >
            <Input placeholder="请输入模块名称" />
          </Form.Item>
          {parentModuleId && (
            <Form.Item label="父模块">
              <Input value={modules.find(m => m.id === parentModuleId)?.name} disabled />
            </Form.Item>
          )}
        </Form>
      </Modal>
    </div>
  );
};

export default ModuleEditor;
