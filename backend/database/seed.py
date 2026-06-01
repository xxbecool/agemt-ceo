"""
Seed script — generates 365 days of realistic demo data for ExecutiveAI.
Run: python -m database.seed
"""
import asyncio
import uuid
import random
from datetime import date, timedelta, datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import AsyncSessionLocal, create_tables
from core.security import get_password_hash
from models.tenant import Tenant
from models.user import User, UserRole
from models.product import Product, ProductCategory
from models.branch import Branch
from models.warehouse import Warehouse
from models.inventory import InventoryItem
from models.sale import Sale, SaleItem
from models.alert import Alert, AlertType, AlertSeverity

random.seed(42)

PRODUCTS_DATA = [
    ("EL001", '4K Smart TV 55"', ProductCategory.ELECTRONICS, 1200, 700),
    ("EL002", 'Laptop Pro 15"', ProductCategory.ELECTRONICS, 1500, 900),
    ("EL003", "Wireless Headphones", ProductCategory.ELECTRONICS, 250, 120),
    ("EL004", "Smartphone X12", ProductCategory.ELECTRONICS, 900, 500),
    ("EL005", 'Tablet Air 10"', ProductCategory.ELECTRONICS, 600, 320),
    ("EL006", "Smartwatch Series 5", ProductCategory.ELECTRONICS, 350, 180),
    ("EL007", "Bluetooth Speaker", ProductCategory.ELECTRONICS, 150, 70),
    ("EL008", "Gaming Console", ProductCategory.ELECTRONICS, 499, 280),
    ("EL009", "Mechanical Keyboard", ProductCategory.ELECTRONICS, 180, 85),
    ("EL010", "USB-C Hub 7-Port", ProductCategory.ELECTRONICS, 80, 35),
    ("HE001", "Vitamin D3 1000IU", ProductCategory.HEALTH, 25, 8),
    ("HE002", "Whey Protein 5lb", ProductCategory.HEALTH, 65, 28),
    ("HE003", "Omega-3 Fish Oil", ProductCategory.HEALTH, 30, 12),
    ("HE004", "Multivitamin Men", ProductCategory.HEALTH, 35, 14),
    ("HE005", "Probiotic 50B CFU", ProductCategory.HEALTH, 45, 18),
    ("HE006", "Collagen Peptides", ProductCategory.HEALTH, 55, 22),
    ("HE007", "Pre-Workout Formula", ProductCategory.HEALTH, 50, 20),
    ("HE008", "BCAA Powder", ProductCategory.HEALTH, 40, 16),
    ("HE009", "Melatonin 5mg", ProductCategory.HEALTH, 20, 7),
    ("HE010", "Zinc + Magnesium", ProductCategory.HEALTH, 28, 11),
    ("FD001", "Organic Coffee Beans 1kg", ProductCategory.FOOD, 32, 14),
    ("FD002", "Extra Virgin Olive Oil 1L", ProductCategory.FOOD, 22, 9),
    ("FD003", "Organic Oats 2kg", ProductCategory.FOOD, 15, 6),
    ("FD004", "Almond Butter 500g", ProductCategory.FOOD, 18, 8),
    ("FD005", "Quinoa 1kg", ProductCategory.FOOD, 14, 5),
    ("FD006", "Protein Granola 500g", ProductCategory.FOOD, 12, 5),
    ("FD007", "Dark Chocolate 85% 100g", ProductCategory.FOOD, 8, 3),
    ("FD008", "Green Tea 100 bags", ProductCategory.FOOD, 16, 6),
    ("FD009", "Coconut Water 1L", ProductCategory.FOOD, 4, 1.5),
    ("FD010", "Mixed Nuts 500g", ProductCategory.FOOD, 20, 9),
    ("CL001", "Performance T-Shirt", ProductCategory.CLOTHING, 45, 18),
    ("CL002", "Running Shorts", ProductCategory.CLOTHING, 55, 22),
    ("CL003", "Athletic Hoodie", ProductCategory.CLOTHING, 85, 35),
    ("CL004", "Compression Leggings", ProductCategory.CLOTHING, 70, 28),
    ("CL005", "Sports Bra Pro", ProductCategory.CLOTHING, 60, 25),
    ("CL006", "Track Pants", ProductCategory.CLOTHING, 75, 30),
    ("CL007", "Gym Gloves", ProductCategory.CLOTHING, 25, 10),
    ("CL008", "Baseball Cap", ProductCategory.CLOTHING, 30, 12),
    ("CL009", "Ankle Socks 6-Pack", ProductCategory.CLOTHING, 22, 8),
    ("CL010", "Winter Jacket", ProductCategory.CLOTHING, 180, 80),
    ("SP001", "Yoga Mat Pro", ProductCategory.SPORTS, 55, 22),
    ("SP002", "Resistance Bands Set", ProductCategory.SPORTS, 35, 14),
    ("SP003", "Dumbbell Set 20kg", ProductCategory.SPORTS, 150, 65),
    ("SP004", "Jump Rope Speed", ProductCategory.SPORTS, 25, 10),
    ("SP005", "Foam Roller", ProductCategory.SPORTS, 40, 16),
    ("SP006", "Water Bottle 1L", ProductCategory.SPORTS, 28, 11),
    ("SP007", "Pull-Up Bar", ProductCategory.SPORTS, 65, 28),
    ("SP008", "Ab Wheel Roller", ProductCategory.SPORTS, 30, 12),
    ("SP009", "Kettlebell 16kg", ProductCategory.SPORTS, 80, 35),
    ("SP010", "Boxing Gloves", ProductCategory.SPORTS, 90, 40),
]

BRANCHES_DATA = [
    ("North Branch", "BR-N", "123 North Ave", "New York", "Northeast"),
    ("South Branch", "BR-S", "456 South Blvd", "Miami", "Southeast"),
    ("East Branch", "BR-E", "789 East St", "Boston", "Northeast"),
    ("West Branch", "BR-W", "321 West Dr", "Los Angeles", "West"),
    ("Central Branch", "BR-C", "555 Central Pkwy", "Chicago", "Midwest"),
]

WAREHOUSES_DATA = [
    ("Main Warehouse", "WH-01", "100 Industrial Rd", "New York", 50000),
    ("South Depot", "WH-02", "200 Logistics Way", "Miami", 30000),
    ("West Hub", "WH-03", "300 Storage Blvd", "Los Angeles", 25000),
]


def revenue_for_date(d: date, branch_multiplier: float, base: float) -> float:
    dow = d.weekday()
    dow_factors = [0.95, 1.0, 1.05, 1.08, 1.15, 0.75, 0.65]
    day_of_year = (d - date(d.year, 1, 1)).days
    trend = 1 + (day_of_year / 365) * 0.12
    month = d.month
    seasonal = 1.25 if month == 12 else (1.15 if month in [11, 3] else 1.0)
    noise = random.uniform(0.88, 1.12)
    return base * branch_multiplier * dow_factors[dow] * trend * seasonal * noise


async def seed(db: AsyncSession):
    print("Creating tables...")
    await create_tables()

    existing = await db.execute(select(Tenant).limit(1))
    if existing.scalar_one_or_none():
        print("Already seeded. Skipping.")
        return

    print("Seeding tenant...")
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Acme Corporation",
        slug="acme-corporation",
        plan="enterprise",
        is_active=True,
    )
    db.add(tenant)
    await db.flush()
    tid = tenant.id

    print("Seeding users...")
    users = [
        User(id=uuid.uuid4(), tenant_id=tid, email="ceo@acme.com", full_name="Sarah Chen",
             hashed_password=get_password_hash("password123"), role=UserRole.CEO, is_active=True, is_verified=True),
        User(id=uuid.uuid4(), tenant_id=tid, email="ops@acme.com", full_name="Marcus Johnson",
             hashed_password=get_password_hash("password123"), role=UserRole.OPERATIONS_MANAGER, is_active=True, is_verified=True),
        User(id=uuid.uuid4(), tenant_id=tid, email="sales@acme.com", full_name="Priya Patel",
             hashed_password=get_password_hash("password123"), role=UserRole.SALES_MANAGER, is_active=True, is_verified=True),
        User(id=uuid.uuid4(), tenant_id=tid, email="analyst@acme.com", full_name="David Kim",
             hashed_password=get_password_hash("password123"), role=UserRole.ANALYST, is_active=True, is_verified=True),
    ]
    for u in users:
        db.add(u)
    await db.flush()

    print("Seeding branches...")
    branch_multipliers = [1.25, 0.82, 0.95, 1.10, 0.88]
    branches = []
    for (name, code, addr, city, region), mult in zip(BRANCHES_DATA, branch_multipliers):
        b = Branch(
            id=uuid.uuid4(), tenant_id=tid, name=name, code=code,
            address=addr, city=city, region=region, is_active=True,
            manager_name=f"Manager of {name}",
        )
        branches.append((b, mult))
        db.add(b)
    await db.flush()

    print("Seeding warehouses...")
    warehouses = []
    for name, code, addr, city, cap in WAREHOUSES_DATA:
        w = Warehouse(id=uuid.uuid4(), tenant_id=tid, name=name, code=code, address=addr, city=city,
                      max_capacity=cap, is_active=True)
        warehouses.append(w)
        db.add(w)
    await db.flush()

    print("Seeding products...")
    products = []
    for sku, name, cat, price, cost in PRODUCTS_DATA:
        p = Product(
            id=uuid.uuid4(), tenant_id=tid, sku=sku, name=name, category=cat,
            unit_price=price, cost_price=cost, is_active=True,
            reorder_point=random.randint(20, 60),
            max_stock_level=random.randint(300, 800),
        )
        products.append(p)
        db.add(p)
    await db.flush()

    print("Seeding inventory...")
    for p in products:
        wh = random.choice(warehouses)
        max_cap = random.randint(200, 600)
        qty_pct = random.choice([0.05, 0.08, 0.15, 0.35, 0.50, 0.65, 0.80])
        qty = int(max_cap * qty_pct)
        daily_consumption = round(random.uniform(1, 15), 2)
        inv = InventoryItem(
            id=uuid.uuid4(), tenant_id=tid, warehouse_id=wh.id, product_id=p.id,
            quantity_on_hand=qty, quantity_reserved=0, quantity_available=qty,
            reorder_point=p.reorder_point, max_capacity=max_cap,
            avg_daily_consumption=daily_consumption,
        )
        db.add(inv)
    await db.flush()

    print("Seeding 365 days of sales...")
    today = date.today()
    sale_count = 0
    for days_ago in range(365, -1, -1):
        sale_date = today - timedelta(days=days_ago)
        for branch, mult in branches:
            num_sales = random.randint(4, 18)
            for _ in range(num_sales):
                invoice = f"INV-{sale_date.strftime('%Y%m%d')}-{branch.code}-{random.randint(1000,9999)}"
                items_in_sale = random.sample(products, random.randint(1, 4))
                total_amount = 0.0
                total_cost = 0.0
                sale_items = []
                for prod in items_in_sale:
                    qty = random.randint(1, 5)
                    price = prod.unit_price * random.uniform(0.95, 1.05)
                    cost = prod.cost_price
                    line_total = round(qty * price, 2)
                    total_amount += line_total
                    total_cost += qty * cost
                    sale_items.append((prod, qty, price, cost, line_total))

                total_amount = round(total_amount * mult, 2)
                gross_profit = round(total_amount - total_cost, 2)
                sale = Sale(
                    id=uuid.uuid4(), tenant_id=tid, branch_id=branch.id,
                    sale_date=sale_date, invoice_number=invoice,
                    total_amount=total_amount, total_cost=round(total_cost, 2),
                    gross_profit=gross_profit, payment_method=random.choice(["cash", "card", "transfer"]),
                )
                db.add(sale)
                await db.flush()

                for prod, qty, price, cost, line_total in sale_items:
                    si = SaleItem(
                        id=uuid.uuid4(), tenant_id=tid, sale_id=sale.id, product_id=prod.id,
                        quantity=qty, unit_price=round(price, 2), unit_cost=cost,
                        line_total=round(line_total * mult, 2),
                    )
                    db.add(si)
                sale_count += 1

        if days_ago % 30 == 0:
            await db.flush()
            print(f"  {365 - days_ago}/365 days seeded ({sale_count} sales)...")

    print("Seeding alerts...")
    alert_data = [
        (AlertType.LOW_STOCK, AlertSeverity.CRITICAL, "Critical Stock: Whey Protein 5lb",
         "Whey Protein 5lb has only 8 units remaining. Expected depletion in 2 days."),
        (AlertType.LOW_STOCK, AlertSeverity.WARNING, 'Low Stock: Laptop Pro 15"',
         'Laptop Pro 15" stock is at 12% capacity. Reorder recommended within 3 days.'),
        (AlertType.SALES_DROP, AlertSeverity.WARNING, "Sales Drop Detected: South Branch",
         "South Branch revenue dropped 18% vs 7-day average. Investigation recommended."),
        (AlertType.LOW_STOCK, AlertSeverity.CRITICAL, "Critical Stock: Smartphone X12",
         "Smartphone X12 has 5 units. At current velocity, stock depletes in 1 day."),
        (AlertType.ANOMALY, AlertSeverity.INFO, "Revenue Spike: North Branch",
         "North Branch revenue 24% above average yesterday. Likely due to promotional event."),
    ]
    for atype, sev, title, msg in alert_data:
        a = Alert(
            id=uuid.uuid4(), tenant_id=tid, alert_type=atype, severity=sev,
            title=title, message=msg, is_read=False, is_resolved=False,
        )
        db.add(a)

    await db.commit()
    print(f"\n✓ Seeding complete!")
    print(f"  Tenant: Acme Corporation")
    print(f"  Users: {len(users)} (ceo@acme.com / password123)")
    print(f"  Products: {len(products)}")
    print(f"  Branches: {len(branches)}")
    print(f"  Warehouses: {len(warehouses)}")
    print(f"  Sales records: {sale_count}")


async def main():
    async with AsyncSessionLocal() as db:
        await seed(db)


if __name__ == "__main__":
    asyncio.run(main())
