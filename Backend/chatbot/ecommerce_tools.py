from channels.db import database_sync_to_async


@database_sync_to_async
def search_products(params):
    # Replace with real product search logic
    return [
        {"id": 1, "name": "Phone X", "price": 999, "category": "phone"},
        {"id": 2, "name": "Laptop Y", "price": 1299, "category": "laptop"},
    ]


@database_sync_to_async
def add_to_cart(params):
    # Replace with real add-to-cart logic
    return {"success": True, "message": f"Added product {params.get('product_id')} to cart."}


@database_sync_to_async
def show_cart(params):
    # Replace with real cart retrieval logic
    return {
        "cart": [
            {"id": 1, "name": "Phone X", "price": 999, "quantity": 1},
            {"id": 2, "name": "Laptop Y", "price": 1299, "quantity": 2},
        ]
    }


@database_sync_to_async
def show_order_details(params):
    # Replace with real order details logic
    return {
        "order_id": params.get("order_id"),
        "items": [
            {"id": 1, "name": "Phone X", "price": 999, "quantity": 1},
        ],
        "status": "shipped",
    }


#  tools for OpenAI API
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search for products by category, price limit, or keyword.",
            "parameters": {
                "type": "object",
                "properties": {"category": {"type": "string"}, "price_limit": {"type": "number"}, "keyword": {"type": "string"}},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_cart",
            "description": "Add a product to the user's cart.",
            "parameters": {"type": "object", "properties": {"product_id": {"type": "integer"}, "quantity": {"type": "integer"}}, "required": ["product_id"]},
        },
    },
    {
        "type": "function",
        "function": {"name": "show_cart", "description": "Show the user's current cart details.", "parameters": {"type": "object", "properties": {}}},
    },
    {
        "type": "function",
        "function": {
            "name": "show_order_details",
            "description": "Show details for a specific order.",
            "parameters": {"type": "object", "properties": {"order_id": {"type": "integer"}}, "required": ["order_id"]},
        },
    },
]
