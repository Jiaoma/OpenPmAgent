# OpenPmAgent 技术规格说明书

> **目标读者**: AI开发代理与开发团队
> **文档版本**: v1.0
> **创建日期**: 2026-02-23

---

## 1. 项目概述

### 1.1 项目定位
OpenPmAgent是一个面向企业中层管理者的项目管理和团队管理平台，支持同时管理20+人并划分为多个小组的场景。

### 1.2 核心约束
- **LLM支持**: 支持三种模式运行
  - 有LLM API接入（OpenAI兼容API）
  - 仅本地LLM API接入（llama.cpp容器）
  - 无LLM API接入（部分功能自动禁用）
- **部署环境**: Docker容器内Ubuntu系统，Nginx代理
- **访问方式**: Web前端，通过 `{IP}:{PORT}/{目标PORT}` 访问

### 1.3 核心功能模块
| 模块 | 功能描述 |
|------|---------|
| **团队管理** | 人员档案、能力模型、小组管理、负载估算、可视化 |
| **技术架构档案** | 模块管理、功能管理、责任田管理、可视化编辑 |
| **项目管理** | 版本/迭代/任务管理、甘特图、任务依赖、达成统计 |
| **系统管理** | 用户认证、操作日志、权限控制 |

---

## 2. 技术栈选型

### 2.1 后端技术栈

| 组件 | 选型 | 理由 |
|------|------|------|
| **语言** | Python 3.11+ | 生态丰富，LLM集成便利，快速开发 |
| **框架** | FastAPI 0.104+ | 高性能异步、自动OpenAPI文档、类型安全 |
| **数据库ORM** | SQLAlchemy 2.0+ | 强大的ORM、异步支持、成熟稳定 |
| **数据库** | PostgreSQL 15+ | 企业级关系型数据库、JSONB支持 |
| **LLM集成** | LangChain 0.1+ | 统一接口，支持多种LLM Provider |
| **任务队列** | Celery + Redis | 异步任务处理、定时任务 |
| **认证** | JWT + OAuth2 | 无状态认证、灵活扩展 |
| **文档导出** | python-docx, openpyxl | Office文档导出 |

### 2.2 前端技术栈

| 组件 | 选型 | 理由 |
|------|------|------|
| **框架** | React 18+ | 组件化、生态完善、TypeScript支持 |
| **语言** | TypeScript 5.0+ | 类型安全、大型项目友好 |
| **构建工具** | Vite 5.0+ | 快速构建、HMR |
| **UI框架** | Ant Design 5.0+ | 企业级UI组件、完善 |
| **状态管理** | Zustand 4.0+ | 轻量级、TypeScript友好 |
| **数据请求** | TanStack Query (React Query) | 缓存、同步、类型安全 |
| **图表可视化** | ECharts 5.4+ | 强大图表能力、支持Graph、Gantt |
| **拖拽编辑** | DnD Kit 6.0+ | 现代拖拽库、无障碍支持 |
| **Mermaid图表** | mermaid | 流程图、架构图生成 |

### 2.3 部署技术栈

| 组件 | 选型 | 理由 |
|------|------|------|
| **容器化** | Docker Compose | 多服务编排、开发/生产一致 |
| **反向代理** | Nginx 1.24+ | 高性能、负载均衡、静态资源服务 |
| **进程管理** | Gunicorn + Uvicorn | 生产级WSGI服务器 |
| **日志管理** | Loguru | 结构化日志、输出友好 |

---

## 3. 系统架构设计

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户浏览器                                 │
│                    (React + TypeScript)                          │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Nginx (反向代理)                             │
│                    静态资源服务 + API转发                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌───────────────────┐          ┌───────────────────┐
│  FastAPI Backend  │          │  LLM Container    │
│   (Port: 8000)    │          │   (llama.cpp)     │
├───────────────────┤          └───────────────────┘
│  ┌─────────────┐  │
│  │   API层     │  │          ┌───────────────────┐
│  ├─────────────┤  │          │  PostgreSQL 15    │
│  │  业务逻辑层   │  │◄────────┤   (Port: 5432)    │
│  ├─────────────┤  │          └───────────────────┘
│  │   ORM层     │  │
│  ├─────────────┤  │          ┌───────────────────┐
│  │ LangChain   │  │          │     Redis         │
│  │  (LLM集成)  │  │          │   (Port: 6379)    │
│  └─────────────┘  │          └───────────────────┘
└───────────────────┘
```

### 3.2 后端目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── dependencies.py         # 依赖注入
│   │
│   ├── api/                    # API路由层
│   │   ├── __init__.py
│   │   ├── deps.py            # 路由依赖
│   │   ├── v1/                # API v1
│   │   │   ├── __init__.py
│   │   │   ├── auth.py        # 认证相关
│   │   │   ├── team.py        # 团队管理
│   │   │   ├── architecture.py # 技术架构
│   │   │   ├── project.py     # 项目管理
│   │   │   ├── report.py      # 报表导出
│   │   │   └── audit.py       # 操作日志
│   │
│   ├── core/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── security.py        # JWT/OAuth2
│   │   ├── llm.py             # LLM集成
│   │   └── utils.py           # 工具函数
│   │
│   ├── models/                 # SQLAlchemy模型
│   │   ├── __init__.py
│   │   ├── base.py            # 基类
│   │   ├── user.py            # 用户模型
│   │   ├── team.py            # 团队模型
│   │   ├── architecture.py    # 架构模型
│   │   ├── project.py         # 项目模型
│   │   └── audit.py           # 审计模型
│   │
│   ├── schemas/                # Pydantic模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── team.py
│   │   ├── architecture.py
│   │   ├── project.py
│   │   └── common.py          # 通用模型
│   │
│   ├── services/               # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── team_service.py
│   │   ├── architecture_service.py
│   │   ├── project_service.py
│   │   └── llm_service.py
│   │
│   ├── tasks/                  # Celery任务
│   │   ├── __init__.py
│   │   └── celery_app.py
│   │
│   └── utils/                  # 工具模块
│       ├── __init__.py
│       ├── mermaid.py         # Mermaid图表生成
│       ├── export.py          # Excel/Word导出
│       └── validators.py       # 自定义验证器
│
├── tests/                      # 测试
│   ├── __init__.py
│   ├── conftest.py
│   ├── api/
│   ├── services/
│   └── models/
│
├── alembic/                    # 数据库迁移
│
├── scripts/                    # 部署脚本
│   ├── deploy.sh
│   └── init_db.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
└── .env.example
```

### 3.3 前端目录结构

```
frontend/
├── src/
│   ├── main.tsx                # 入口文件
│   ├── App.tsx                 # 根组件
│   ├── vite-env.d.ts
│   │
│   ├── api/                    # API客户端
│   │   ├── client.ts           # Axios实例配置
│   │   ├── auth.ts
│   │   ├── team.ts
│   │   ├── architecture.ts
│   │   ├── project.ts
│   │   └── report.ts
│   │
│   ├── components/             # 通用组件
│   │   ├── Layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── index.tsx
│   │   ├── Chart/
│   │   │   ├── RadarChart.tsx
│   │   │   ├── LineChart.tsx
│   │   │   └── index.ts
│   │   ├── GraphView/
│   │   │   ├── GraphEditor.tsx
│   │   │   ├── GraphRenderer.tsx
│   │   │   └── index.ts
│   │   ├── DragDrop/
│   │   │   ├── DraggableBlock.tsx
│   │   │   ├── DropZone.tsx
│   │   │   └── index.ts
│   │   └── Common/
│   │       ├── Modal.tsx
│   │       ├── Table.tsx
│   │       └── Form.tsx
│   │
│   ├── pages/                  # 页面组件
│   │   ├── Login/
│   │   │   ├── index.tsx
│   │   │   └── AdminLogin.tsx
│   │   ├── Team/
│   │   │   ├── PersonList.tsx
│   │   │   ├── GroupList.tsx
│   │   │   ├── WorkloadView.tsx
│   │   │   ├── CapabilityRadar.tsx
│   │   │   └── index.tsx
│   │   ├── Architecture/
│   │   │   ├── ModuleEditor.tsx
│   │   │   ├── FunctionEditor.tsx
│   │   │   ├── ResponsibilityEditor.tsx
│   │   │   └── index.tsx
│   │   ├── Project/
│   │   │   ├── VersionList.tsx
│   │   │   ├── IterationList.tsx
│   │   │   ├── TaskList.tsx
│   │   │   ├── GanttChart.tsx
│   │   │   ├── TaskGraph.tsx
│   │   │   └── index.tsx
│   │   ├── Report/
│   │   │   ├── TaskAchievement.tsx
│   │   │   └── index.tsx
│   │   └── Audit/
│   │       ├── AuditLog.tsx
│   │       └── index.tsx
│   │
│   ├── stores/                 # 状态管理
│   │   ├── authStore.ts
│   │   ├── teamStore.ts
│   │   ├── projectStore.ts
│   │   └── index.ts
│   │
│   ├── hooks/                  # 自定义Hook
│   │   ├── useAuth.ts
│   │   ├── useTeamData.ts
│   │   ├── useProjectData.ts
│   │   └── index.ts
│   │
│   ├── types/                  # TypeScript类型
│   │   ├── api.d.ts
│   │   ├── models.d.ts
│   │   └── index.d.ts
│   │
│   ├── utils/                  # 工具函数
│   │   ├── mermaid.ts
│   │   ├── date.ts
│   │   └── index.ts
│   │
│   ├── styles/                 # 样式
│   │   ├── globals.css
│   │   └── variables.css
│   │
│   └── assets/                 # 静态资源
│
├── tests/                      # 测试
│   ├── setup.ts
│   ├── components/
│   └── pages/
│
├── Dockerfile
├── nginx.conf
├── package.json
├── tsconfig.json
├── vite.config.ts
└── .env.example
```

---

## 4. 数据模型设计

### 4.1 核心ER图

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│    User     │         │   Person    │         │   Group     │
├─────────────┤         ├─────────────┤         ├─────────────┤
│ id          │1       1│ id          │N     N  │ id          │
│ emp_id      │         │ name        │         │ name        │
│ is_admin    │         │ emp_id      │         │ leader_id   │
│ password    │         │ email       │         │ leader_id   │
└─────────────┘         │ group_id    │         └─────────────┘
                        │ capability  │                │
                        │ responsibility│◄─────────────┘
                        │ role        │                │
                        └─────────────┘                │
                               │                        │
                               │                        │
                               ▼                        ▼
                        ┌─────────────┐         ┌─────────────┐
                        │  Capability │         │   Task      │
                        ├─────────────┤         ├─────────────┤
                        │ id          │N       1│ id          │
                        │ person_id   │         │ name        │
                        │ dimension   │         │ start_date  │
                        │ level       │         │ end_date    │
                        └─────────────┘         │ man_months  │
                                                │ status      │
                               ◄────────────────│ iteration_id│
                               │                └─────────────┘
                               │                        │
                               │                        │
                               ▼                        ▼
                        ┌─────────────┐         ┌─────────────┐
                        │ Responsibility│       │  Iteration  │
                        ├─────────────┤         ├─────────────┤
                        │ id          │         │ id          │
                        │ name        │         │ name        │
                        │ group_id    │         │ version_id  │
                        │ owner_id    │         │ start_date  │
                        │ backup_id   │         │ end_date    │
                        └─────────────┘         └─────────────┘
                                                        │
                                                        │
                               ◄────────────────────────┘
                               │
                               ▼
                        ┌─────────────┐
                        │   Version   │
                        ├─────────────┤
                        │ id          │
                        │ name        │
                        │ pm_name     │
                        │ sm_name     │
                        │ tm_name     │
                        └─────────────┘
```

### 4.2 详细数据模型

#### User（用户表）

```python
class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    emp_id: str = Column(String(50), unique=True, index=True, nullable=False)
    is_admin: bool = Column(Boolean, default=False, nullable=False)
    password_hash: Optional[str] = Column(String(255), nullable=True)

    # Relations
    person: Optional["Person"] = relationship("Person", back_populates="user", uselist=False)
    audit_logs: List["AuditLog"] = relationship("AuditLog", back_populates="user")
```

#### Person（人员档案表）

```python
class Person(Base):
    __tablename__ = "persons"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(100), nullable=False)
    emp_id: str = Column(String(50), unique=True, index=True, nullable=False)
    email: str = Column(String(255), nullable=False)
    group_id: Optional[int] = Column(Integer, ForeignKey("groups.id"), nullable=True)
    role: str = Column(String(100), nullable=False)

    # Relations
    user: Optional["User"] = relationship("User", back_populates="person")
    group: Optional["Group"] = relationship("Group", back_populates="members")
    capabilities: List["Capability"] = relationship("Capability", back_populates="person", cascade="all, delete-orphan")
    responsibilities: List["Responsibility"] = relationship("Responsibility", foreign_keys="Responsibility.owner_id")
    backup_responsibilities: List["Responsibility"] = relationship("Responsibility", foreign_keys="Responsibility.backup_id")
    assigned_tasks: List["Task"] = relationship("Task", secondary="task_assignees")
    dev_tasks: List["Task"] = relationship("Task", foreign_keys="Task.developer_id")
    test_tasks: List["Task"] = relationship("Task", foreign_keys="Task.tester_id")
```

#### Capability（能力模型表）

```python
class Capability(Base):
    __tablename__ = "capabilities"

    id: int = Column(Integer, primary_key=True, index=True)
    person_id: int = Column(Integer, ForeignKey("persons.id"), nullable=False)
    dimension: str = Column(String(100), nullable=False)
    level: int = Column(Integer, nullable=False)  # 1-5

    # Relations
    person: "Person" = relationship("Person", back_populates="capabilities")
```

#### CapabilityDimension（能力维度定义表）

```python
class CapabilityDimension(Base):
    __tablename__ = "capability_dimensions"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(100), unique=True, nullable=False)
    description: str = Column(String(500), nullable=True)
    is_active: bool = Column(Boolean, default=True, nullable=False)
```

#### Group（小组表）

```python
class Group(Base):
    __tablename__ = "groups"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(100), unique=True, nullable=False)
    leader_id: int = Column(Integer, ForeignKey("persons.id"), nullable=False)

    # Relations
    leader: "Person" = relationship("Person", foreign_keys=[leader_id])
    members: List["Person"] = relationship("Person", back_populates="group")
    responsibilities: List["Responsibility"] = relationship("Responsibility", back_populates="group")
    key_figures: List["KeyFigure"] = relationship("KeyFigure", back_populates="group", cascade="all, delete-orphan")
```

#### KeyFigure（关键人物表）

```python
class KeyFigure(Base):
    __tablename__ = "key_figures"

    id: int = Column(Integer, primary_key=True, index=True)
    group_id: int = Column(Integer, ForeignKey("groups.id"), nullable=False)
    type: str = Column(String(50), nullable=False)  # PL, MDE, etc.
    person_id: int = Column(Integer, ForeignKey("persons.id"), nullable=False)

    # Relations
    group: "Group" = relationship("Group", back_populates="key_figures")
    person: "Person" = relationship("Person")
```

#### Responsibility（责任田表）

```python
class Responsibility(Base):
    __tablename__ = "responsibilities"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(200), nullable=False)
    group_id: int = Column(Integer, ForeignKey("groups.id"), nullable=False)
    owner_id: int = Column(Integer, ForeignKey("persons.id"), nullable=False)
    backup_id: int = Column(Integer, ForeignKey("persons.id"), nullable=True)
    current_year_tasks: List[int] = Column(JSONB, nullable=True)  # 存储任务ID列表

    # Relations
    group: "Group" = relationship("Group", back_populates="responsibilities")
    owner: "Person" = relationship("Person", foreign_keys=[owner_id])
    backup: Optional["Person"] = relationship("Person", foreign_keys=[backup_id])
    functions: List["Function"] = relationship("Function", back_populates="responsibility")
```

#### Module（模块表）

```python
class Module(Base):
    __tablename__ = "modules"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(200), nullable=False)
    parent_id: Optional[int] = Column(Integer, ForeignKey("modules.id"), nullable=True)

    # Relations
    parent: Optional["Module"] = relationship("Module", remote_side=[id], back_populates="children")
    children: List["Module"] = relationship("Module", back_populates="parent", cascade="all, delete-orphan")
    functions: List["Function"] = relationship("FunctionModule", back_populates="module")
```

#### Function（功能表）

```python
class Function(Base):
    __tablename__ = "functions"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(200), nullable=False)
    parent_id: Optional[int] = Column(Integer, ForeignKey("functions.id"), nullable=True)
    responsibility_id: Optional[int] = Column(Integer, ForeignKey("responsibilities.id"), nullable=True)

    # Relations
    parent: Optional["Function"] = relationship("Function", remote_side=[id], back_populates="children")
    children: List["Function"] = relationship("Function", back_populates="parent", cascade="all, delete-orphan")
    responsibility: Optional["Responsibility"] = relationship("Responsibility", back_populates="functions")
    modules: List["FunctionModule"] = relationship("FunctionModule", back_populates="function")
    data_flows: List["DataFlow"] = relationship("DataFlow", foreign_keys="DataFlow.source_function_id")
    target_flows: List["DataFlow"] = relationship("DataFlow", foreign_keys="DataFlow.target_function_id")
```

#### FunctionModule（功能-模块关联表）

```python
class FunctionModule(Base):
    __tablename__ = "function_modules"

    id: int = Column(Integer, primary_key=True, index=True)
    function_id: int = Column(Integer, ForeignKey("functions.id"), nullable=False)
    module_id: int = Column(Integer, ForeignKey("modules.id"), nullable=False)
    order: int = Column(Integer, default=0, nullable=False)

    # Relations
    function: "Function" = relationship("Function", back_populates="modules")
    module: "Module" = relationship("Module", back_populates="functions")
```

#### DataFlow（数据流表）

```python
class DataFlow(Base):
    __tablename__ = "data_flows"

    id: int = Column(Integer, primary_key=True, index=True)
    source_function_id: int = Column(Integer, ForeignKey("functions.id"), nullable=False)
    target_function_id: int = Column(Integer, ForeignKey("functions.id"), nullable=False)
    order: int = Column(Integer, default=0, nullable=False)
    description: Optional[str] = Column(String(500), nullable=True)

    # Relations
    source_function: "Function" = relationship("Function", foreign_keys=[source_function_id])
    target_function: "Function" = relationship("Function", foreign_keys=[target_function_id])
```

#### Version（版本表）

```python
class Version(Base):
    __tablename__ = "versions"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(100), nullable=False)
    pm_name: str = Column(String(100), nullable=False)  # 项目经理
    sm_name: str = Column(String(100), nullable=False)  # 软件经理
    tm_name: str = Column(String(100), nullable=False)  # 测试经理

    # Relations
    iterations: List["Iteration"] = relationship("Iteration", back_populates="version", cascade="all, delete-orphan")
```

#### Iteration（迭代表）

```python
class Iteration(Base):
    __tablename__ = "iterations"

    id: int = Column(Integer, primary_key=True, index=True)
    version_id: int = Column(Integer, ForeignKey("versions.id"), nullable=False)
    name: str = Column(String(100), nullable=False)
    start_date: date = Column(Date, nullable=False)
    end_date: date = Column(Date, nullable=False)
    estimated_man_months: float = Column(Float, default=0.0)

    # Relations
    version: "Version" = relationship("Version", back_populates="iterations")
    tasks: List["Task"] = relationship("Task", back_populates="iteration")
```

#### Task（任务表）

```python
class Task(Base):
    __tablename__ = "tasks"

    id: int = Column(Integer, primary_key=True, index=True)
    iteration_id: int = Column(Integer, ForeignKey("iterations.id"), nullable=False)
    name: str = Column(String(200), nullable=False)
    start_date: date = Column(Date, nullable=False)
    end_date: date = Column(Date, nullable=False)
    man_months: float = Column(Float, nullable=False)
    status: str = Column(String(50), default="pending")  # pending, in_progress, completed

    # 关键角色
    delivery_owner_id: int = Column(Integer, ForeignKey("persons.id"), nullable=False)
    developer_id: int = Column(Integer, ForeignKey("persons.id"), nullable=False)
    tester_id: int = Column(Integer, ForeignKey("persons.id"), nullable=False)

    # 文档
    design_doc_url: Optional[str] = Column(String(500), nullable=True)

    # Relations
    iteration: "Iteration" = relationship("Iteration", back_populates="tasks")
    delivery_owner: "Person" = relationship("Person", foreign_keys=[delivery_owner_id])
    developer: "Person" = relationship("Person", foreign_keys=[developer_id])
    tester: "Person" = relationship("Person", foreign_keys=[tester_id])
    assignees: List["Person"] = relationship("Person", secondary="task_assignees")

    # 依赖和关联
    dependencies: List["TaskDependency"] = relationship("TaskDependency", foreign_keys="TaskDependency.task_id")
    dependents: List["TaskDependency"] = relationship("TaskDependency", foreign_keys="TaskDependency.depends_on_id")
    relations: List["TaskRelation"] = relationship("TaskRelation", foreign_keys="TaskRelation.task_id")
    related_tasks: List["TaskRelation"] = relationship("TaskRelation", foreign_keys="TaskRelation.related_task_id")

    # 完成记录
    completion: Optional["TaskCompletion"] = relationship("TaskCompletion", back_populates="task", uselist=False)
```

#### TaskAssignee（任务分配表）

```python
class TaskAssignee(Base):
    __tablename__ = "task_assignees"

    task_id: int = Column(Integer, ForeignKey("tasks.id"), primary_key=True)
    person_id: int = Column(Integer, ForeignKey("persons.id"), primary_key=True)
```

#### TaskDependency（任务依赖表）

```python
class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    id: int = Column(Integer, primary_key=True, index=True)
    task_id: int = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    depends_on_id: int = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    type: str = Column(String(50), default="finish_to_start")  # finish_to_start, start_to_start, etc.
```

#### TaskRelation（任务关联表）

```python
class TaskRelation(Base):
    __tablename__ = "task_relations"

    id: int = Column(Integer, primary_key=True, index=True)
    task_id: int = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    related_task_id: int = Column(Integer, ForeignKey("tasks.id"), nullable=False)
```

#### TaskCompletion（任务完成记录表）

```python
class TaskCompletion(Base):
    __tablename__ = "task_completions"

    id: int = Column(Integer, primary_key=True, index=True)
    task_id: int = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    actual_end_date: datetime = Column(DateTime, nullable=False)
    completion_status: str = Column(String(50), nullable=False)  # early, on_time, slightly_late, severely_late
```

#### AuditLog（操作日志表）

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    action: str = Column(String(100), nullable=False)  # create, update, delete
    resource_type: str = Column(String(100), nullable=False)  # person, group, task, etc.
    resource_id: int = Column(Integer, nullable=False)
    changes: Optional[dict] = Column(JSONB, nullable=True)
    timestamp: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    status: str = Column(String(50), default="success")  # success, failure

    # Relations
    user: "User" = relationship("User", back_populates="audit_logs")
```

---

## 5. API接口设计

### 5.1 API设计原则
- RESTful风格
- 统一响应格式
- 分页支持
- 权限控制（Admin权限、普通用户只读）
- 操作日志记录

### 5.2 通用响应格式

```python
# 成功响应
{
    "code": 200,
    "message": "success",
    "data": {...}
}

# 分页响应
{
    "code": 200,
    "message": "success",
    "data": {
        "items": [...],
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5
    }
}

# 错误响应
{
    "code": 400,
    "message": "validation error",
    "errors": [...]
}
```

### 5.3 API路由清单

#### 认证相关 (`/api/v1/auth`)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/login/admin` | Admin用户登录 | 公开 |
| POST | `/login/user` | 普通用户登录（工号） | 公开 |
| POST | `/logout` | 登出 | 认证用户 |
| GET | `/me` | 获取当前用户信息 | 认证用户 |

#### 团队管理 (`/api/v1/team`)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| **人员管理** | | | |
| GET | `/persons` | 获取人员列表 | 认证 |
| POST | `/persons` | 创建人员 | Admin |
| GET | `/persons/{id}` | 获取人员详情 | 认证 |
| PUT | `/persons/{id}` | 更新人员 | Admin |
| DELETE | `/persons/{id}` | 删除人员 | Admin |
| | | | |
| **能力模型** | | | |
| GET | `/capability-dimensions` | 获取能力维度列表 | 认证 |
| POST | `/capability-dimensions` | 创建能力维度 | Admin |
| PUT | `/capability-dimensions/{id}` | 更新能力维度 | Admin |
| DELETE | `/capability-dimensions/{id}` | 删除能力维度 | Admin |
| GET | `/persons/{id}/capabilities` | 获取人员能力模型 | 认证 |
| PUT | `/persons/{id}/capabilities` | 更新人员能力模型 | Admin |
| | | | |
| **小组管理** | | | |
| GET | `/groups` | 获取小组列表 | 认证 |
| POST | `/groups` | 创建小组 | Admin |
| GET | `/groups/{id}` | 获取小组详情 | 认证 |
| PUT | `/groups/{id}` | 更新小组 | Admin |
| DELETE | `/groups/{id}` | 删除小组 | Admin |
| POST | `/groups/{id}/key-figures` | 添加关键人物 | Admin |
| DELETE | `/groups/{id}/key-figures/{kf_id}` | 删除关键人物 | Admin |
| | | | |
| **责任田管理** | | | |
| GET | `/responsibilities` | 获取责任田列表 | 认证 |
| POST | `/responsibilities` | 创建责任田 | Admin |
| PUT | `/responsibilities/{id}` | 更新责任田 | Admin |
| DELETE | `/responsibilities/{id}` | 删除责任田 | Admin |
| | | | |
| **负载分析** | | | |
| GET | `/workload/person/{id}` | 获取个人任务负载 | 认证 |
| GET | `/workload/group/{id}` | 获取小组任务负载 | 认证 |
| GET | `/workload/group/{id}/forecast` | 获取小组3个月负载预测 | 认证 |
| GET | `/workload/monthly-summary` | 获取月度负载统计 | 认证 |
| GET | `/graph/team-structure` | 获取团队结构图数据 | 认证 |
| GET | `/radar/capability/person/{id}` | 获取个人能力雷达图数据 | 认证 |
| GET | `/radar/capability/group/{id}` | 获取小组能力雷达图数据 | 认证 |

#### 技术架构 (`/api/v1/architecture`)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| **模块管理** | | | |
| GET | `/modules` | 获取模块树 | 认证 |
| POST | `/modules` | 创建模块 | Admin |
| PUT | `/modules/{id}` | 更新模块 | Admin |
| DELETE | `/modules/{id}` | 删除模块 | Admin |
| POST | `/modules/{id}/move` | 移动模块（拖拽） | Admin |
| GET | `/modules/mermaid` | 导出模块Mermaid图 | 认证 |
| | | | |
| **功能管理** | | | |
| GET | `/functions` | 获取功能树 | 认证 |
| POST | `/functions` | 创建功能 | Admin |
| PUT | `/functions/{id}` | 更新功能 | Admin |
| DELETE | `/functions/{id}` | 删除功能 | Admin |
| POST | `/functions/{id}/move` | 移动功能（拖拽） | Admin |
| GET | `/functions/{id}/modules` | 获取功能关联模块 | 认证 |
| POST | `/functions/{id}/modules` | 更新功能关联模块 | Admin |
| GET | `/functions/{id}/data-flows` | 获取功能数据流 | 认证 |
| POST | `/functions/{id}/data-flows` | 更新功能数据流 | Admin |
| GET | `/functions/mermaid` | 导出功能Mermaid图 | 认证 |
| | | | |
| **架构关联** | | | |
| GET | `/relations/responsibility-functions` | 获取责任田-功能关联图 | 认证 |

#### 项目管理 (`/api/v1/project`)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| **版本管理** | | | |
| GET | `/versions` | 获取版本列表 | 认证 |
| POST | `/versions` | 创建版本 | Admin |
| GET | `/versions/{id}` | 获取版本详情 | 认证 |
| PUT | `/versions/{id}` | 更新版本 | Admin |
| DELETE | `/versions/{id}` | 删除版本 | Admin |
| | | | |
| **迭代管理** | | | |
| GET | `/iterations` | 获取迭代列表 | 认证 |
| POST | `/iterations` | 创建迭代 | Admin |
| GET | `/iterations/{id}` | 获取迭代详情 | 认证 |
| PUT | `/iterations/{id}` | 更新迭代 | Admin |
| DELETE | `/iterations/{id}` | 删除迭代 | Admin |
| POST | `/iterations/{id}/check-conflicts` | 检查迭代冲突 | Admin |
| | | | |
| **任务管理** | | | |
| GET | `/tasks` | 获取任务列表 | 认证 |
| POST | `/tasks` | 创建任务 | Admin |
| GET | `/tasks/{id}` | 获取任务详情 | 认证 |
| PUT | `/tasks/{id}` | 更新任务 | Admin |
| DELETE | `/tasks/{id}` | 删除任务 | Admin |
| POST | `/tasks/{id}/dependencies` | 添加任务依赖 | Admin |
| DELETE | `/tasks/{id}/dependencies/{dep_id}` | 删除任务依赖 | Admin |
| POST | `/tasks/{id}/relations` | 添加任务关联 | Admin |
| DELETE | `/tasks/{id}/relations/{rel_id}` | 删除任务关联 | Admin |
| POST | `/tasks/{id}/check-conflicts` | 检查任务冲突 | Admin |
| POST | `/tasks/{id}/complete` | 标记任务完成 | Admin |
| | | | |
| **任务图分析** | | | |
| GET | `/tasks/graph` | 获取任务依赖图数据 | 认证 |
| GET | `/tasks/longest-path` | 获取最长路径 | 认证 |
| GET | `/tasks/highest-load` | 获取负载最高人员 | 认证 |
| GET | `/gantt` | 获取甘特图数据 | 认证 |
| GET | `/gantt/mermaid` | 导出甘特图Mermaid | 认证 |
| | | | |
| **任务达成统计** | | | |
| GET | `/achievement` | 获取任务达成统计 | 认证 |
| GET | `/achievement/export` | 导出任务达成Excel | 认证 |

#### 报表导出 (`/api/v1/report`)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/export/mermaid` | 导出Mermaid图表为Markdown | 认证 |
| POST | `/export/excel` | 导出数据为Excel | 认证 |
| POST | `/export/word` | 导出报告为Word | 认证 |

#### 操作日志 (`/api/v1/audit`)

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/logs` | 获取操作日志列表 | Admin |
| GET | `/logs/{id}` | 获取操作日志详情 | Admin |

---

## 6. 前端架构设计

### 6.1 路由设计

```typescript
const routes = [
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/login/admin',
    element: <AdminLogin />,
  },
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        path: '',
        element: <Dashboard />,
      },
      {
        path: 'team',
        children: [
          { path: 'persons', element: <PersonList /> },
          { path: 'groups', element: <GroupList /> },
          { path: 'workload', element: <WorkloadView /> },
          { path: 'capability', element: <CapabilityRadar /> },
        ],
      },
      {
        path: 'architecture',
        children: [
          { path: 'modules', element: <ModuleEditor /> },
          { path: 'functions', element: <FunctionEditor /> },
          { path: 'responsibilities', element: <ResponsibilityEditor /> },
        ],
      },
      {
        path: 'project',
        children: [
          { path: 'versions', element: <VersionList /> },
          { path: 'iterations', element: <IterationList /> },
          { path: 'tasks', element: <TaskList /> },
          { path: 'gantt', element: <GanttChart /> },
          { path: 'graph', element: <TaskGraph /> },
        ],
      },
      {
        path: 'report',
        children: [
          { path: 'achievement', element: <TaskAchievement /> },
        ],
      },
      {
        path: 'audit',
        children: [
          { path: 'logs', element: <AuditLog /> },
        ],
      },
    ],
  },
];
```

### 6.2 状态管理架构（Zustand）

```typescript
// authStore.ts
interface AuthState {
  user: User | null;
  token: string | null;
  isAdmin: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

// teamStore.ts
interface TeamState {
  persons: Person[];
  groups: Group[];
  capabilities: Capability[];
  responsibilities: Responsibility[];
  fetchPersons: () => Promise<void>;
  fetchGroups: () => Promise<void>;
  updatePerson: (id: number, data: Partial<Person>) => Promise<void>;
  // ...
}

// projectStore.ts
interface ProjectState {
  versions: Version[];
  iterations: Iteration[];
  tasks: Task[];
  selectedVersion: Version | null;
  selectedIteration: Iteration | null;
  fetchVersions: () => Promise<void>;
  fetchIterations: (versionId: number) => Promise<void>;
  // ...
}
```

### 6.3 数据获取策略（React Query）

```typescript
// hooks/useTeamData.ts
export function usePersons() {
  return useQuery({
    queryKey: ['persons'],
    queryFn: () => api.team.getPersons(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useUpdatePerson() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Person> }) =>
      api.team.updatePerson(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['persons'] });
    },
  });
}
```

### 6.4 图表可视化策略

#### 团队结构图（GraphView）
- 使用 `@antv/g6` 或 `react-flow` 渲染关系图
- 节点类型：人员、小组、责任田
- 边类型：归属、负责、关联

#### 能力雷达图
- 使用 ECharts Radar图表
- 支持个人和小组对比

#### 任务甘特图
- 使用 ECharts Timeline或gantt库
- 显示任务时间线、依赖关系

#### 任务依赖图
- 使用 D3.js或@antv/g6
- 显示任务依赖、关联关系
- 支持最长路径高亮

### 6.5 拖拽编辑策略

#### 模块/功能编辑器
- 使用 `@dnd-kit/core` 实现拖拽
- 支持层级嵌套
- 拖拽到不同方块变为子模块/子功能
- 支持导出Mermaid

```typescript
// 拖拽示例
interface DraggableBlockProps {
  id: string;
  type: 'module' | 'function';
  data: Module | Function;
  children?: DraggableBlockProps[];
}
```

---

## 7. 部署架构设计

### 7.1 Docker Compose配置

```yaml
version: '3.8'

services:
  # PostgreSQL数据库
  postgres:
    image: postgres:15-alpine
    container_name: openpm_db
    environment:
      POSTGRES_DB: openpm
      POSTGRES_USER: openpm
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - openpm_network
    restart: unless-stopped

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: openpm_redis
    networks:
      - openpm_network
    restart: unless-stopped

  # FastAPI后端
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: openpm_backend
    environment:
      DATABASE_URL: postgresql+asyncpg://openpm:${DB_PASSWORD}@postgres:5432/openpm
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      LLM_API_URL: ${LLM_API_URL:-}
      LLM_API_KEY: ${LLM_API_KEY:-}
      LLM_TYPE: ${LLM_TYPE:-none}  # openai, local, none
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    networks:
      - openpm_network
    restart: unless-stopped
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  # Celery Worker
  celery_worker:
    build:
      context: ./backend
      docker_name: openpm_celery_worker
    environment:
      DATABASE_URL: postgresql+asyncpg://openpm:${DB_PASSWORD}@postgres:5432/openpm
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    networks:
      - openpm_network
    restart: unless-stopped
    command: celery -A app.tasks.celery_app worker --loglevel=info

  # Nginx反向代理
  nginx:
    image: nginx:1.24-alpine
    container_name: openpm_nginx
    ports:
      - "${NGINX_PORT}:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
    depends_on:
      - backend
    networks:
      - openpm_network
    restart: unless-stopped

  # LLM服务 (可选)
  llm:
    image: llama.cpp:latest
    container_name: openpm_llm
    environment:
      MODEL_PATH: /models/llama-2-7b-chat.gguf
    volumes:
      - ./models:/models
    networks:
      - openpm_network
    restart: unless-stopped
    profiles:
      - local-llm

networks:
  openpm_network:
    driver: bridge

volumes:
  postgres_data:
```

### 7.2 Nginx配置

```nginx
server {
    listen 80;
    server_name localhost;

    # 静态资源
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    # API转发
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket支持 (可选)
    location /ws/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 7.3 环境变量配置

```bash
# .env
DB_PASSWORD=your_secure_password
SECRET_KEY=your_jwt_secret_key
NGINX_PORT=8080

# LLM配置 (可选)
LLM_TYPE=openai  # openai, local, none
LLM_API_URL=https://api.openai.com/v1
LLM_API_KEY=your_openai_api_key
# 或者本地LLM
# LLM_TYPE=local
# LLM_API_URL=http://llm:8080
```

### 7.4 部署脚本

```bash
#!/bin/bash
# deploy.sh

set -e

echo "Starting OpenPmAgent deployment..."

# 1. 构建前端
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# 2. 初始化数据库
echo "Initializing database..."
cd backend
docker-compose run --rm backend alembic upgrade head
cd ..

# 3. 启动服务
echo "Starting services..."
docker-compose up -d postgres redis backend celery_worker nginx

# 4. 等待服务启动
echo "Waiting for services to be ready..."
sleep 10

# 5. 检查健康状态
echo "Checking service health..."
curl -f http://localhost:8080/api/v1/health || exit 1

echo "Deployment completed successfully!"
echo "Access the application at http://localhost:8080"
```

---

## 8. 功能模块详细规格

### 8.1 团队管理模块

#### 8.1.1 人员档案管理

**功能描述**:
- 管理人员基本信息（姓名、工号、邮件、职位）
- 关联能力模型、小组、责任田
- 管理人员任务列表

**API规格**:
```python
# schemas/team.py
class PersonBase(BaseModel):
    name: str
    emp_id: str
    email: EmailStr
    group_id: Optional[int] = None
    role: str

class PersonCreate(PersonBase):
    pass

class PersonUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    group_id: Optional[int] = None
    role: Optional[str] = None

class PersonResponse(PersonBase):
    id: int
    group: Optional[GroupResponse] = None
    capabilities: List[CapabilityResponse] = []
    responsibilities: List[ResponsibilityResponse] = []
```

**业务规则**:
- 工号全局唯一
- 删除人员前检查是否有关联数据
- Admin用户才能修改能力模型

#### 8.1.2 能力模型管理

**功能描述**:
- 定义能力维度（如：编码、架构、沟通、测试、文档）
- 为每个人员打分（1-5级）
- 可视化展示（雷达图）

**能力等级定义**:
| 等级 | 描述 |
|------|------|
| 1 | 初学者 - 需要指导 |
| 2 | 基础 - 可独立完成简单任务 |
| 3 | 中级 - 可独立完成常规任务 |
| 4 | 高级 - 可指导他人，处理复杂任务 |
| 5 | 专家 - 行业领先，可定义标准 |

#### 8.1.3 小组管理

**功能描述**:
- 管理小组信息（组名、组长、组员）
- 管理关键人物（PL、MDE等）
- 关联责任田

**业务规则**:
- 组长必须是已建档人员
- 关键人物类型可自定义（PL、MDE等）

#### 8.1.4 负载估算

**功能描述**:
- 计算个人任务负载（人月）
- 计算小组任务负载（所有成员之和）
- 生成3个月负载预测曲线
- 按负载高低排名

**负载计算公式**:
```
个人负载 = sum(任务人月数) / 任务时间跨度(月)
小组负载 = sum(所有成员负载)
```

**负载预测**:
- 基于当前任务和计划任务
- 按周/月聚合
- 生成时间序列数据

#### 8.1.5 可视化展示

**团队结构图**:
- 节点：小组、人员、责任田
- 边：归属关系、负责关系
- 点击人员查看详情

**能力雷达图**:
- 个人能力：展示各维度得分
- 小组能力：展示总能力和平均能力

### 8.2 技术架构档案模块

#### 8.2.1 模块管理

**功能描述**:
- 树状结构管理模块和子模块
- 拖拽编辑（支持嵌套、移动）
- 导出Mermaid图表

**拖拽规则**:
- 拖拽方块A到方块B → A变为B的子模块
- 支持一个方块包含多个方块
- 拖拽到空白处 → 成为顶级模块

**Mermaid导出格式**:
```mermaid
graph TD
    A[系统] --> B[用户管理]
    A --> C[订单管理]
    B --> B1[用户认证]
    B --> B2[用户信息]
    C --> C1[订单创建]
    C --> C2[订单查询]
```

#### 8.2.2 功能管理

**功能描述**:
- 树状结构管理功能和子功能
- 关联模块（多对多）
- 定义数据流（模块间交互）
- 导出Mermaid图表

**数据流表示**:
```mermaid
graph LR
    F1[功能A] -->|用户数据| M1[用户模块]
    F1 -->|订单数据| M2[订单模块]
    M1 -.数据流向.-> M2
```

#### 8.2.3 责任田管理

**功能描述**:
- 关联小组和功能
- 定义田主和后备田主
- 记录年度任务

**业务规则**:
- 田主和后备田主必须是已建档人员
- 一个责任田可包含多个功能

### 8.3 项目管理模块

#### 8.3.1 版本管理

**功能描述**:
- 定义项目版本
- 记录关键角色（项目经理、软件经理、测试经理）

**业务规则**:
- 关键角色仅记录姓名
- 版本包含多个迭代

#### 8.3.2 迭代管理

**功能描述**:
- 定义迭代时间范围
- 包含多个任务
- 统计工作量（人月）
- 检查任务冲突

**冲突检查规则**:
- 迭代终止时间早于任务终止时间 → 冲突
- 迭代起始时间晚于任务起始时间 → 冲突
- 任务可依赖更早迭代

#### 8.3.3 任务管理

**功能描述**:
- 定义任务时间、工作量
- 指定责任人（交付、开发、测试）
- 定义依赖关系（任务A依赖任务B → B必须先完成）
- 定义关联关系（任务A与任务B关联 → 同时完成）
- 标记任务完成并记录达成状态

**达成状态分类**:
| 状态 | 条件 |
|------|------|
| 提前完成 | 完成时间 < 计划终止时间 |
| 准时完成 | 完成时间 <= 计划终止时间 |
| 略微超期 | 计划终止时间 < 完成时间 <= 计划终止时间+24h |
| 严重超期 | 完成时间 > 计划终止时间+24h |

**依赖关系类型**:
- `finish_to_start`: B完成后A才能开始
- `start_to_start`: B开始后A才能开始
- `finish_to_finish`: B完成后A才能完成

**冲突检查规则**:
- 依赖任务的终止时间晚于当前任务终止时间 → 冲突
- 任务的终止时间晚于迭代的终止时间 → 冲突

#### 8.3.4 任务图分析

**功能描述**:
- 渲染任务依赖图和关联图
- 查找最长路径（关键路径）
- 查找负载最高人员

**最长路径算法**:
- 使用DAG拓扑排序
- 优先选择依赖路径最长
- 标记关键任务

**负载计算**:
- 统计每个人员的任务总人月
- 排名返回

#### 8.3.5 甘特图

**功能描述**:
- 展示任务时间线
- 显示依赖关系
- 导出Mermaid

**Mermaid格式**:
```mermaid
gantt
    title 项目计划
    dateFormat YYYY-MM-DD
    section 迭代1
    任务1 :a1, 2024-01-01, 7d
    任务2 :a2, after a1, 5d
    任务3 :a3, after a2, 3d
```

#### 8.3.6 任务达成统计

**功能描述**:
- 统计每人任务达成情况
- 按达成状态分类计数
- 导出Excel

**统计维度**:
- 版本级别
- 迭代级别
- 人员级别

**导出字段**:
- 人员工号、姓名
- 任务总数
- 达成个数、未达成个数
- 提前完成、准时完成、略微超期、严重超期个数

---

## 9. 测试策略

### 9.1 测试分层

```
┌─────────────────────────────────────────┐
│          E2E测试 (Playwright)           │
│      用户流程验证、集成测试               │
├─────────────────────────────────────────┤
│         集成测试 (pytest)               │
│      API端点测试、数据库集成              │
├─────────────────────────────────────────┤
│         单元测试 (pytest)               │
│      业务逻辑、工具函数                   │
└─────────────────────────────────────────┘
```

### 9.2 后端测试

```python
# tests/api/test_team.py
def test_create_person_as_admin(client, admin_token):
    response = client.post(
        "/api/v1/team/persons",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "张三",
            "emp_id": "E001",
            "email": "zhangsan@example.com",
            "role": "工程师"
        }
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "张三"

def test_create_person_as_user_fails(client, user_token):
    # 非Admin用户无法创建人员
    response = client.post(
        "/api/v1/team/persons",
        headers={"Authorization": f"Bearer {user_token}"},
        json={...}
    )
    assert response.status_code == 403

def test_calculate_workload(client):
    # 测试负载计算逻辑
    ...

def test_check_task_conflicts(client):
    # 测试任务冲突检测
    ...

def test_longest_path_calculation(client):
    # 测试关键路径算法
    ...
```

### 9.3 前端测试

```typescript
// tests/pages/PersonList.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import PersonList from '@/pages/Team/PersonList';

describe('PersonList', () => {
  it('renders person list', async () => {
    const queryClient = new QueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <PersonList />
      </QueryClientProvider>
    );

    expect(screen.getByText('人员列表')).toBeInTheDocument();
  });

  it('creates new person when form submitted', async () => {
    // ...
  });
});
```

### 9.4 E2E测试

```typescript
// tests/e2e/team-management.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Team Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8080');
    await page.fill('input[name="emp_id"]', 'admin');
    await page.fill('input[name="password"]', 'password');
    await page.click('button[type="submit"]');
  });

  test('create new person', async ({ page }) => {
    await page.goto('http://localhost:8080/team/persons');
    await page.click('button:has-text("新增")');
    await page.fill('input[name="name"]', '测试人员');
    await page.fill('input[name="emp_id"]', 'E999');
    await page.click('button:has-text("保存")');

    await expect(page.locator('text=测试人员')).toBeVisible();
  });

  test('view workload chart', async ({ page }) => {
    await page.goto('http://localhost:8080/team/workload');
    await expect(page.locator('.workload-chart')).toBeVisible();
  });
});
```

### 9.5 测试覆盖率目标

| 类型 | 目标覆盖率 |
|------|-----------|
| 后端单元测试 | >= 80% |
| 后端集成测试 | 覆盖所有API端点 |
| 前端单元测试 | >= 70% |
| E2E测试 | 覆盖关键用户流程 |

---

## 10. 安全与权限设计

### 10.1 权限矩阵

| 操作 | Admin | 普通用户 |
|------|-------|---------|
| 登录 | 密码认证 | 工号认证 |
| 查看数据 | 全部 | 全部（部分） |
| 创建/修改/删除 | 全部 | 无 |
| 导出数据 | 全部 | 仅自己相关 |
| 修改能力模型 | 是 | 否 |

### 10.2 认证机制

```python
# JWT Token结构
{
    "sub": "user_id",
    "emp_id": "E001",
    "is_admin": false,
    "exp": 1234567890
}

# Token刷新
- Access Token有效期: 2小时
- Refresh Token有效期: 7天
- 支持Token刷新
```

### 10.3 操作日志

```python
# 日志记录内容
{
    "user_id": 1,
    "emp_id": "E001",
    "action": "create",
    "resource_type": "person",
    "resource_id": 10,
    "changes": {
        "name": "张三",
        "emp_id": "E001"
    },
    "timestamp": "2026-02-23T10:00:00Z",
    "status": "success"
}
```

---

## 11. LLM集成策略

### 11.1 LLM支持模式

| 模式 | 配置 | 可用功能 |
|------|------|---------|
| **无LLM** | `LLM_TYPE=none` | 基础功能，AI推荐禁用 |
| **OpenAI API** | `LLM_TYPE=openai` + API Key | AI推荐、智能分析 |
| **本地LLM** | `LLM_TYPE=local` + llama.cpp | AI推荐（低延迟） |

### 11.2 LLM应用场景

1. **智能负载分配推荐**
   - 基于人员能力和当前负载
   - 推荐最佳任务分配

2. **风险预警**
   - 基于历史数据预测延期风险
   - 主动预警

3. **报表生成**
   - 自动生成项目周报/月报
   - 自然语言解释

### 11.3 LangChain集成

```python
# core/llm.py
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class LLMService:
    def __init__(self):
        self.llm = self._create_llm()

    def _create_llm(self):
        llm_type = os.getenv("LLM_TYPE", "none")
        if llm_type == "openai":
            return ChatOpenAI(
                base_url=os.getenv("LLM_API_URL"),
                api_key=os.getenv("LLM_API_KEY")
            )
        elif llm_type == "local":
            return ChatOpenAI(
                base_url=os.getenv("LLM_API_URL"),
                model="llama-2"
            )
        return None

    async def recommend_task_assignment(self, task: Task, candidates: List[Person]):
        if not self.llm:
            return None

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是项目管理专家，根据人员能力推荐任务分配。"),
            ("user", """
            任务: {task_name}
            候选人: {candidates}
            请推荐最佳人员，并给出理由。
            """)
        ])

        # ...
```

---

## 12. 已确认技术决策

### 12.1 技术选型确认
- [x] 数据库选择：**PostgreSQL 15+**
- [x] 前端框架：**React 18+ + Ant Design 5.0+ + TypeScript 5.0+**
- [x] 后端框架：**FastAPI 0.104+ (Python 3.11+)**

### 12.2 功能细节确认
- [x] 能力维度管理：**两者结合（预设默认维度作为起点，用户可修改和扩展）**
  - 预设维度：编码、架构、沟通、测试、文档
  - 用户可自定义添加新维度
  - 用户可禁用或删除不需要的维度

- [x] 任务依赖关系类型：**支持多种依赖类型**
  - finish_to_start：依赖任务完成后才能开始当前任务
  - start_to_start：依赖任务开始后才能开始当前任务
  - finish_to_finish：依赖任务完成后才能完成当前任务
  - start_to_finish：依赖任务开始后才能完成当前任务

- [x] LLM集成方式：**实时响应**
  - 所有AI推荐功能（负载分配、风险预警、报表生成）均实时返回结果
  - 通过LangChain统一接口，支持OpenAI API和本地llama.cpp

### 12.3 部署细节确认
- [x] 远程服务器访问方式：**Docker端口映射**
  - 通过Nginx暴露端口，映射到内部容器服务
  - 访问格式：`http://{SERVER_IP}:{NGINX_PORT}`
- [x] HTTPS支持：**暂时不需要**（后续可按需添加）
- [x] 多语言支持：**暂不需要**（仅支持中文）

### 12.4 额外功能确认
- [x] 数据导入：**支持从Excel/CSV导入人员、任务等基础数据**
  - 支持批量导入人员档案
  - 支持批量导入任务数据
  - 支持模板下载和数据校验

- [x] 任务模板：**支持创建任务模板**
  - 可保存任务配置为模板
  - 可从模板快速创建新任务
  - 支持模板分类管理

- [x] 数据定时备份和备份回滚：**支持**
  - 定时备份PostgreSQL数据库
  - 支持手动触发备份
  - 支持从备份文件恢复数据
  - 支持备份文件管理（查看、下载、删除）

### 12.5 未确认事项
- [ ] 历史版本查看：待确认

---

**文档结束**
