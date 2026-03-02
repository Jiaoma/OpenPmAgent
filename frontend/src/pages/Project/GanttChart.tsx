import { useState, useEffect } from 'react';
import { Card, Select, Button, Space, message, Typography, Spin, DatePicker } from 'antd';
import {
  ReloadOutlined,
  ExportOutlined,
  FilterOutlined,
} from '@ant-design/icons';
import { ganttApi, versionApi, iterationApi, type Version, type Iteration } from '@/api/project';
import ReactECharts from 'echarts-for-react';

const { Text } = Typography;
const { RangePicker } = DatePicker;

interface GanttTask {
  id: number;
  name: string;
  iteration_name?: string;
  start_date: string;
  end_date: string;
  man_months: number;
  status: 'pending' | 'in_progress' | 'completed';
  developer_name?: string;
}

const GanttChart = () => {
  const [loading, setLoading] = useState(false);
  const [versions, setVersions] = useState<Version[]>([]);
  const [iterations, setIterations] = useState<Iteration[]>([]);
  const [ganttData, setGanttData] = useState<GanttTask[]>([]);
  const [selectedVersionId, setSelectedVersionId] = useState<number | undefined>();
  const [selectedIterationId, setSelectedIterationId] = useState<number | undefined>();
  const [dateRange, setDateRange] = useState<[any, any] | null>(null);
  const [, setChartInstance] = useState<any>(null);

  useEffect(() => {
    fetchVersions();
    fetchGanttData();
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

  const fetchGanttData = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (selectedVersionId) params.version_id = selectedVersionId;
      if (selectedIterationId) params.iteration_id = selectedIterationId;
      if (dateRange) {
        params.start_date = dateRange[0].format('YYYY-MM-DD');
        params.end_date = dateRange[1].format('YYYY-MM-DD');
      }

      const data = await ganttApi.getGanttData(params);
      setGanttData(data);
    } catch (error: any) {
      message.error('获取甘特图数据失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExportMermaid = async () => {
    try {
      const params: any = {};
      if (selectedVersionId) params.version_id = selectedVersionId;
      if (selectedIterationId) params.iteration_id = selectedIterationId;
      
      const mermaid = await ganttApi.exportGanttMermaid(params);
      const blob = new Blob([mermaid], { type: 'text/markdown' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'gantt_diagram.md';
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      message.success('Mermaid导出成功');
    } catch (error: any) {
      message.error('导出失败: ' + error.message);
    }
  };

  const getChartOption = () => {
    if (!ganttData.length) {
      return {
        title: {
          text: '无数据',
          left: 'center',
          top: 'center',
        },
      };
    }

    // Prepare data for Gantt chart
    const tasks = ganttData.map((task, index) => ({
      name: task.name,
      value: [
        task.start_date,
        task.end_date,
        task.id,
        task.status,
        task.developer_name,
      ],
      itemStyle: {
        color: getStatusColor(task.status),
      },
    }));

    // Group tasks by iteration
    const iterationGroups = ganttData.reduce((acc, task) => {
      const key = task.iteration_name || '未分组';
      if (!acc[key]) acc[key] = [];
      acc[key].push(task);
      return acc;
    }, {} as Record<string, GanttTask[]>);

    return {
      title: {
        text: '项目甘特图',
        left: 'center',
      },
      tooltip: {
        formatter: (params: any) => {
          const task = ganttData.find(t => t.id === params.value[2]);
          if (!task) return '';
          return `
            <div style="padding: 8px;">
              <div><strong>${task.name}</strong></div>
              <div>开始时间: ${task.start_date}</div>
              <div>结束时间: ${task.end_date}</div>
              <div>工作量: ${task.man_months} 人月</div>
              <div>状态: ${getStatusLabel(task.status)}</div>
              <div>开发人员: ${task.developer_name || '未分配'}</div>
              <div>迭代: ${task.iteration_name || '-'}</div>
            </div>
          `;
        },
      },
      legend: {
        data: [
          { name: '待开始', itemStyle: { color: '#999' } },
          { name: '进行中', itemStyle: { color: '#1890ff' } },
          { name: '已完成', itemStyle: { color: '#52c41a' } },
        ],
        top: 30,
      },
      grid: {
        left: '15%',
        right: '5%',
        bottom: '15%',
      },
      xAxis: {
        type: 'time',
        min: getMinDate(),
        max: getMaxDate(),
      },
      yAxis: {
        data: Object.keys(iterationGroups),
        type: 'category',
        axisLabel: {
          fontSize: 12,
        },
      },
      series: [
        {
          type: 'custom',
          renderItem: (params: any, api: any) => {
            const task = ganttData[params.dataIndex];
            const startDate = new Date(task.start_date).getTime();
            const endDate = new Date(task.end_date).getTime();
            
            return {
              type: 'rect',
              shape: {
                x: api.coord([startDate, task.iteration_name])[0],
                y: api.coord([startDate, task.iteration_name])[1] - 10,
                width: api.coord([endDate, task.iteration_name])[0] - api.coord([startDate, task.iteration_name])[0],
                height: 20,
              },
              style: {
                fill: getStatusColor(task.status),
                stroke: '#fff',
                lineWidth: 1,
              },
            };
          },
          data: ganttData,
          z: 100,
        },
      ],
      dataZoom: [
        {
          type: 'slider',
          show: true,
          xAxisIndex: [0],
          start: 0,
          end: 100,
        },
        {
          type: 'inside',
          xAxisIndex: [0],
          start: 0,
          end: 100,
        },
      ],
    };
  };

  const getMinDate = () => {
    if (!ganttData.length) return new Date().getTime();
    const minDate = Math.min(...ganttData.map(t => new Date(t.start_date).getTime()));
    return minDate - 7 * 24 * 60 * 60 * 1000; // Add 7 days buffer
  };

  const getMaxDate = () => {
    if (!ganttData.length) return new Date().getTime() + 30 * 24 * 60 * 60 * 1000;
    const maxDate = Math.max(...ganttData.map(t => new Date(t.end_date).getTime()));
    return maxDate + 7 * 24 * 60 * 60 * 1000; // Add 7 days buffer
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

  const onChartReady = (chartInstance: any) => {
    setChartInstance(chartInstance);
  };

  return (
    <Card
      title="甘特图"
      extra={
        <Space>
          <RangePicker onChange={(dates) => setDateRange(dates as any)} />
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
          <Button icon={<ReloadOutlined />} onClick={fetchGanttData}>
            刷新
          </Button>
          <Button icon={<ExportOutlined />} onClick={handleExportMermaid}>
            导出Mermaid
          </Button>
        </Space>
      }
    >
      <Spin spinning={loading}>
        <div style={{ height: '600px' }}>
          {ganttData.length > 0 ? (
            <ReactECharts
              option={getChartOption()}
              style={{ height: '100%', width: '100%' }}
              onChartReady={onChartReady}
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
              <FilterOutlined style={{ fontSize: 48, marginBottom: 16 }} />
              <p>暂无数据，请调整筛选条件或创建任务</p>
            </div>
          )}
        </div>
      </Spin>

      {/* Legend */}
      <div style={{ marginTop: 16, display: 'flex', justifyContent: 'center', gap: 24 }}>
        <Space>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ width: 16, height: 16, backgroundColor: '#999' }}></div>
            <Text>待开始</Text>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ width: 16, height: 16, backgroundColor: '#1890ff' }}></div>
            <Text>进行中</Text>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ width: 16, height: 16, backgroundColor: '#52c41a' }}></div>
            <Text>已完成</Text>
          </div>
        </Space>
      </div>
    </Card>
  );
};

export default GanttChart;
