# Data Quality Platform

> Intelligent data cleaning and quality assurance platform for structured datasets with ML-powered inconsistency detection and automatic remediation.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Language: Python](https://img.shields.io/badge/Language-Python-3776ab.svg)
![Frontend: React](https://img.shields.io/badge/Frontend-React-61dafb.svg)
![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen.svg)

---

## 🎯 Problem

Data quality is critical for machine learning and business intelligence, yet most datasets suffer from:
- Missing values and inconsistencies
- Duplicate records and corrupted data
- Outliers and anomalies
- Type mismatches and formatting issues
- No visibility into data quality metrics

Manual data cleaning is tedious, error-prone, and not scalable.

---

## ✨ Solution

An intelligent, full-stack data quality platform that:
- **Automatically detects** inconsistencies and data quality issues
- **Intelligently cleans** structured datasets with ML-based remediation
- **Visualizes** data quality metrics and provides actionable insights
- **Validates** data schema and content compliance
- **Generates reports** on data quality improvements

---

## 🚀 Features

- ✅ Automated inconsistency detection
- ✅ Intelligent data cleaning and remediation
- ✅ Missing value handling (imputation, deletion strategies)
- ✅ Duplicate record detection and removal
- ✅ Outlier detection and handling
- ✅ Data type validation and conversion
- ✅ Interactive web dashboard for data exploration
- ✅ Quality metrics and reporting
- ✅ Batch processing for large datasets
- ✅ Data profiling and statistics

---

## 🛠️ Tech Stack

### Backend
| Component | Technology |
|-----------|------------|
| **Runtime** | Python 3.9+ |
| **Framework** | Flask / FastAPI |
| **Data Processing** | Pandas, NumPy |
| **ML / Analysis** | Scikit-learn |
| **Database** | PostgreSQL / MongoDB |

### Frontend
| Component | Technology |
|-----------|------------|
| **Framework** | React 18+ |
| **Bundler** | Vite |
| **UI Library** | React Components |
| **Visualization** | Chart.js / Recharts |

---

## 📂 Project Structure

```
data-quality-platform/
├── backend/
│   ├── app/
│   │   ├── api/              # REST API endpoints
│   │   ├── models/           # Data models
│   │   ├── services/         # Business logic
│   │   └── utils/            # Utilities
│   ├── ml/
│   │   ├── cleaners/         # Data cleaning modules
│   │   ├── detectors/        # Issue detection
│   │   └── validators/       # Data validation
│   ├── requirements.txt      # Python dependencies
│   └── config.py             # Configuration
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API services
│   │   └── styles/           # CSS styles
│   ├── package.json          # npm dependencies
│   └── vite.config.js        # Vite configuration
├── docs/                     # Documentation
├── LICENSE                   # MIT License
├── .gitignore               # Git ignore rules
├── CONTRIBUTING.md          # Contribution guidelines
└── README.md                # This file
```

---

## 📋 Prerequisites

- Python 3.9+
- Node.js 16+ and npm
- PostgreSQL or MongoDB (optional for data storage)

---

## 🔧 Installation

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/Vijaykrishna343/data-quality-platform.git
cd data-quality-platform

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
cd backend
pip install -r requirements.txt
```

### Frontend Setup

```bash
# Install frontend dependencies
cd frontend
npm install

# Build frontend (optional)
npm run build
```

---

## 💡 Usage

### Upload and Clean Dataset

```python
from backend.app.services import DataCleaningService

# Initialize service
cleaner = DataCleaningService()

# Upload dataset
dataset = cleaner.load_csv("data/messy_data.csv")

# Analyze data quality
analysis = cleaner.analyze(dataset)
print(f"Quality Score: {analysis.quality_score}%")

# Auto-clean dataset
cleaned_data = cleaner.clean(dataset)

# Get cleaning report
report = cleaner.get_report()
print(report)

# Export cleaned data
cleaned_data.to_csv("data/cleaned_data.csv")
```

### Run Web Dashboard

```bash
# Start backend API
cd backend
python -m flask run

# In another terminal, start frontend
cd frontend
npm run dev

# Access dashboard at http://localhost:5173
```

---

## 📊 Data Quality Metrics

The platform provides:
- **Completeness**: % of non-null values
- **Uniqueness**: % of unique records
- **Validity**: % of valid data types
- **Consistency**: % of matching formats
- **Accuracy**: Confidence in data correctness
- **Overall Score**: Combined quality metric (0-100%)

---

## 🔮 Future Improvements

- [ ] Support for unstructured data (text, images)
- [ ] Advanced ML models for anomaly detection
- [ ] Real-time data quality monitoring
- [ ] Multi-database support
- [ ] Scheduling and automation
- [ ] Data lineage and provenance tracking
- [ ] Collaborative data cleaning workflows
- [ ] Custom rule engine for domain-specific validation

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ by [Vijay Krishna](https://github.com/Vijaykrishna343)**