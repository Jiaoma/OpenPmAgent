import { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Card, Space, Select, Button, message } from 'antd';
import ReactECharts from 'echarts-for-react';
import PersonList from './PersonList';
import GroupList from './GroupList';
import WorkloadView from './WorkloadView';
import { radarApi, graphApi, personApi, groupApi } from '@/api/team';

const CapabilityRadar = () => {
  const [loading, setLoading] = useState(false);
  const [personRadarData, setPersonRadarData] = useState<any>(null);
  const [groupRadarData, setGroupRadarData] = useState<any>(null);
  const [viewType, setViewType] = useState<'person' | 'group'>('person');
  const [selectedPersonId, setSelectedPersonId] = useState<number | null>(null);
  const [selectedGroupId, setSelectedGroupId] = useState<number | null>(null);
  const [personOptions, setPersonOptions] = useState<{ value: number; label: string }[]>([]);
  const [groupOptions, setGroupOptions] = useState<{ value: number; label: string }[]>([]);

  useEffect(() => {
    fetchPersonOptions();
    fetchGroupOptions();
  }, []);

  const fetchPersonOptions = async () => {
    try {
      const data = await personApi.getPersons({ limit: 1000 });
      setPersonOptions(data.map((p: any) => ({ value: p.id, label: `${p.name} (${p.emp_id})` })));
    } catch (error: any) {
      message.error('获取人员列表失败: ' + error.message);
    }
  };

  const fetchGroupOptions = async () => {
    try {
      const data = await groupApi.getGroups({ limit: 1000 });
      setGroupOptions(data.map((g: any) => ({ value: g.id, label: g.name })));
    } catch (error: any) {
      message.error('获取小组列表失败: ' + error.message);
    }
  };

  const handleFetch = async () => {
    setLoading(true);
    try {
      if (viewType === 'person' && selectedPersonId) {
        const data = await radarApi.getPersonCapabilityRadar(selectedPersonId);
        setPersonRadarData(data);
      } else if (viewType === 'group' && selectedGroupId) {
        const data = await radarApi.getGroupCapabilityRadar(selectedGroupId);
        setGroupRadarData(data);
      }
    } catch (error: any) {
      message.error('获取能力数据失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const radarOption = {
    tooltip: {
      formatter: (value: number, item: any) => `${item}: ${value}`,
    },
  };

  const personSeries = personRadarData ? [{
    type: 'radar',
    data: personRadarData.values,
    name: personRadarData.person_name,
  }] : [];

  const groupSeries = groupRadarData ? [{
    type: 'radar',
    data: groupRadarData.values,
    name: groupRadarData.group_name,
  }] : [];

  const series = viewType === 'person' ? personSeries : groupSeries;

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title="能力雷达图"
      >
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Select
            style={{ width: 300 }}
            placeholder="选择视图类型"
            value={viewType}
            onChange={(v) => {
              setViewType(v);
              setSelectedPersonId(null);
              setSelectedGroupId(null);
            }}
          >
            <option value="person">个人能力</option>
            <option value="group">团队平均能力</option>
          </Select>
          <Select
            style={{ width: 300 }}
            placeholder="选择人员（个人视图）"
            value={selectedPersonId || undefined}
            onChange={setSelectedPersonId}
            disabled={viewType !== 'person'}
          >
            <option value="">请选择人员</option>
            {personOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </Select>
          <Select
            style={{ width: 300 }}
            placeholder="选择小组（团队视图）"
            value={selectedGroupId || undefined}
            onChange={setSelectedGroupId}
            disabled={viewType !== 'group'}
          >
            <option value="">请选择小组</option>
            {groupOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </Select>
          <Button type="primary" onClick={handleFetch} loading={loading}>
            查询
          </Button>
        </Space>
      </Card>
      {(personRadarData || groupRadarData) && (
        <div style={{ marginTop: 24 }}>
          {personRadarData && viewType === 'person' && (
            <ReactECharts
              option={radarOption}
              style={{ height: 500 }}
              series={personSeries}
              notMerge={true}
            />
          )}
          {groupRadarData && viewType === 'group' && (
            <ReactECharts
              option={radarOption}
              style={{ height: 500 }}
              series={groupSeries}
              notMerge={true}
            />
          )}
        </div>
      )}
    </div>
  );
};

const TeamPages = () => {
  return (
    <Routes>
      <Route path="/" element={<PersonList />} />
      <Route path="/persons" element={<PersonList />} />
      <Route path="/groups" element={<GroupList />} />
      <Route path="/workload" element={<WorkloadView />} />
      <Route path="/capability" element={<CapabilityRadar />} />
    </Routes>
  );
};

export default TeamPages;
