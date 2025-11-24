# Setup Guide

## Prerequisites

- Python 3.8+
- pip
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/content-analyzer-llm.git
cd content-analyzer-llm
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the app:
```bash
streamlit run app.py
```

## Deployment

### Streamlit Cloud
1. Push to GitHub
2. Go to share.streamlit.io
3. Deploy from repository

### Docker
```bash
docker build -t content-analyzer .
docker run -p 8501:8501 content-analyzer
```

For more details, see README.md