import pytest
from irp.models.inventory import InventoryView, ReplenishmentTask


def test_inventory_view_creation():
    inventory = InventoryView(
        sku_id="SKU001",
        sku_name="产品A",
        sellable_qty=100,
        reserved_qty=20,
        in_transit_qty=50,
        available_qty=80,
        total_qty=170,
        stock_status="正常"
    )
    assert inventory.available_qty == 80
    assert inventory.total_qty == 170


def test_inventory_view_full_fields():
    inventory = InventoryView(
        sku_id="SKU002",
        sku_name="产品B",
        category="电子产品",
        sellable_qty=200,
        reserved_qty=30,
        in_transit_qty=100,
        quality_check_qty=10,
        returned_qty=5,
        available_qty=170,
        total_qty=345,
        reorder_point=50,
        reorder_qty=200,
        lead_time_days=14,
        preferred_supplier_id="SUP001",
        backup_supplier_id="SUP002",
        stock_status="预警"
    )
    assert inventory.sku_id == "SKU002"
    assert inventory.reorder_point == 50
    assert inventory.preferred_supplier_id == "SUP001"
    assert inventory.stock_status == "预警"


def test_replenishment_task_creation():
    task = ReplenishmentTask(
        task_id="RPT001",
        sku_id="SKU001",
        supplier_id="SUP001",
        qty=100,
        status="待采购"
    )
    assert task.status == "待采购"
    assert task.qty == 100


def test_replenishment_task_with_requisition():
    task = ReplenishmentTask(
        task_id="RPT002",
        sku_id="SKU002",
        supplier_id="SUP002",
        qty=200,
        status="采购中",
        requisition_id="REQ001"
    )
    assert task.requisition_id == "REQ001"
    assert task.status == "采购中"
