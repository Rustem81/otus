---
inclusion: fileMatch
fileMatchPattern: "backend/alembic/**,backend/app/models/**,**/schema*,**/migration*"
---

# Правила работы с базой данных и миграциями

## SQLAlchemy 2 (async)

### Правило D1: Модели — декларативный стиль с mapped_column

```python
from __future__ import annotations
from sqlalchemy import String, Numeric, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from decimal import Decimal
import enum

class Base(DeclarativeBase):
    pass

class Direction(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class Advertisement(Base):
    __tablename__ = "advertisements"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    external_id: Mapped[str] = mapped_column(String, unique=True, comment="ID объявления на MEXC")
    price: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    volume: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    min_limit: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    max_limit: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    direction: Mapped[Direction] = mapped_column(String(4))
    currency: Mapped[str] = mapped_column(String(10))
    payment_methods: Mapped[list[str]] = mapped_column(ARRAY(String))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"))
    merchant: Mapped[Merchant] = relationship(back_populates="advertisements")

    __table_args__ = (
        Index("ix_ads_currency_direction_active", "currency", "direction", "is_active"),
        Index("ix_ads_fetched_at", "fetched_at"),
    )
```

### Правило D2: Async-сессии

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### Правило D3: Индексы обязательны

Каждая таблица должна иметь индексы для полей, по которым идёт фильтрация и сортировка. Составные индексы для частых комбинаций фильтров.

## Alembic — миграции

### Правило D4: Версионированные миграции

- Каждое изменение схемы — через Alembic миграцию, никогда вручную
- Имя миграции — описательное: `alembic revision --autogenerate -m "add_risk_score_to_advertisements"`
- Каждая миграция содержит `upgrade()` и `downgrade()`
- Перед коммитом: проверь что `downgrade()` работает корректно

### Правило D5: Структура Alembic

```
backend/
├── alembic/
│   ├── versions/
│   │   ├── 001_initial_schema.py
│   │   ├── 002_add_risk_score.py
│   │   └── ...
│   ├── env.py                  # async-совместимый env.py
│   └── script.py.mako
├── alembic.ini
```

### Правило D6: Async env.py для Alembic

```python
# alembic/env.py
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import get_settings
from app.models import Base  # импорт всех моделей

settings = get_settings()

def run_migrations_online():
    connectable = create_async_engine(settings.DATABASE_URL)

    async def do_run():
        async with connectable.connect() as connection:
            await connection.run_sync(do_migrations)

    import asyncio
    asyncio.run(do_run())

def do_migrations(connection):
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()
```

### Правило D7: Запрещено

- НЕ используй `db.execute(text("SELECT ..."))` для бизнес-логики — только SQLAlchemy ORM/Core
- НЕ удаляй миграции из `versions/` — только добавляй новые
- НЕ меняй существующие миграции после того, как они применены
- НЕ используй `drop_column` / `drop_table` без `downgrade()` с восстановлением
