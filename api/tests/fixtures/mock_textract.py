"""Mock AWS Textract responses for testing."""


def get_mock_textract_response():
    """
    Mock AnalyzeExpense response matching AWS Textract format.

    Based on actual Textract AnalyzeExpense API response structure.
    """
    return {
        "ExpenseDocuments": [
            {
                "SummaryFields": [
                    {
                        "Type": {"Text": "VENDOR_NAME"},
                        "ValueDetection": {"Text": "Walmart Supercenter"}
                    },
                    {
                        "Type": {"Text": "INVOICE_RECEIPT_DATE"},
                        "ValueDetection": {"Text": "01/15/2024"}
                    },
                    {
                        "Type": {"Text": "TOTAL"},
                        "ValueDetection": {"Text": "45.67"}
                    },
                    {
                        "Type": {"Text": "TAX"},
                        "ValueDetection": {"Text": "3.42"}
                    }
                ],
                "LineItemGroups": [
                    {
                        "LineItems": [
                            {
                                "LineItemExpenseFields": [
                                    {
                                        "Type": {"Text": "ITEM"},
                                        "ValueDetection": {"Text": "Bananas Organic"}
                                    },
                                    {
                                        "Type": {"Text": "PRICE"},
                                        "ValueDetection": {"Text": "2.50"}
                                    },
                                    {
                                        "Type": {"Text": "QUANTITY"},
                                        "ValueDetection": {"Text": "1"}
                                    }
                                ]
                            },
                            {
                                "LineItemExpenseFields": [
                                    {
                                        "Type": {"Text": "ITEM"},
                                        "ValueDetection": {"Text": "Milk 2% Gallon"}
                                    },
                                    {
                                        "Type": {"Text": "PRICE"},
                                        "ValueDetection": {"Text": "4.99"}
                                    }
                                ]
                            },
                            {
                                "LineItemExpenseFields": [
                                    {
                                        "Type": {"Text": "ITEM"},
                                        "ValueDetection": {"Text": "Bread Whole Wheat"}
                                    },
                                    {
                                        "Type": {"Text": "PRICE"},
                                        "ValueDetection": {"Text": "3.49"}
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
