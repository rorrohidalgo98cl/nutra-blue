from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.database.supabase import supabase_client
from app.core.security import verify_admin_user
from app.core.mock_store import MOCK_ORDERS
from app.core.mock_data import MOCK_PRODUCTS
from app.models.products import Product, ProductCreate, ProductUpdate
from app.models.orders import OrderUpdateStatus
import uuid

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/orders")
async def list_orders(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    _: dict = Depends(verify_admin_user),
):
    if supabase_client is None:
        orders = list(MOCK_ORDERS.values())
        if status:
            orders = [o for o in orders if o.get("status") == status]
        return sorted(orders, key=lambda o: o.get("created_at", ""), reverse=True)[:limit]

    try:
        query = supabase_client.from_("orders").select("*").order("created_at", desc=True).limit(limit)
        if status:
            query = query.eq("status", status)
        response = query.execute()
        return response.data or []
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch orders")


@router.patch("/orders/{order_id}/status")
async def admin_update_order_status(
    order_id: str,
    status_data: OrderUpdateStatus,
    _: dict = Depends(verify_admin_user),
):
    allowed = {"pending", "paid", "expired", "cancelled", "shipped"}
    if status_data.status not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {allowed}")

    if supabase_client is None:
        if order_id not in MOCK_ORDERS:
            raise HTTPException(status_code=404, detail="Order not found")
        MOCK_ORDERS[order_id]["status"] = status_data.status
        return MOCK_ORDERS[order_id]

    try:
        response = supabase_client.from_("orders").update(
            {"status": status_data.status}
        ).eq("id", order_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Order not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update order")


@router.get("/products", response_model=List[Product])
async def list_products(_: dict = Depends(verify_admin_user)):
    if supabase_client is None:
        return MOCK_PRODUCTS

    try:
        response = supabase_client.from_("products").select("*").order("name").execute()
        return response.data or []
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch products")


@router.post("/products", response_model=Product)
async def create_product(product: ProductCreate, _: dict = Depends(verify_admin_user)):
    if supabase_client is None:
        new_product = {
            "id": str(uuid.uuid4()),
            **product.model_dump(),
        }
        MOCK_PRODUCTS.append(new_product)
        return new_product

    try:
        response = supabase_client.from_("products").insert(product.model_dump()).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create product")
        return response.data[0]
    except Exception as e:
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(status_code=400, detail="Product name already exists")
        raise HTTPException(status_code=500, detail="Failed to create product")


@router.patch("/products/{product_id}", response_model=Product)
async def update_product(
    product_id: str,
    product: ProductUpdate,
    _: dict = Depends(verify_admin_user),
):
    update_data = {k: v for k, v in product.model_dump().items() if v is not None}

    if supabase_client is None:
        for p in MOCK_PRODUCTS:
            if p["id"] == product_id:
                p.update(update_data)
                return p
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        response = supabase_client.from_("products").update(update_data).eq("id", product_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Product not found")
        return response.data[0]
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update product")


@router.delete("/products/{product_id}")
async def delete_product(product_id: str, _: dict = Depends(verify_admin_user)):
    if supabase_client is None:
        for i, p in enumerate(MOCK_PRODUCTS):
            if p["id"] == product_id:
                MOCK_PRODUCTS.pop(i)
                return {"success": True}
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        response = supabase_client.from_("products").delete().eq("id", product_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to delete product")


@router.get("/dashboard/metrics")
async def get_dashboard_metrics(_: dict = Depends(verify_admin_user)):
    if supabase_client is None:
        orders = list(MOCK_ORDERS.values())
        revenue = sum(o.get("total", 0) for o in orders if o.get("status") in ["paid", "shipped"])
        pending_orders = sum(1 for o in orders if o.get("status") == "pending")
        return {
            "revenue": revenue,
            "pending_orders": pending_orders,
            "visits": 1420,
            "conversion_rate": 2.8
        }
    try:
        res_orders = supabase_client.from_("orders").select("total, status").execute()
        orders_data = res_orders.data or []
        revenue = sum(o.get("total", 0) or o.get("total_amount", 0) for o in orders_data if o.get("status") in ["paid", "shipped"])
        pending_orders = sum(1 for o in orders_data if o.get("status") == "pending")
        return {
            "revenue": revenue,
            "pending_orders": pending_orders,
            "visits": 1420,
            "conversion_rate": 2.8
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard metrics: {str(e)}")


@router.get("/orders/recent")
async def get_recent_orders(limit: int = 10, _: dict = Depends(verify_admin_user)):
    if supabase_client is None:
        orders = list(MOCK_ORDERS.values())
        return sorted(orders, key=lambda o: o.get("created_at", ""), reverse=True)[:limit]
    try:
        response = supabase_client.from_("orders").select("*").order("created_at", desc=True).limit(limit).execute()
        return response.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recent orders: {str(e)}")


@router.get("/inventory/alerts")
async def get_inventory_alerts(_: dict = Depends(verify_admin_user)):
    if supabase_client is None:
        low_stock = [p for p in MOCK_PRODUCTS if p.get("stock", 0) <= 40]
        # Return mock expiration alerts
        expiration_alerts = [
            {"id": "matcha-ritual", "name": "Matcha Ritual", "stock": 35, "alert_type": "vencimiento", "details": "Vence en 15 días"}
        ]
        return {
            "low_stock": low_stock[:5],
            "expiration": expiration_alerts
        }
    try:
        res_low = supabase_client.from_("products").select("*").lte("stock", 10).execute()
        # Handle expiration alerts gracefully (return empty list if column doesn't exist yet)
        try:
            res_exp = supabase_client.from_("products").select("*").execute()
            expiration = []
            for p in (res_exp.data or []):
                exp_date = p.get("expiration_date")
                if exp_date:
                    expiration.append(p)
        except Exception:
            expiration = []
        return {
            "low_stock": res_low.data or [],
            "expiration": expiration
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch inventory alerts: {str(e)}")


@router.post("/products/quick-add", response_model=Product)
async def quick_add_product(product: ProductCreate, _: dict = Depends(verify_admin_user)):
    if supabase_client is None:
        new_product = {
            "id": str(uuid.uuid4()),
            **product.model_dump(),
        }
        MOCK_PRODUCTS.append(new_product)
        return new_product

    try:
        response = supabase_client.from_("products").insert(product.model_dump()).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create product")
        return response.data[0]
    except Exception as e:
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(status_code=400, detail="Product name already exists")
        raise HTTPException(status_code=500, detail="Failed to create product")

