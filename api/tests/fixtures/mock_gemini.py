"""Mock Gemini API responses for testing."""


def get_mock_gemini_extraction():
    """
    Mock Gemini extraction output matching ReceiptExtraction schema.
    """
    return {
        "merchant_name": "Walmart",
        "purchase_date": "2024-01-15",
        "total_amount": "45.67",
        "tax_amount": "3.42",
        "line_items": [
            {
                "description": "Bananas Organic",
                "category": "Groceries",
                "quantity": 1,
                "unit_price": "2.50",
                "total_price": "2.50"
            },
            {
                "description": "Milk 2% Gallon",
                "category": "Groceries",
                "quantity": 1,
                "unit_price": "4.99",
                "total_price": "4.99"
            },
            {
                "description": "Bread Whole Wheat",
                "category": "Groceries",
                "quantity": 1,
                "unit_price": "3.49",
                "total_price": "3.49"
            },
            {
                "description": "Eggs Organic Dozen",
                "category": "Groceries",
                "quantity": 1,
                "unit_price": "5.99",
                "total_price": "5.99"
            },
            {
                "description": "Orange Juice",
                "category": "Groceries",
                "quantity": 1,
                "unit_price": "4.29",
                "total_price": "4.29"
            },
            {
                "description": "Yogurt Greek",
                "category": "Groceries",
                "quantity": 2,
                "unit_price": "1.99",
                "total_price": "3.98"
            },
            {
                "description": "Apples Gala",
                "category": "Groceries",
                "quantity": 1,
                "unit_price": "5.49",
                "total_price": "5.49"
            },
            {
                "description": "Pasta Spaghetti",
                "category": "Groceries",
                "quantity": 1,
                "unit_price": "1.49",
                "total_price": "1.49"
            },
            {
                "description": "Tomato Sauce",
                "category": "Groceries",
                "quantity": 1,
                "unit_price": "2.79",
                "total_price": "2.79"
            },
            {
                "description": "Chicken Breast",
                "category": "Groceries",
                "quantity": 1,
                "unit_price": "7.24",
                "total_price": "7.24"
            }
        ]
    }
