# Online Shoppers Intention Prediction

A machine learning project to predict online shoppers' purchase intention using classification models and advanced data analysis techniques.

## 📋 Project Overview

This project analyzes online shopping behavior and builds predictive models to identify customers likely to make a purchase. It includes comprehensive exploratory data analysis (EDA), data preprocessing, model training, optimization, and interactive visualizations.

**Dataset**: Online Shoppers Purchasing Intention Dataset  
**Target**: Revenue (binary classification - purchase/no purchase)

## 📁 Project Structure

```
final_makine/
├── README.md                          # Project documentation
├── app.py                             # Main application
├── project_presentation.ipynb         # Interactive presentation notebook
├── online_shoppers_intention.csv      # Raw dataset
│
├── agents/                            # Expert agent guides for each phase
│   ├── dataprep-expert-agent.md       # Data preparation guidelines
│   ├── eda-expert-agent.md            # EDA guidelines
│   ├── model-expert-agent.md          # Model training guidelines
│   ├── deployment-expert-agent.md     # Deployment guidelines
│   └── sunum-dosyası-hazırlama-agent.md
│
├── data/                              # Data directory
│   ├── raw/                           # Original dataset
│   ├── processed/                     # Cleaned and preprocessed data
│   └── model_ready/                   # Train/test splits (X_train, X_test, y_train, y_test)
│
├── scripts/                           # Python scripts for pipeline
│   ├── phase1_data_overview.py        # Data loading and overview
│   ├── phase2_univariate.py           # Single variable analysis
│   ├── phase3_bivariate.py            # Two-variable relationships
│   ├── phase4_multivariate.py         # Multiple variable analysis
│   ├── dataprep_pipeline.py           # Data preprocessing
│   ├── model_training.py              # Model training and evaluation
│   ├── run_optimization.py            # Model optimization
│   └── [other utility scripts]
│
├── figures/                           # Generated visualizations (HTML)
│   ├── phase2_*.html                  # Univariate analysis plots
│   ├── phase3_*.html                  # Bivariate analysis plots
│   ├── phase4_correlation_matrix.html # Correlation heatmap
│   ├── single_roc_curve.html          # ROC curve
│   ├── single_pr_curve.html           # Precision-Recall curve
│   └── [other metrics/plots]
│
├── models/                            # Trained models and results
│   ├── all_model_results.csv          # Model comparison results
│   └── threshold_config.json          # Optimal threshold configuration
│
└── reports/                           # Exported reports
    ├── csv/                           # Tabular reports
    └── markdown/                      # Markdown formatted reports
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Virtual environment (venv or conda)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd final_makine
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 📊 Project Phases

### Phase 1: Data Overview
- Load and explore the raw dataset
- Display basic statistics and data types
- Check for missing values
- **Script**: `scripts/phase1_data_overview.py`

### Phase 2: Univariate Analysis
- Analyze individual features
- Create histograms and bar plots
- Examine distributions by revenue
- **Script**: `scripts/phase2_univariate.py`

### Phase 3: Bivariate Analysis
- Analyze relationships between pairs of variables
- Create boxplots and scatter plots
- Examine feature importance relative to target
- **Script**: `scripts/phase3_bivariate.py`

### Phase 4: Multivariate Analysis
- Study complex relationships between multiple features
- Generate correlation matrices
- Create advanced visualizations
- **Script**: `scripts/phase4_multivariate.py`

### Data Preprocessing
- Handle missing values
- Remove outliers
- Feature scaling and normalization
- Encode categorical variables
- **Script**: `scripts/dataprep_pipeline.py`

### Model Training & Evaluation
- Train multiple classification models
- Evaluate performance metrics (accuracy, precision, recall, F1, ROC-AUC)
- Create ROC and Precision-Recall curves
- Generate confusion matrices
- **Script**: `scripts/model_training.py`

### Model Optimization
- Fine-tune model hyperparameters
- Optimize decision thresholds for recall/precision trade-offs
- Generate optimization reports
- **Script**: `scripts/run_optimization.py`

## 🔧 Usage

### Run the complete pipeline:
```bash
python scripts/dataprep_pipeline.py
python scripts/model_training.py
python scripts/run_optimization.py
```

### View the interactive presentation:
```bash
jupyter notebook project_presentation.ipynb
```

### Run the main application:
```bash
python app.py
```

### Generate visualizations:
```bash
python scripts/export_separated_figures.py
```

## 📈 Key Results

- **Models Trained**: Multiple classification models (Logistic Regression, Random Forest, Gradient Boosting, etc.)
- **Best Performance**: Detailed results stored in `models/all_model_results.csv`
- **Visualizations**: 20+ interactive HTML plots in `figures/` directory
- **Optimal Threshold**: Configured in `models/threshold_config.json`

## 📊 Data Description

**Dataset**: Online Shoppers Purchasing Intention Dataset  
**Samples**: ~12,330 sessions  
**Features**: 17 numerical and categorical features
- Session Duration, Page Values, Bounce Rates, Exit Rates
- Product-related information
- Visitor type, month, weekend indicator, traffic source
- Special day indicator, browser, operating system, region

**Target Variable**: 
- `Revenue`: Binary (Yes=1 / No=0) - whether a session resulted in a purchase

## 📁 Data Splits

```
data/model_ready/
├── X_train.csv        # Training features
├── X_test.csv         # Test features
├── y_train.csv        # Training labels
└── y_test.csv         # Test labels
```

## 📑 Reports and Analysis

- Detailed analysis reports in `reports/markdown/` directory
- CSV exports of intermediate results in `reports/csv/` directory
- Prediction results in `analysis_history/predictions.csv`

## 🤝 Expert Agents

This project includes specialized agent guides for different phases:
- **Data Preparation Expert**: Guidelines for data cleaning and preprocessing
- **EDA Expert**: Best practices for exploratory data analysis
- **Model Expert**: Model selection and training strategies
- **Deployment Expert**: Production deployment guidelines

Refer to the files in `agents/` directory for detailed guidance.

## 📝 Notebooks

- **project_presentation.ipynb**: Interactive presentation with all analyses and results
- **scripts/recall_optimization.ipynb**: Detailed recall optimization analysis
- **scripts/final_evaluation_dashboard.ipynb**: Comprehensive evaluation dashboard

## 🔍 Analysis History

Previous predictions and analyses are stored in `analysis_history/predictions.csv`

## 📦 Output Files

### Visualizations (HTML)
- Distribution plots
- Correlation matrices
- ROC curves
- Precision-Recall curves
- Confusion matrices
- Performance metrics summaries

### Models
- All trained models with evaluation metrics
- Optimal threshold configuration for decision-making

### Reports
- Detailed markdown reports
- CSV exports of analysis results

## 🛠️ Utilities

Several utility scripts available:
- `fix_notebook_markdown.py`: Notebook markdown formatting
- `convert_prints_to_markdown.py`: Convert print statements to markdown
- `save_processed_data.py`: Save processed datasets
- `add_learning_curve.py`: Add learning curves to analysis
- And more...

## 📋 Requirements

Main dependencies (see `requirements.txt` for complete list):
- pandas
- numpy
- scikit-learn
- matplotlib
- seaborn
- plotly
- jupyter

## 📄 License

This project is for educational and research purposes.

## ✅ Next Steps

1. Review the project structure and data
2. Run the data preparation pipeline
3. Explore the interactive presentation notebook
4. Review expert agent guides for your area of focus
5. Run model training and optimization
6. Deploy using guidelines from deployment expert

---

**Last Updated**: June 2026  
**Project Status**: Active Development
