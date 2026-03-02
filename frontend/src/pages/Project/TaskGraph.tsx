import { useState, useEffect } from 'react';
import { Card, Button, Space, message, Spin, Select, Drawer, Descriptions, Tag, Typography } from 'antd';
import {
  ReloadOutlined,
  NodeIndexOutlined,
  ApartmentOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { taskApi, versionApi, iterationApi, taskGraphApi, type Task, type Version, type Iteration } from '@/api/project';
import ReactECharts from 'echarts-for-react';


const { Text } = Typography;

interface TaskNode {
  id: number;
  name: string;
  category: number;
  status: string;
  developer_name?: string;
}

interface TaskEdge {
  source: number;
  target: number;
  name: string;
}

const TaskGraph = () => {
  const [loading, setLoading] = useState(false);
  const [versions, setVersions] = useState<Version[]>([]);
  const [iterations, setIterations] = useState<Iteration[]>([]);
  const [selectedVersionId, setSelectedVersionId] = useState<number | undefined>();
  const [selectedIterationId, setSelectedIterationId] = useState<number | undefined>();
  const [taskGraph, setTaskGraph] = useState({ nodes: [], edges: [] });
  const [criticalPath, setCriticalPath] = useState<any[]>([]);
  const [highestLoadPerson, setHighestLoadPerson] = useState<any>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [drawerVisible, setDrawerVisible] = useState(false);

  useEffect(() => {
    fetchVersions();
    fetchTaskGraph();
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

  const fetchTaskGraph = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (selectedVersionId) params.version_id = selectedVersionId;
      if (selectedIterationId) params.iteration_id = selectedIterationId;

      const data = await taskGraphApi.getTaskGraph(selectedIterationId);
      setTaskGraph(data);
    } catch (error: any) {
      message.error('获取任务图数据失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeCriticalPath = async () => {
    try {
      const params: any = {};
      if (selectedVersionId) params.version_id = selectedVersionId;
      if (selectedIterationId) params.iteration_id = selectedIterationId;

      const path = await taskGraphApi.getLongestPath(selectedIterationId);
      setCriticalPath(path);
      message.success('关键路径分析完成');
    } catch (error: any) {
      message.error('分析关键路径失败: ' + error.message);
    }
  };

  const handleGetHighestLoad = async () => {
    try {
      const params: any = {};
      if (selectedVersionId) params.version_id = selectedVersionId;
      if (selectedIterationId) params.iteration_id = selectedIterationId;

      const person = await taskGraphApi.getHighestLoadPerson(selectedIterationId);
      setHighestLoadPerson(person);
      message.success('负载最高人员查询完成');
    } catch (error: any) {
      message.error('查询负载最高人员失败: ' + error.message);
    }
  };

  const handleNodeClick = (params: any) => {
    const task = (taskGraph as any).tasks?.find((t: Task) => t.id === params.data.id);
    if (task) {
      setSelectedTask(task);
      setDrawerVisible(true);
    }
  };

  const getChartOption = () => {
    if (!taskGraph.nodes.length) {
      return {
        title: {
          text: '无数据',
          left: 'center',
          top: 'center',
        },
      };
    }

    const nodes = taskGraph.nodes.map((node: any) => ({
      id: node.id,
      name: node.name,
      symbolSize: 60,
      category: node.status,
      itemStyle: {
        color: getStatusColor(node.status),
      },
    }));

    const links = taskGraph.edges.map((edge: any) => ({
      source: edge.source,
      target: edge.target,
      label: {
        show: true,
        formatter: edge.name || '',
        color: '#666',
      },
      lineStyle: {
        color: '#999',
        curveness: 0.3,
      },
    }));

    const categories = [
      { name: '待开始', itemStyle: { color: '#999' } },
      { name: '进行中', itemStyle: { color: '#1890ff' } },
      { name: '已完成', itemStyle: { color: '#52c41a' } },
    ];

    return {
      title: {
        text: '任务依赖关系图',
        left: 'center',
      },
      tooltip: {
        formatter: (params: any) => {
          if (params.dataType === 'node') {
            return `
              <div style="padding: 8px;">
                <div><strong>${params.data.name}</strong></div>
                <div>状态: ${getStatusLabel(params.data.category)}</div>
                <div>开发人员: ${params.data.developer_name || '未分配'}</div>
              </div>
            `;
          } else if (params.dataType === 'edge') {
            return params.data.name || '依赖关系';
          }
          return '';
        },
      },
      legend: {
        data: categories,
        top: 30,
      },
      animationDuration: 1500,
      animationEasingUpdate: 'quinticInOut',
      series: [
        {
          type: 'graph',
          layout: 'force',
          data: nodes,
          links: links,
          categories: categories,
          roam: true,
          label: {
            show: true,
            position: 'bottom',
            formatter: (params: any) => {
              return params.data.name.length > 8
                ? params.data.name.substring(0, 8) + '...'
                : params.data.name;
            },
          },
          force: {
            repulsion: 200,
            edgeLength: 100,
            gravity: 0.1,
          },
          edgeSymbol: ['circle', 'arrow'],
          edgeSymbolSize: [4, 10],
          lineStyle: {
            color: 'source',
            curveness: 0.3,
          },
        },
      ],
    };
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return '#999';
      case 'in_progress': return '#1890ff';
      case 'completed': return '#52c41a';
      default: return '#999';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending': return '待开始';
      case 'in_progress': return '进行中';
      case 'completed': return '已完成';
      default: return status;
    }
  };

  return (
    <div>
      <Card
        title="任务图分析"
        extra={
          <Space>
            <Select
              style={{ width: 150 }}
              placeholder="选择版本"
              allowClear
              value={selectedVersionId}
              onChange={setSelectedVersionId}
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
            <Button icon={<ReloadOutlined />} onClick={fetchTaskGraph}>
              刷新
            </Button>
            <Button icon={<ApartmentOutlined />} onClick={handleAnalyzeCriticalPath}>
              分析最长路径
            </Button>
            <Button icon={<UserOutlined />} onClick={handleGetHighestLoad}>
              查看负载最高人员
            </Button>
          </Space>
        }
      >
        <Spin spinning={loading}>
          <div style={{ height: '600px' }}>
            {taskGraph.nodes.length > 0 ? (
              <ReactECharts
                option={getChartOption()}
                style={{ height: '100%', width: '100%' }}
                onEvents={{
                  click: handleNodeClick,
                }}
              />
            ) : (
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                color: '#999',
              }}>
                <NodeIndexOutlined style={{ fontSize: 48, marginBottom: 16 }} />
                <p>暂无数据，请调整筛选条件或创建任务</p>
              </div>
            )}
          </div>
        </Spin>
      </Card>

      {/* Critical Path Display */}
      {criticalPath.length > 0 && (
        <Card
          title="关键路径"
          style={{ marginTop: 16 }}
          type="inner"
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            {criticalPath.map((task, index) => (
              <div key={task.id} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Tag color="blue">#{index + 1}</Tag>
                <Text>{task.name}</Text>
                {index < criticalPath.length - 1 && <Text type="secondary">→</Text>}
              </div>
            ))}
          </Space>
        </Card>
      )}

      {/* Highest Load Person Display */}
      {highestLoadPerson && (
        <Card
          title="负载最高人员"
          style={{ marginTop: 16 }}
          type="inner"
        >
          <Descriptions column={2} size="small">
            <Descriptions.Item label="姓名">
              {highestLoadPerson.name}
            </Descriptions.Item>
            <Descriptions.Item label="总工作量">
              {highestLoadPerson.total_workload} 人月
            </Descriptions.Item>
            <Descriptions.Item label="任务数">
              {highestLoadPerson.task_count}
            </Descriptions.Item>
            <Descriptions.Item label="职位">
              {highestLoadPerson.position}
            </Descriptions.Item>
          </Descriptions>
        </Card>
      )}

      {/* Task Details Drawer */}
      <Drawer
        title="任务详情"
        width={600}
        open={drawerVisible}
        onClose={() => setDrawerVisible(false)}
      >
        {selectedTask && (
          <Descriptions column={1} bordered>
            <Descriptions.Item label="任务名称">{selectedTask.name}</Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={getStatusColor(selectedTask.status)}>
                {getStatusLabel(selectedTask.status)}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="开始时间">{selectedTask.start_date}</Descriptions.Item>
            <Descriptions.Item label="结束时间">{selectedTask.end_date}</Descriptions.Item>
            <Descriptions.Item label="工作量">{selectedTask.man_months} 人月</Descriptions.Item>
            <Descriptions.Item label="开发人员">
              {selectedTask.developer_name || '未分配'}
            </Descriptions.Item>
            <Descriptions.Item label="交付负责人">
              {selectedTask.delivery_owner_name || '未分配'}
            </Descriptions.Item>
            <Descriptions.Item label="测试人员">
              {selectedTask.tester_name || '未分配'}
            </Descriptions.Item>
            <Descriptions.Item label="迭代">
              {selectedTask.iteration_name || '-'}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Drawer>
    </div>
  );
};

export default TaskGraph;
