"""Initial schema — all tables for ExecutiveAI

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE userrole AS ENUM ('CEO','ADMIN','OPERATIONS_MANAGER','SALES_MANAGER','ANALYST')"
    )
    op.execute(
        "CREATE TYPE productcategory AS ENUM ('Electronics','Food','Clothing','Health','Sports')"
    )
    op.execute(
        "CREATE TYPE stockstatus AS ENUM ('normal','low','critical','overstock','out_of_stock')"
    )
    op.execute(
        "CREATE TYPE alerttype AS ENUM ('low_stock','overstock','sales_drop','revenue_target','anomaly','system')"
    )
    op.execute(
        "CREATE TYPE alertseverity AS ENUM ('info','warning','critical')"
    )
    op.execute(
        "CREATE TYPE forecasttype AS ENUM ('revenue','inventory','demand')"
    )

    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("plan", sa.String(50), default="enterprise", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"])

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", postgresql.ENUM("CEO", "ADMIN", "OPERATIONS_MANAGER",
                                          "SALES_MANAGER", "ANALYST",
                                          name="userrole", create_type=False), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("is_verified", sa.Boolean, default=False, nullable=False),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])

    op.create_table(
        "branches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("region", sa.String(100), nullable=True),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("manager_name", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_branches_tenant_id", "branches", ["tenant_id"])
    op.create_index("ix_branches_code", "branches", ["code"])

    op.create_table(
        "warehouses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("max_capacity", sa.Integer, nullable=False, default=10000),
        sa.Column("current_utilization", sa.Float, default=0.0, nullable=False),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_warehouses_tenant_id", "warehouses", ["tenant_id"])

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sku", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", postgresql.ENUM("Electronics", "Food", "Clothing", "Health", "Sports",
                                               name="productcategory", create_type=False), nullable=False),
        sa.Column("unit_price", sa.Float, nullable=False),
        sa.Column("cost_price", sa.Float, nullable=False),
        sa.Column("unit", sa.String(50), default="piece", nullable=False),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("reorder_point", sa.Integer, default=50, nullable=False),
        sa.Column("max_stock_level", sa.Integer, default=500, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_products_tenant_id", "products", ["tenant_id"])
    op.create_index("ix_products_sku", "products", ["sku"])

    op.create_table(
        "sales",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id"), nullable=False),
        sa.Column("sale_date", sa.Date, nullable=False),
        sa.Column("invoice_number", sa.String(100), nullable=False),
        sa.Column("total_amount", sa.Float, nullable=False),
        sa.Column("total_cost", sa.Float, nullable=False, default=0.0),
        sa.Column("discount_amount", sa.Float, default=0.0, nullable=False),
        sa.Column("tax_amount", sa.Float, default=0.0, nullable=False),
        sa.Column("gross_profit", sa.Float, default=0.0, nullable=False),
        sa.Column("customer_name", sa.String(255), nullable=True),
        sa.Column("payment_method", sa.String(50), default="cash", nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_sales_tenant_id", "sales", ["tenant_id"])
    op.create_index("ix_sales_branch_id", "sales", ["branch_id"])
    op.create_index("ix_sales_sale_date", "sales", ["sale_date"])
    op.create_index("ix_sales_invoice_number", "sales", ["invoice_number"])

    op.create_table(
        "sale_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sale_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("sales.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("unit_price", sa.Float, nullable=False),
        sa.Column("unit_cost", sa.Float, nullable=False, default=0.0),
        sa.Column("discount_pct", sa.Float, default=0.0, nullable=False),
        sa.Column("line_total", sa.Float, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_sale_items_sale_id", "sale_items", ["sale_id"])
    op.create_index("ix_sale_items_product_id", "sale_items", ["product_id"])
    op.create_index("ix_sale_items_tenant_id", "sale_items", ["tenant_id"])

    op.create_table(
        "inventory_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("warehouses.id"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity_on_hand", sa.Integer, nullable=False, default=0),
        sa.Column("quantity_reserved", sa.Integer, nullable=False, default=0),
        sa.Column("quantity_available", sa.Integer, nullable=False, default=0),
        sa.Column("reorder_point", sa.Integer, nullable=False, default=50),
        sa.Column("max_capacity", sa.Integer, nullable=False, default=500),
        sa.Column("avg_daily_consumption", sa.Float, nullable=False, default=0.0),
        sa.Column(
            "stock_status",
            postgresql.ENUM("normal", "low", "critical", "overstock", "out_of_stock",
                             name="stockstatus", create_type=False),
            nullable=False, default="normal"
        ),
        sa.Column("last_restocked_at", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_inventory_items_tenant_id", "inventory_items", ["tenant_id"])
    op.create_index("ix_inventory_items_warehouse_id", "inventory_items", ["warehouse_id"])
    op.create_index("ix_inventory_items_product_id", "inventory_items", ["product_id"])

    op.create_table(
        "alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "alert_type",
            postgresql.ENUM("low_stock", "overstock", "sales_drop", "revenue_target",
                             "anomaly", "system", name="alerttype", create_type=False),
            nullable=False
        ),
        sa.Column(
            "severity",
            postgresql.ENUM("info", "warning", "critical",
                             name="alertseverity", create_type=False),
            nullable=False, default="warning"
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=True),
        sa.Column("entity_id", sa.String(255), nullable=True),
        sa.Column("metadata_json", postgresql.JSON, nullable=True),
        sa.Column("is_read", sa.Boolean, default=False, nullable=False),
        sa.Column("is_resolved", sa.Boolean, default=False, nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_alerts_tenant_id", "alerts", ["tenant_id"])
    op.create_index("ix_alerts_alert_type", "alerts", ["alert_type"])

    op.create_table(
        "forecast_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "forecast_type",
            postgresql.ENUM("revenue", "inventory", "demand",
                             name="forecasttype", create_type=False),
            nullable=False
        ),
        sa.Column("forecast_date", sa.Date, nullable=False),
        sa.Column("entity_id", sa.String(255), nullable=True),
        sa.Column("entity_type", sa.String(100), nullable=True),
        sa.Column("yhat", sa.Float, nullable=False),
        sa.Column("yhat_lower", sa.Float, nullable=False),
        sa.Column("yhat_upper", sa.Float, nullable=False),
        sa.Column("trend", sa.Float, nullable=True),
        sa.Column("seasonality", sa.Float, nullable=True),
        sa.Column("model_version", sa.String(50), default="prophet_v1", nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_forecast_records_tenant_id", "forecast_records", ["tenant_id"])
    op.create_index("ix_forecast_records_forecast_date", "forecast_records", ["forecast_date"])
    op.create_index("ix_forecast_records_entity_id", "forecast_records", ["entity_id"])


def downgrade() -> None:
    op.drop_table("forecast_records")
    op.drop_table("alerts")
    op.drop_table("inventory_items")
    op.drop_table("sale_items")
    op.drop_table("sales")
    op.drop_table("products")
    op.drop_table("warehouses")
    op.drop_table("branches")
    op.drop_table("users")
    op.drop_table("tenants")

    op.execute("DROP TYPE IF EXISTS forecasttype")
    op.execute("DROP TYPE IF EXISTS alertseverity")
    op.execute("DROP TYPE IF EXISTS alerttype")
    op.execute("DROP TYPE IF EXISTS stockstatus")
    op.execute("DROP TYPE IF EXISTS productcategory")
    op.execute("DROP TYPE IF EXISTS userrole")
