# Reciepto

**Reciepto** is an intelligent receipt management and budgeting application that automatically extracts detailed line-item data from physical receipts. Using AWS Textract for OCR and LangGraph-orchestrated LLM workflows, Reciepto transforms receipt images into structured financial data for analytics and budgeting.

## Features

### 📸 Receipt Processing
- **Smart Upload**: Drag-and-drop interface for JPG, PNG, and PDF receipts
- **AI-Powered Extraction**: Automated OCR with AWS Textract and LLM-based data cleaning
- **Line-Item Detection**: Extracts individual items, prices, quantities, and categories
- **Manual Corrections**: Edit and correct extracted data through an intuitive interface

### 📊 Analytics & Insights
- **Visual Dashboards**:
  - Spending by Category (Pie Charts)
  - Monthly Trends (Bar Charts)
  - Merchant Frequency Analysis
- **CSV Export**: Export all receipt data for external analysis
- **Recent Activity**: Track processing status of uploaded receipts

### 💰 Budget Management
- **Category Budgets**: Set monthly spending limits per category
- **Smart Alerts**: Visual indicators when approaching budget limits
- **11 Default Categories**: Groceries, Dining, Transportation, Utilities, Entertainment, Healthcare, Clothing, Home & Garden, Personal Care, Shopping, and Other

### ⚙️ Customization
- **Category Management**: Create and edit spending categories
- **LLM Selection**: Choose between OpenAI and Anthropic models
- **API Configuration**: Manage AWS Textract and LLM API keys

## Tech Stack

### Frontend
- **Next.js 16** with App Router
- **React 19** with TypeScript
- **Tailwind CSS 4** for styling
- **Shadcn/UI** component library

### Backend
- **FastAPI** (Python 3.12)
- **LangGraph** for workflow orchestration
- **AWS Textract** for OCR
- **OpenAI/Anthropic** for LLM-based data extraction
- **Pydantic** for data validation

### Infrastructure
- **PostgreSQL 16** for data storage
- **SeaweedFS** for image storage
- **Docker & Docker Compose** for containerization

## Prerequisites

- **Node.js** 20+ and npm
- **Python** 3.12+
- **Docker** and Docker Compose
- **API Keys**:
  - AWS credentials with Textract access
  - OpenAI or Anthropic API key

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd reciepto
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# LLM API Keys
OPENAI_API_KEY=your_openai_key
# OR
ANTHROPIC_API_KEY=your_anthropic_key

# Database
DATABASE_URL=postgresql://user:password@db:5432/receipto

# SeaweedFS
SEAWEEDFS_URL=http://seaweedfs:8080
```

### 3. Start with Docker Compose (Recommended)

```bash
docker-compose up -d
```

Access the application:
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

### 4. Manual Setup (Development)

#### Backend Setup

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
fastapi dev main.py
```

The API will be available at http://localhost:8000

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:3000

## Project Structure

```
reciepto/
├── api/                    # FastAPI backend
│   ├── main.py            # Application entry point
│   ├── requirements.txt   # Python dependencies
│   └── .venv/            # Virtual environment (gitignored)
│
├── frontend/              # Next.js frontend
│   ├── app/              # Next.js App Router pages
│   ├── public/           # Static assets
│   ├── package.json      # Node dependencies
│   └── tsconfig.json     # TypeScript configuration
│
├── db/                   # Database files (docker volume)
│
├── .devcontainer/        # Development container config
├── docker-compose.yml    # Container orchestration
├── SPEC.md              # Technical specification
├── CLAUDE.md            # Development guidance
└── README.md            # This file
```

## Configuration

### Single User Application

Reciepto is designed as a single-user application with no authentication system. All API keys and credentials are stored as environment variables.

### Default Categories

The application seeds the following categories on first run:
- Groceries
- Dining
- Transportation
- Utilities
- Entertainment
- Healthcare
- Clothing
- Home & Garden
- Personal Care
- Shopping
- Other

You can customize these categories through the Settings page.

## Development

### Frontend Development

All frontend commands run from `/workspace/frontend`:

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

### Backend Development

All backend commands run from `/workspace/api`:

```bash
fastapi dev main.py   # Development server with auto-reload
fastapi run main.py   # Production server
```

### API Documentation

FastAPI provides automatic interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Receipt Management
- `POST /receipts/upload` - Upload and process receipt
- `GET /receipts` - List all receipts (paginated)
- `GET /receipts/{id}` - Get receipt details with line items
- `PATCH /receipts/{id}` - Update receipt data

### Analytics
- `GET /analytics/spending` - Aggregated spending data
- `GET /analytics/export` - Export data to CSV

For detailed API schemas and response codes, see the [API Documentation](http://localhost:8000/docs) or [SPEC.md](/SPEC.md).

## Testing

### Frontend Tests

```bash
cd frontend
npm test              # Run Jest tests
npm test -- --watch   # Watch mode
npm test -- --coverage # Coverage report
```

**Framework**: Jest + React Testing Library
**Mocking**: MSW (Mock Service Worker) for API calls

### Backend Tests

```bash
cd api
source .venv/bin/activate
pytest                 # Run all tests
pytest -v             # Verbose output
pytest --cov          # Coverage report
```

**Framework**: pytest + pytest-asyncio
**Mocking**:
- AWS Textract via `moto` library
- LLM APIs via custom fixtures
- Database via test containers

See [SPEC.md - Section 7](/SPEC.md#7-testing-strategy) for detailed testing strategies.

## LangGraph Workflow

The receipt processing pipeline uses a stateful LangGraph workflow:

1. **OCR Node**: Extracts raw text using AWS Textract
2. **Extraction Node**: LLM processes OCR output to extract structured data
3. **Validation Node**: Validates data integrity and consistency
4. **Persistence Node**: Saves to PostgreSQL

The workflow includes self-correction loops and can flag receipts for manual review when validation fails.

## Troubleshooting

### Common Issues

**Issue**: Upload fails with "Processing..." stuck
- Check that the backend is running on port 8000
- Verify AWS Textract credentials are valid
- Check backend logs: `docker-compose logs backend`

**Issue**: Frontend can't connect to API
- Ensure CORS is properly configured in FastAPI
- Verify both services are running
- Check that ports 3000 and 8000 are not blocked

**Issue**: Database connection errors
- Verify PostgreSQL is running: `docker-compose ps`
- Check DATABASE_URL environment variable
- Ensure database migrations have run

**Issue**: LLM extraction fails
- Verify API keys are set correctly
- Check API rate limits haven't been exceeded
- Review backend logs for specific error messages

### Getting Help

1. Check the [Technical Specification](SPEC.md) for implementation details
2. Review [Development Guidelines](CLAUDE.md) for workflow guidance
3. Check API documentation at http://localhost:8000/docs
4. Review application logs: `docker-compose logs -f`

## Contributing

This is a single-user application designed for personal receipt management. For customization and feature requests, modify the source code according to the technical specification in [SPEC.md](SPEC.md).

## License

[Specify your license here]

## Architecture Notes

- **Single User**: No authentication or multi-user support
- **Async Processing**: Receipt processing runs as background tasks to prevent timeouts
- **Stateful Workflows**: LangGraph manages complex multi-step processing pipelines
- **Data Normalization**: LLM normalizes merchant names and categorizes items automatically
- **Self-Correction**: Workflow can retry extraction if validation fails

---

For detailed technical specifications, see [SPEC.md](SPEC.md).
For development guidance, see [CLAUDE.md](CLAUDE.md).
