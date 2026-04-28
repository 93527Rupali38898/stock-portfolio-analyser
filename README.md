# 📈 Wealth Portfolio Analyzer

A comprehensive financial analytics dashboard built using Streamlit that enables users to analyze and optimize investment portfolios across **stocks, mutual funds, and fixed deposits (FDs)**.

The application integrates real-world quantitative finance techniques such as **risk-return analysis, portfolio optimization, and Monte Carlo simulation** into an interactive platform.

---

## 📌 Overview

The Wealth Portfolio Analyzer provides a unified system to:

* Analyze performance across multiple asset classes
* Compare investment risk and return
* Construct and optimize portfolios dynamically
* Simulate real-world financial decision-making

It is a practical implementation of **Modern Portfolio Theory (MPT)**.

---

## 🚀 Key Features

### 🔥 1. Dynamic Multi-Asset Portfolio (All Combined)

* Combine **stocks, mutual funds, and fixed deposits**
* Flexible asset allocation
* Automatic data alignment across datasets
* Computes:

  * Portfolio Return
  * Portfolio Risk
  * Covariance Matrix
  * Correlation Matrix
* Efficient Frontier using Monte Carlo simulation
* Identifies **Optimal Portfolio (Maximum Sharpe Ratio)**

---

### 📊 2. Multi-Stock Portfolio

* Analyze multiple stocks together
* Risk-return evaluation across stocks
* Portfolio optimization using covariance

---

### 🏦 3. Multi-Mutual Fund Portfolio

* Analyze multiple mutual funds simultaneously
* NAV-based performance evaluation
* Portfolio risk and diversification analysis

---

### ⚖️ 4. Asset Pair Comparison

* Compare any two assets
* Calculates:

  * Mean Return
  * Risk (Standard Deviation)
  * Covariance
* Interactive portfolio weight adjustment

---

### 📈 5. Single Stock Deep Dive

* Upload stock CSV data
* Automatic column detection
* Calculates:

  * Returns
  * CAGR
  * Annualized Risk
  * Coefficient of Variation

---

### 📉 6. Single Mutual Fund Deep Dive

* Upload NAV data
* Calculates:

  * CAGR
  * Risk
  * Performance metrics

---

### 🛡️ 7. Fixed Deposit (FD) Analysis

* Models risk-free investment growth
* Calculates:

  * Maturity Amount
  * Interest Earned
* Supports:

  * Monthly / Quarterly / Annual compounding
* Visualizes FD growth trajectory

---

### 🎨 Interactive Dashboard

* Built using Streamlit
* Clean and responsive UI
* Dynamic charts using Plotly
* Metric cards for quick insights

---

## 🧠 Financial Concepts Implemented

* Portfolio Return (Weighted Mean)
* Portfolio Risk: √(wᵀ Σ w)
* Covariance & Correlation
* Monte Carlo Simulation
* Efficient Frontier
* Sharpe Ratio (Risk-Adjusted Return)
* CAGR (Compound Annual Growth Rate)
* Compound Interest (FD Modeling)

---

## 🛠️ Tech Stack

* Python
* Streamlit
* Pandas
* NumPy
* Plotly

---

## ⚙️ How It Works

* Automatically detects **Date, Price/NAV, Dividend columns**
* Converts raw financial data into return series
* Aligns multiple assets on a common timeline
* Integrates fixed deposits as **risk-free assets (zero variance)**
* Uses statistical models to compute portfolio metrics
* Simulates thousands of portfolios to identify optimal allocation

---

## 🚀 How to Run the Project

### 1. Clone Repository

git clone https://github.com/93527Rupali38898/stock-portfolio-analyser.git
cd stock-portfolio-analyser

### 2. Install Dependencies

pip install -r requirements.txt

### 3. Run Application

streamlit run stock_analysis_app.py

👉 Open in browser: http://localhost:8501

---

## 📂 Input Format

### Multi-Asset / Stock / Mutual Fund Modes

CSV must contain:

* Date
* Closing Price / NAV
* (Optional) Dividend

---

### Case Study Mode

Year | Asset1 Returns | Asset2 Returns

---

## 🧠 Skills Demonstrated

* Financial Modeling
* Portfolio Optimization
* Data Analysis
* Statistical Computing
* Multi-Asset Investment Analysis
* Interactive Dashboard Development

---

## 👩‍💻 Author

Rupali Goyal

---

## 📌 Note

This project is intended for educational purposes and financial data analysis.
