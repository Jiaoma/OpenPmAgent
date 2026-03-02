import { useState } from 'react';
import {
  Button,
  Card,
  Form,
  Input,
  message,
  Upload,
  Modal,
  Checkbox,
  Descriptions,
  Space,
  Typography,
  Divider,
  Alert,
  Spin,
} from 'antd';
import {
  DownloadOutlined,
  UploadOutlined,

  FileTextOutlined,
} from '@ant-design/icons';
import { backupApi, type BackupResponse, type RestoreResponse } from '@/api/backup';


const { Title, Text } = Typography;

const BackupPage = () => {
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [restoreModalVisible, setRestoreModalVisible] = useState(false);
  const [restoreLoading, setRestoreLoading] = useState(false);
  const [lastBackup, setLastBackup] = useState<BackupResponse | null>(null);
  const [restoreResult, setRestoreResult] = useState<RestoreResponse | null>(null);
  const [form] = Form.useForm();

  const handleCreateBackup = async () => {
    setLoading(true);
    try {
      const values = await form.validateFields();
      const backup = await backupApi.createBackup(values);
      setLastBackup(backup);
      message.success('备份创建成功');
    } catch (error: any) {
      message.error('备份创建失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadBackup = async () => {
    setDownloading(true);
    try {
      const response = await backupApi.downloadBackup();
      const url = window.URL.createObjectURL(new Blob([response as BlobPart]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `backup_${new Date().getTime()}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      message.success('备份下载成功');
    } catch (error: any) {
      message.error('备份下载失败: ' + error.message);
    } finally {
      setDownloading(false);
    }
  };

  const handleRestoreUpload = async (info: any) => {
    if (info.file.status === 'done') {
      try {
        const reader = new FileReader();
        reader.onload = async (e) => {
          try {
            const backupData = JSON.parse((e.target?.result as string) || '{}');
            setRestoreModalVisible(true);
            message.success('备份文件上传成功');
          } catch (parseError) {
            message.error('备份文件格式错误');
          }
        };
        reader.readAsText(info.file.originFileObj);
      } catch (error: any) {
        message.error('备份文件解析失败: ' + error.message);
      }
    }
  };

  const handleRestore = async (restoreOptions: any) => {
    setRestoreLoading(true);
    try {
      await form.validateFields();
      const restoreRequest = {
        backup_data: lastBackup,
        restore_options: restoreOptions,
      };
      const result = await backupApi.restoreFromBackup(restoreRequest);
      setRestoreResult(result);

      if (result && result.errors && result.errors.length > 0) {
        message.warning('恢复完成，但存在错误');
      } else {
        message.success('恢复成功');
      }
      setRestoreModalVisible(false);
    } catch (error: any) {
      message.error('恢复失败: ' + error.message);
    } finally {
      setRestoreLoading(false);
    }
  };

  const uploadProps = {
    name: 'file',
    accept: '.json',
    beforeUpload: () => false, // Prevent automatic upload
    onChange: handleRestoreUpload,
    showUploadList: false,
  };

  return (
    <div style={{ padding: '24px' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Page Header */}
        <div>
          <Title level={2}>
            <FileTextOutlined /> 备份与恢复
          </Title>
          <Text type="secondary">
            管理系统数据的备份和恢复操作
          </Text>
        </div>

        <Divider />

        {/* Create Backup Card */}
        <Card
          title="创建备份"
          extra={
            <Space>
              <Button onClick={handleCreateBackup} loading={loading}>
                创建备份
              </Button>
              <Button
                icon={<DownloadOutlined />}
                onClick={handleDownloadBackup}
                loading={downloading}
              >
                下载最新备份
              </Button>
            </Space>
          }
        >
          <Form form={form} layout="vertical">
            <Form.Item
              name="name"
              label="备份名称"
              rules={[{ required: true, message: '请输入备份名称' }]}
            >
              <Input placeholder="例如：生产环境备份_20250101" />
            </Form.Item>
            <Form.Item name="description" label="备份描述">
              <Input.TextArea
                rows={3}
                placeholder="请输入备份描述（可选）"
              />
            </Form.Item>
          </Form>

          {lastBackup && (
            <Alert
              message="最新备份信息"
              description={
                <Descriptions column={2} size="small">
                  <Descriptions.Item label="备份名称">
                    {lastBackup.name}
                  </Descriptions.Item>
                  <Descriptions.Item label="备份时间">
                    {new Date(lastBackup.timestamp).toLocaleString()}
                  </Descriptions.Item>
                  <Descriptions.Item label="描述">
                    {lastBackup.description}
                  </Descriptions.Item>
                  <Descriptions.Item label="数据范围">
                    <Space size="small">
                      {lastBackup.data.team && <Text>团队</Text>}
                      {lastBackup.data.architecture && <Text>架构</Text>}
                      {lastBackup.data.project && <Text>项目</Text>}
                    </Space>
                  </Descriptions.Item>
                </Descriptions>
              }
              type="info"
              style={{ marginTop: 16 }}
            />
          )}
        </Card>

        {/* Restore Backup Card */}
        <Card
          title="从备份恢复"
          extra={
            <Upload {...uploadProps}>
              <Button icon={<UploadOutlined />}>选择备份文件</Button>
            </Upload>
          }
        >
          <Alert
            message="注意事项"
            description="恢复操作会覆盖现有数据，请谨慎操作。建议在恢复前先创建当前数据的备份。"
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
          />

          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <div>
              <Text strong>恢复操作说明：</Text>
              <ul>
                <li>
                  点击"选择备份文件"按钮上传之前下载的JSON备份文件
                </li>
                <li>上传成功后会显示恢复选项对话框</li>
                <li>可选择恢复哪些数据（团队、架构、项目）</li>
                <li>恢复操作不可逆，请确认无误后执行</li>
              </ul>
            </div>

            {restoreResult && (
              <Alert
                message="恢复结果"
                description={
                  <Descriptions column={1} size="small">
                    <Descriptions.Item label="团队数据">
                      {restoreResult.team}
                    </Descriptions.Item>
                    <Descriptions.Item label="架构数据">
                      {restoreResult.architecture}
                    </Descriptions.Item>
                    <Descriptions.Item label="项目数据">
                      {restoreResult.project}
                    </Descriptions.Item>
                    {restoreResult.errors.length > 0 && (
                      <Descriptions.Item label="错误信息">
                        {restoreResult.errors.map((error, index) => (
                          <div key={index} style={{ color: 'red' }}>
                            {error}
                          </div>
                        ))}
                      </Descriptions.Item>
                    )}
                  </Descriptions>
                }
                type={
                  restoreResult.errors.length > 0 ? 'warning' : 'success'
                }
              />
            )}
          </Space>
        </Card>
      </Space>

      {/* Restore Options Modal */}
      <Modal
        title="选择恢复选项"
        open={restoreModalVisible}
        onOk={() => handleRestore(undefined)}
        onCancel={() => setRestoreModalVisible(false)}
        confirmLoading={restoreLoading}
        okText="确认恢复"
        cancelText="取消"
      >
        <Spin spinning={restoreLoading}>
          <Form layout="vertical">
            <Form.Item
              name="restoreOptions"
              label="请选择要恢复的数据类型"
              initialValue={{
                team: true,
                architecture: true,
                project: true,
              }}
            >
              <Checkbox.Group>
                <Space direction="vertical">
                  <Checkbox value="team">团队数据（人员、小组、责任田）</Checkbox>
                  <Checkbox value="architecture">
                    架构数据（模块、功能、数据流）
                  </Checkbox>
                  <Checkbox value="project">
                    项目数据（版本、迭代、任务）
                  </Checkbox>
                </Space>
              </Checkbox.Group>
            </Form.Item>

            <Alert
              message="警告"
              description="恢复操作将覆盖现有数据，此操作不可撤销。请确保您已做好必要的准备。"
              type="error"
              showIcon
            />
          </Form>
        </Spin>
      </Modal>
    </div>
  );
};

export default BackupPage;
