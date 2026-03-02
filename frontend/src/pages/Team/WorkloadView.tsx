import { useState } from 'react';
import { Card, DatePicker, Select, Table, Statistic, Row, Col, Tag, message, Input, Button } from 'antd';
import { BarChartOutlined, TeamOutlined } from '@ant-design/icons';
import { workloadApi, type WorkloadPersonResponse, type WorkloadMonthlySummary } from '@/api/team';
import type { Dayjs } from 'dayjs/esm';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;

const WorkloadView = () => {
  const [loading, setLoading] = useState(false);
  const [viewType, setViewType] = useState<'person' | 'group' | 'monthly'>('person');
  const [, setSelectedPersonId] = useState<number | null>(null);
  const [, setSelectedGroupId] = useState<number | null>(null);
  const [selectedMonth, setSelectedMonth] = useState<number>(dayjs().month() + 1);
  const [selectedYear, setSelectedYear] = useState<number>(dayjs().year());
  const [workloadData, setWorkloadData] = useState<WorkloadPersonResponse[] | WorkloadMonthlySummary | null>(null);
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs]>([
    dayjs().startOf('month'),
    dayjs().endOf('month'),
  ]);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const startDate = dateRange[0].format('YYYY-MM-DD');
      const endDate = dateRange[1].format('YYYY-MM-DD');

      let data;
      if (viewType === 'person' && selectedPersonId) {
        data = await workloadApi.getPersonWorkload(selectedPersonId, startDate, endDate);
      } else if (viewType === 'group' && selectedGroupId) {
        data = await workloadApi.getGroupWorkload(selectedGroupId, startDate, endDate);
      } else if (viewType === 'monthly') {
        data = await workloadApi.getMonthlyWorkloadSummary(selectedMonth, selectedYear);
      }

      setWorkloadData(data);
    } catch (error: any) {
      message.error('获取负载分析数据失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const personColumns = [
    { title: '姓名', dataIndex: 'person_name', key: 'person_name', width: 120 },
    { title: '任务数', dataIndex: 'task_count', key: 'task_count', width: 100 },
    {
      title: '工作负载(人月)',
      dataIndex: 'workload',
      key: 'workload',
      width: 150,
      render: (value: number) => (
        <Tag color={value > 3 ? 'red' : value > 2 ? 'orange' : 'green'}>
          {value.toFixed(2)}
        </Tag>
      ),
    },
  ];

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="分析视图"
              value={viewType === 'person' ? '个人负载' : viewType === 'group' ? '小组负载' : '月度汇总'}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
        <Col span={18}>
          <Card>
            <Row gutter={[16, 16]} align="middle">
              <Col span={8}>
                <Select value={viewType} onChange={(v) => setViewType(v)} style={{ width: '100%' }}>
                  <Option value="person">个人负载</Option>
                  <Option value="group">小组负载</Option>
                  <Option value="monthly">月度汇总</Option>
                </Select>
              </Col>
              <Col span={16}>
                {viewType === 'monthly' ? (
                  <>
                    <Select
                      value={selectedMonth}
                      onChange={setSelectedMonth}
                      style={{ width: 120, marginRight: 8 }}
                    >
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(m => (
                        <Option key={m} value={m}>{m}月</Option>
                      ))}
                    </Select>
                    <Input
                      type="number"
                      value={selectedYear}
                      onChange={(e) => setSelectedYear(Number(e.target.value))}
                      style={{ width: 100, marginRight: 8 }}
                      suffix="年"
                    />
                  </>
                ) : (
                  <RangePicker
                    value={dateRange}
                    onChange={(dates) => {
              if (dates && dates[0] && dates[1]) {
                setDateRange([dates[0], dates[1]]);
              }
            }}
                    format="YYYY-MM-DD"
                    style={{ width: '100%' }}
                  />
                )}
              </Col>
              <Col span={8} style={{ textAlign: 'right' }}>
                <Button type="primary" onClick={handleSearch} loading={loading}>
                  查询
                </Button>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {viewType === 'monthly' && workloadData && 'person_workloads' in workloadData ? (
        <Card title={`月度负载统计 - ${selectedYear}年${selectedMonth}月`}>
          <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
            <Col span={8}>
              <Statistic
                title="总工作负载"
                value={workloadData.total_workload}
                suffix="人月"
                prefix={<TeamOutlined />}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="平均负载"
                value={workloadData.avg_workload}
                suffix="人月"
                valueStyle={{ color: '#3f8600' }}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="负载最高人员"
                value={workloadData.highest_load || '-'}
                valueStyle={{ color: '#cf1322' }}
              />
            </Col>
          </Row>
          <Table
            columns={personColumns}
            dataSource={workloadData.person_workloads}
            rowKey="person_id"
            pagination={false}
            scroll={{ y: 400 }}
          />
        </Card>
      ) : (
        <Card title={viewType === 'person' ? '个人负载分析' : '小组负载分析'}>
          <p style={{ textAlign: 'center', color: '#999', padding: '40px 0' }}>
            请先选择分析对象，然后点击查询
          </p>
        </Card>
      )}
    </div>
  );
};

export default WorkloadView;
