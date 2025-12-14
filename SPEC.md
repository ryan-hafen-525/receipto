# Reciepto Application Specification

## 1. Executive Summary

**Reciepto** is a receipt analysis and budgeting application designed to automate the extraction of detailed line-item data from physical receipts. By leveraging AWS Textract for OCR and a LangGraph-orchestrated LLM workflow for semantic cleaning, Reciepto transforms unstructured images into structured financial data for analytics and budgeting.

## 2. Tech Stack & Architecture

### 2.1 Core Stack

- **Frontend**: Next.js 14+ (App Router), TypeScript, Tailwind CSS, Shadcn/UI.
- **Backend**: FastAPI (Python 3.10+), Pydantic.
- **AI/ML**: LangGraph (Workflow Orchestration), AWS Textract (OCR), OpenAI/Anthropic (LLM for cleaning).
- **Database**: PostgreSQL (v16).
- **Infrastructure**: Docker, Docker Compose (Local Dev), SeasweedFS (image storage).

### 2.2 Application Type & Configuration

- **Single User Application**: Reciepto is designed as a single-user application. There is no multi-user authentication or user management system.
- **Secrets Management**: All API keys and sensitive credentials (AWS Textract, OpenAI/Anthropic API keys, database connection strings) are stored as environment variables and passed to containers via docker-compose configuration.

## 3. Features Specification

### 3.1 Frontend (Next.js)

#### Receipt Upload Zone
- Drag-and-drop interface for images (JPG, PNG) and PDFs.
- Optimistic UI updates showing "Processing..." status.

#### Dashboard
- **Recent Activity**: List of recently uploaded receipts with status indicators (Pending, Analyzed, Failed).
- **Monthly Overview**: Card showing Total Spent, Top Category, and Budget Health.

#### All Receipt View
- A table of all the receipts that have been uploaded with options to sort on different columns. Includes the name of the store, total cost, and date.

#### Receipt Detail View
- Side-by-side view: Original Receipt Image vs. Extracted Data.
- Editable fields for user corrections (Merchant Name, Date, Line Item Prices).

#### Analytics Page
- Visualizations using Recharts/Visx:
  - Spending by Category (Pie Chart)
  - Monthly Trend (Bar Chart)
  - Merchant Frequency (List)
- **Export Functionality**:
  - Export analytics data to CSV format
  - Include all receipts data with line items
  - Filterable by date range before export

#### Budgeting Tools
- Set monthly limits per category (e.g., "Groceries: $400")
- Alerts/Visual indicators when nearing limits

#### Settings
- Allow to edit possible categories.
- Change the llm
- Input API keys for textract and LLMs

### 3.2 Backend (FastAPI)

#### API Endpoints

- **POST /receipts/upload**: Accepts file, uploads to storage, initiates LangGraph run (background task).
  - **200 OK**: File uploaded successfully, returns receipt ID and processing status
  - **400 Bad Request**: Invalid file format or size
  - **413 Payload Too Large**: File exceeds size limit
  - **500 Internal Server Error**: Storage or processing initialization failed

- **GET /receipts**: Returns paginated list of receipts with summary data.
  - **200 OK**: Returns paginated receipt list with metadata
  - **400 Bad Request**: Invalid pagination parameters

- **GET /receipts/{id}**: Returns full details including line items.
  - **200 OK**: Returns complete receipt with all line items
  - **404 Not Found**: Receipt ID does not exist

- **PATCH /receipts/{id}**: Allows manual user overrides of extracted data.
  - **200 OK**: Receipt updated successfully
  - **400 Bad Request**: Invalid data format
  - **404 Not Found**: Receipt ID does not exist

- **GET /analytics/spending**: Aggregated data for frontend charts.
  - **200 OK**: Returns aggregated spending data
  - **400 Bad Request**: Invalid query parameters

- **GET /analytics/export**: Export receipt data to CSV format.
  - **200 OK**: Returns CSV file download
  - **400 Bad Request**: Invalid date range or filter parameters

#### Background Workers

Uses FastAPI BackgroundTasks or Celery to run the LangGraph workflow asynchronously so the upload endpoint doesn't timeout.

## 4. LangGraph Workflow (The "Brain")

The core logic resides in a stateful graph that processes the receipt.

### State Schema (ReceiptState)

```python
class ReceiptState(TypedDict):
    image_path: str
    raw_textract_output: dict
    cleaned_json: dict
    validation_errors: list[str]
    status: Literal['processing', 'review_required', 'complete']
```

### Nodes

#### ocr_node
- Calls AWS Textract DetectDocumentText (or AnalyzeDocument for tables).
- Stores raw blocks in state.

#### extraction_node
- Constructs a prompt with the raw OCR text.
- Asks LLM to extract: Merchant, Date, Total, Tax, and a list of LineItems (Name, Category, Price, Qty).
- **Crucial Step**: The LLM normalizes data (e.g., converts "Wal-Mrt Super" → "Walmart", formats dates to ISO 8601).

#### validation_node
- Uses Pydantic to validate the LLM output.
- Checks if `Sum(LineItems) + Tax ~= Total`.
- If validation fails, it can loop back to extraction_node with an error message (Self-Correction) or flag for human review.

#### persistence_node
- Saves the final structured object to PostgreSQL.

## 5. Database Schema (PostgreSQL)

### Table: receipts

| Column         | Type    | Constraints                                    |
|----------------|---------|------------------------------------------------|
| id             | UUID    | Primary Key                                    |
| image_url      | String  |                                                |
| merchant_name  | String  |                                                |
| purchase_date  | Date    |                                                |
| total_amount   | Decimal |                                                |
| tax_amount     | Decimal |                                                |
| status         | Enum    | pending, complete, manual_review               |
| created_at     | Timestamp |                                              |

### Table: line_items

| Column       | Type    | Constraints                   | Notes                                                    |
|--------------|---------|-------------------------------|----------------------------------------------------------|
| id           | UUID    | Primary Key                   |                                                          |
| receipt_id   | UUID    | Foreign Key → receipts.id     |                                                          |
| description  | String  |                               |                                                          |
| category     | String  |                               | Inferred by LLM (e.g., Food, Utilities, Entertainment)   |
| quantity     | Integer |                               |                                                          |
| unit_price   | Decimal |                               |                                                          |
| total_price  | Decimal |                               |                                                          |

### Table: categories

| Column               | Type    | Constraints               |
|----------------------|---------|---------------------------|
| id                   | UUID    | Primary Key               |
| name                 | String  |                           |
| monthly_budget_limit | Decimal |                           |

#### Default Categories

The application will seed the following default categories on first run:
- **Groceries**: Food and household supplies from grocery stores
- **Dining**: Restaurants, cafes, fast food, delivery services
- **Transportation**: Gas, public transit, parking, rideshare
- **Utilities**: Electric, water, gas, internet, phone bills
- **Entertainment**: Movies, concerts, streaming services, hobbies
- **Healthcare**: Pharmacy, doctor visits, medical supplies
- **Clothing**: Apparel, shoes, accessories
- **Home & Garden**: Furniture, home improvement, gardening
- **Personal Care**: Haircuts, cosmetics, gym memberships
- **Shopping**: General retail, electronics, online shopping
- **Other**: Miscellaneous items that don't fit other categories

## 6. Containerization Strategy

The application will be defined in a `docker-compose.yml` for easy orchestration.

### Services

#### frontend
- **Build context**: `./frontend`
- **Port**: 3000

#### backend
- **Build context**: `./backend`
- **Port**: 8000
- **Environment**: AWS credentials, OpenAI API Key, DB connection string

#### db
- **Image**: `postgres:16-alpine`
- **Port**: 5432
- **Volume**: `./postgres-data:/var/lib/postgresql/data`

## 7. Testing Strategy

### 7.1 Unit Testing

#### Frontend Tests
- **Framework**: Jest + React Testing Library
- **Coverage**: Component rendering, user interactions, state management
- **Mocking**: API calls using MSW (Mock Service Worker)

#### Backend Tests
- **Framework**: pytest + pytest-asyncio
- **Coverage**: API endpoints, business logic, data validation
- **Mocking Strategies**:
  - **AWS Textract**: Use `moto` library or custom mock responses for Textract API calls
  - **LLM APIs**: Create fixture responses with typical extraction outputs; mock OpenAI/Anthropic SDK calls
  - **Database**: Use pytest fixtures with in-memory SQLite or PostgreSQL test containers

### 7.2 Integration Testing

- **API Integration**: Test full request/response cycles with test database
- **LangGraph Workflow**: Test complete workflow with mocked external services
- **Database Operations**: Test with actual PostgreSQL instance in test mode

### 7.3 Mock Data Examples

#### Mock Textract Response
```python
mock_textract_response = {
    "Blocks": [
        {"BlockType": "LINE", "Text": "WALMART SUPERCENTER", "Confidence": 99.5},
        {"BlockType": "LINE", "Text": "Date: 01/15/2024", "Confidence": 98.2},
        # ... additional blocks
    ]
}
```

#### Mock LLM Extraction Output
```python
mock_llm_output = {
    "merchant_name": "Walmart",
    "purchase_date": "2024-01-15",
    "total_amount": 45.67,
    "tax_amount": 3.42,
    "line_items": [
        {"description": "Bananas", "category": "Groceries", "quantity": 1, "unit_price": 2.50, "total_price": 2.50},
        {"description": "Milk", "category": "Groceries", "quantity": 1, "unit_price": 4.99, "total_price": 4.99}
    ]
}
```