# 📈 Dynamic Stock Portfolio Analyser

A professional, interactive financial dashboard built using **Streamlit** and **Plotly** to analyze stock performance, compute risk-return metrics, and optimize multi-asset portfolios using real financial mathematics.

---

## 📌 Project Description

This project allows users to upload stock data and perform advanced portfolio analysis including:

* 📊 Risk vs Return calculations
* 🔗 Covariance & Correlation matrix
* ⚖️ Portfolio optimization
* 📈 Efficient Frontier visualization
* ⭐ Sharpe Ratio maximization

It simulates real-world financial analytics used in portfolio management.

---

## ✨ Features

### 🔥 1. Dynamic Multi-Asset Portfolio

* Supports multiple companies (2–10 assets)
* Upload separate CSV files for each company
* Automatic **date alignment across assets**
* Calculates:

  * Covariance Matrix
  * Correlation Matrix
  * Portfolio Risk & Return
* Generates **Efficient Frontier (Monte Carlo Simulation)**
* Finds **Optimal Portfolio (Max Sharpe Ratio)**

---

### 📊 2. Case Study (2 Assets)

* Compare two assets (e.g., KO vs MSFT)
* Calculates:

  * Mean Return
  * Risk (Standard Deviation)
  * Covariance & Correlation
* Interactive weight-based portfolio analysis

---

### 📈 3. Single Stock Deep Dive

* Upload any stock CSV
* Auto-detect columns (Date, Price, Dividend)
* Calculates:

  * Returns
  * CAGR
  * Risk
  * Coefficient of Variation

---

## 🧠 How It Works

* **Data Processing:**
  Uses pandas to clean, align, and process financial data.

* **Mathematics Used:**

  * Portfolio Return = weighted sum of returns
  * Portfolio Risk = √(wᵀ Σ w)
  * Covariance Matrix for multi-asset interaction
  * Monte Carlo simulation for Efficient Frontier

* **Visualization:**
  Interactive charts using Plotly for deep analysis.

---

## 🛠️ Tech Stack

* Python
* Streamlit
* Pandas
* NumPy
* Plotly

---

## 🚀 How to Run the Project

### Step 1: Clone the Repository

```bash
git clone https://github.com/93527Rupali38898/stock-portfolio-analyser.git
cd stock-portfolio-analyser
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run the Application

```bash
streamlit run stock_analysis_app.py
```

👉 The app will open automatically in your browser at:
http://localhost:8501

---

## 📂 Input Format

### Multi-Asset Mode

CSV must contain:

* Date
* Closing Price
* (Optional) Dividend

---

### Case Study Mode

CSV format:

```
Year | Asset1 Returns | Asset2 Returns
```

---

## 🎯 Key Highlights

* Real financial mathematics
* Dynamic portfolio size

---

## 👩‍💻 Author

**Rupali Goyal**

---

## 📌 Note

This project is built for educational and financial data analysis purposes.

---
