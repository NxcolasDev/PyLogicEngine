"""Cria tabelas de usuário e eventos com índices para filtros analíticos."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Callback Alembic cria tabelas/índices para autenticação, JOIN e agregação."""

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_created_at", "users", ["created_at"], unique=False)
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"], unique=False)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_events_created_at", "events", ["created_at"], unique=False)
    op.create_index("ix_events_id", "events", ["id"], unique=False)
    op.create_index("ix_events_severity", "events", ["severity"], unique=False)
    op.create_index("ix_events_user_created_at", "events", ["user_id", "created_at"], unique=False)
    op.create_index("ix_events_user_id", "events", ["user_id"], unique=False)


def downgrade() -> None:
    """Callback Alembic remove índices e tabelas na ordem inversa."""

    op.drop_index("ix_events_user_id", table_name="events")
    op.drop_index("ix_events_user_created_at", table_name="events")
    op.drop_index("ix_events_severity", table_name="events")
    op.drop_index("ix_events_id", table_name="events")
    op.drop_index("ix_events_created_at", table_name="events")
    op.drop_table("events")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_created_at", table_name="users")
    op.drop_table("users")
