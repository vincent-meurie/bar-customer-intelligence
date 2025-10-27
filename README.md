# Bar Customer Intelligence Platform

ML-powered customer analytics for bars and entertainment venues.

## Features (Planned)
- Customer Segmentation (RFM Analysis)
- Lifetime Value Prediction
- Churn Prediction
- A/B Testing Framework
- Interactive Dashboard

## Tech Stack
- Python 3.11+
- Django 5.0
- Scikit-learn
- PyTorch
- PostgreSQL (production) / SQLite (dev)

## Development Approach
Test-Driven Development (TDD)

## Setup Instructions

### 1. Clone the repository
```bash
git clone
cd bar-customer-intelligence
```

### 2. Create virtual environment (PyCharm)
1. Open PyCharm
2. File -> Open -> Select project directory
3. PyCharm will prompt to create a virtual environment
4. Or manually: `python -m venv .venv`

### 3. Activate virtual environment
** Windows (PyCharm Terminal):**
```bash
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
source .venv.bin/activate
```

### 4. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements/dev.txt
pip install -e .
```

### 5. Setup environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 6. Run tests
```bash
pytest
```