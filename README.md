# 📈 Wealth Portfolio Analyzer

A professional financial analytics dashboard built using Streamlit that enables users to analyze and optimize portfolios across **stocks and mutual funds** using real-world quantitative finance techniques.

---

## 📌 Overview

This application provides an interactive platform to evaluate investment performance, measure risk, and construct optimal portfolios using **Modern Portfolio Theory**.

It supports both **stocks and mutual funds**, offering flexible analysis modes for beginners as well as advanced users.

---

## 🚀 Key Features

### 🔥 1. Dynamic Multi-Asset Portfolio

* Combine stocks and mutual funds in a single portfolio
* Supports 2–20 assets dynamically
* Automatic date alignment across datasets
* Computes:

  * Covariance Matrix
  * Correlation Matrix
  * Portfolio Return & Risk
* Efficient Frontier using Monte Carlo simulation
* Identifies **Optimal Portfolio (Max Sharpe Ratio)**

---

### ⚖️ 2. Asset Pair Optimizer

* Compare two assets (stocks or mutual funds)
* Calculates:

  * Mean Return
  * Risk (Standard Deviation)
  * Covariance
* Interactive weight-based portfolio analysis

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

* Upload mutual fund NAV data
* Specialized NAV-based analysis
* Calculates:

  * CAGR
  * Risk
  * Performance metrics

---

### 🎨 5. Interactive UI & Dashboard

* Adaptive Light/Dark Mode
* Custom styled metric cards
* Interactive charts using Plotly
* Tab-based analytics dashboard

---

## 🧠 Financial Concepts Implemented

* Portfolio Return (Weighted Mean)
* Portfolio Risk: √(wᵀ Σ w)
* Covariance & Correlation
* Monte Carlo Simulation
* Efficient Frontier
* Sharpe Ratio Optimization
* CAGR (Compound Annual Growth Rate)

---

## 🛠️ Tech Stack

* Python
* Streamlit
* Pandas
* NumPy
* Plotly

---

## ⚙️ How It Works

* Automatically detects **Date, Price, NAV, Dividend columns**
* Converts raw financial data into return series
* Aligns multiple assets on a common timeline
* Uses statistical methods to compute portfolio metrics
* Simulates thousands of portfolios to find optimal allocation

---

## 🚀 How to Run

git clone https://github.com/93527Rupali38898/stock-portfolio-analyser.git
cd stock-portfolio-analyser

pip install -r requirements.txt

streamlit run stock_analysis_app.py

Open in browser: http://localhost:8501

---

## 📂 Input Format

### Multi-Asset Mode

CSV must contain:

* Date
* Closing Price / NAV
* (Optional) Dividend

---

### Asset Pair Mode

Year | Asset1 Returns | Asset2 Returns

---

## 🧠 Skills Demonstrated

* Financial Modeling
* Portfolio Optimization
* Data Analysis
* Statistical Computation
* Interactive Dashboard Design
* Problem Solving with Real Data

---

## 👩‍💻 Author

Rupali Goyal

---

## 📌 Note

This project is intended for educational purposes and financial data analysis.
