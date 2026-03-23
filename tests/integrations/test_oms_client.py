import pytest
from irp.integrations.oms_client import OMSInventory


def test_oms_inventory_model():
    inventory = OMSInventory(
        sku_id="SKU001",
        sku_name="Product A",
        sellable_qty=100,
        reserved_qty=20,
        in_transit_qty=50,
        available_qty=80
    )
    assert inventory.sku_id == "SKU001"
    assert inventory.sellable_qty == 100
    assert inventory.available_qty == 80


def test_oms_inventory_available_calculation():
    inventory = OMSInventory(
        sku_id="SKU002",
        sku_name="Product B",
        sellable_qty=200,
        reserved_qty=50,
        available_qty=150
    )
    assert inventory.available_qty == 150
