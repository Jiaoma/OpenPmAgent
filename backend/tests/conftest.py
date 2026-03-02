"""Pytest configuration and fixtures."""
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient

from app.main import app
from app.database import get_db, Base
from app.models import User
from app.core.security import get_password_hash

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_engine():
    """Create test engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, checkfirst=False)
    await engine.dispose()


@pytest_asyncio.fixture
async def db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client."""

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession) -> User:
    """Create admin user in database."""
    admin = User(
        emp_id="admin001",
        password_hash=get_password_hash("admin123"),
        is_admin=True,
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> User:
    """Create test user in database."""
    user = User(
        emp_id="user001",
        password_hash=get_password_hash("user123"),
        is_admin=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient, admin_user: User) -> AsyncGenerator[AsyncClient, None]:
    """Create an authenticated client with admin token."""
    # Login as admin
    response = await client.post(
        "/api/v1/auth/login/admin",
        json={"emp_id": "admin001", "password": "admin123"}
    )

    if response.status_code == 200:
        data = response.json()
        if "data" in data and "access_token" in data["data"]:
            token = data["data"]["access_token"]
            client.headers.update({"Authorization": f"Bearer {token}"})

    yield client


@pytest_asyncio.fixture
async def user_client(client: AsyncClient, test_user: User) -> AsyncGenerator[AsyncClient, None]:
    """Create an authenticated client with regular user token."""
    # Login as regular user
    response = await client.post(
        "/api/v1/auth/login",
        json={"emp_id": "user001", "password": "user123"}
    )

    if response.status_code == 200:
        data = response.json()
        if "data" in data and "access_token" in data["data"]:
            token = data["data"]["access_token"]
            client.headers.update({"Authorization": f"Bearer {token}"})

    yield client
