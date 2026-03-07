"""add nhiem_vu table

Revision ID: a1b2c3d4e5f6
Revises: ee6bf6dc5a65
Create Date: 2026-03-08 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'ee6bf6dc5a65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'nhiem_vu',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tieu_de', sa.String(200), nullable=False),
        sa.Column('mo_ta', sa.Text(), nullable=True),
        sa.Column('nguoi_giao_id', sa.UUID(), nullable=False),
        sa.Column('nguoi_nhan_id', sa.UUID(), nullable=False),
        sa.Column('ngay_giao', sa.Date(), nullable=False),
        sa.Column('han_hoan_thanh', sa.Date(), nullable=False),
        sa.Column('ngay_hoan_thanh_thuc_te', sa.Date(), nullable=True),
        sa.Column('trang_thai', sa.String(30), nullable=False,
                  server_default='CHUA_BAT_DAU'),
        sa.Column('muc_do_uu_tien', sa.String(20), nullable=False,
                  server_default='TRUNG_BINH'),
        sa.Column('ho_so_id', sa.UUID(), nullable=True),
        sa.Column('ket_qua', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['nguoi_giao_id'], ['nguoi_dung.id']),
        sa.ForeignKeyConstraint(['nguoi_nhan_id'], ['nguoi_dung.id']),
        sa.ForeignKeyConstraint(['ho_so_id'], ['ho_so.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_nhiem_vu_nguoi_nhan_id', 'nhiem_vu', ['nguoi_nhan_id'])
    op.create_index('ix_nhiem_vu_nguoi_giao_id', 'nhiem_vu', ['nguoi_giao_id'])
    op.create_index('ix_nhiem_vu_trang_thai', 'nhiem_vu', ['trang_thai'])


def downgrade() -> None:
    op.drop_index('ix_nhiem_vu_trang_thai', 'nhiem_vu')
    op.drop_index('ix_nhiem_vu_nguoi_nhan_id', 'nhiem_vu')
    op.drop_index('ix_nhiem_vu_nguoi_giao_id', 'nhiem_vu')
    op.drop_table('nhiem_vu')
