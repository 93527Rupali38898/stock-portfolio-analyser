# 📈 Wealth Portfolio Analyzer

A comprehensive financial analytics dashboard built using Streamlit that enables users to analyze and optimize investment portfolios across **stocks, mutual funds, and fixed deposits (FDs)**.

The application applies real-world quantitative finance concepts such as **risk-return analysis, portfolio optimization, and Monte Carlo simulation** in an interactive and user-friendly environment.

---

## 📌 Overview

This project provides a unified platform to:

* Analyze performance of multiple asset classes
* Compare risk and return across investments
* Construct and optimize portfolios
* Simulate real-world financial decision-making

It reflects practical implementation of **Modern Portfolio Theory (MPT)**.

---

## 🚀 Key Features

### 🔥 1. Dynamic Multi-Asset Portfolio

* Combine **stocks, mutual funds, and fixed deposits**
* Flexible portfolio construction
* Automatic data alignment across assets
* Computes:

  * Portfolio Return
  * Portfolio Risk
  * Covariance Matrix
  * Correlation Matrix
* Efficient Frontier using Monte Carlo simulation
* Identifies **Optimal Portfolio (Max Sharpe Ratio)**

---

### ⚖️ 2. Asset Pair Optimizer

* Compare any two assets
* Calculates:

  * Mean Return
  * Risk (Standard Deviation)
  * Covariance
* Interactive weight-based portfolio adjustment

---

### 📊 3. Single Stock Deep Dive

* Upload stock CSV data
* Automatic column detection
* Calculates:

  * Returns
  * CAGR
  * Annualized Risk
  * Coefficient of Variation

---

### 🏦 4. Mutual Fund Deep Dive

* Upload NAV-based data
* Specialized mutual fund analysis
* Calculates:

  * CAGR
  * Risk
  * Performance metrics

---

### 🛡️ 5. Fixed Deposit (FD) Analysis

* Analyze risk-free investment growth
* Calculates:

  * Maturity Amount
  * Interest Earned
* Supports:

  * Monthly / Quarterly / Annual compounding
* Visualizes FD growth over time

---

### 🎨 6. Interactive Dashboard

* Built with Streamlit
* Adaptive Light/Dark UI
* Interactive charts using Plotly
* Dynamic metric cards and analytics panels

---

## 🧠 Financial Concepts Implemented

* Portfolio Return (Weighted Mean)
* Portfolio Risk: √(wᵀ Σ w)
* Covariance & Correlation
* Monte Carlo Simulation
* Efficient Frontier
* Sharpe Ratio Optimization
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
* Converts price data into return series
* Aligns multiple assets into a common timeline
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

### Multi-Asset Mode

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
* Statistical Computation
* Multi-Asset Investment Analysis
* Dashboard Development

---

## 👩‍💻 Author

Rupali Goyal

---

## 📌 Note

This project is intended for educational purposes and financial data analysis.
