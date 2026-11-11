# 📶 PakSim Insights & AI Telecom Hub

An advanced Python Streamlit application that detects mobile network operators in Pakistan (Jazz, Zong, Ufone, Telenor, SCOM) by phone number prefix, tracks bundle metrics (remaining MBs, on-net/off-net minutes, SMS), visualizes 7-day data consumption history, and leverages **Google AI Studio (Gemini 2.5 Flash)** to analyze package confirmation SMS and recommend optimal telecom bundles.

## 📑 Table of Contents

1. [Key Features](#-key-features)

2. [Telecom Privacy & Architecture Note](#-telecom-privacy--architecture-note)

3. [Project Structure](#-project-structure)

4. [Pakistani Mobile Prefix Allocation](#-pakistani-mobile-prefix-allocation)

5. [Prerequisites & Requirements](#-prerequisites--requirements)

6. [Step-by-Step GitHub & Local Setup Guide](#-step-by-step-github--local-setup-guide)

7. [Deploying to Streamlit Cloud](#-deploying-to-streamlit-cloud)

8. [License](#-license)

## 🌟 Key Features

* **Automated Network Identification:** Instantly identifies whether an 11-digit Pakistani number (`03XXXXXXXXX` or `+923XXXXXXXXX`) belongs to **Jazz**, **Zong**, **Ufone**, **Telenor**, or **SCOM**.

* **Real-Time Bundle & Quota Dashboard:** Displays current data balance (MBs/GBs), on-net calling minutes, off-net calling minutes, and remaining SMS with visual progress gauges.

* **7-Day Consumption Analytics:** Interactive stacked bar and donut charts powered by Plotly displaying day vs. night data usage and category breakdowns (Social, Video, Web, Gaming).

* **Official USSD & Customer Service Hub:** Provides quick dial codes (`*111#`, `*102#`, `*124#`, `*444#`) and helpline numbers for each carrier.

* **AI Telecom Studio (Gemini AI via Google AI Studio):**

  * **SMS Parser:** Paste carrier confirmation SMS to extract bundle quotas, validity, and expiry automatically.

  * **AI Package Advisor:** Recommends tailored 4G/5G data and calling bundles based on budget and priorities.

  * **Q&A Assistant:** Answers technical telecom questions (APN configuration, 4G troubleshooting, tax deductions).

## 🔒 Telecom Privacy & Architecture Note

> **Important Developer Context:**
> Under Pakistan Telecommunication Authority (PTA) regulations and telecom privacy standards, mobile network operators (Jazz, Telenor, Zong, Ufone) **do not offer public, unauthenticated APIs** that allow external third parties to fetch private subscriber balances, live call logs, or data consumption records simply by typing a phone number. Doing so would violate subscriber confidentiality.
>
> Official carrier applications (Jazz World, My Zong, My Ufone, My Telenor) require an **SMS OTP (One-Time Password)** sent to the active SIM card to authorize access. This application provides:
>
> 1. Exact PTA prefix-based carrier detection.
>
> 2. Direct USSD codes for live operator verification.
>
> 3. An intelligent SMS parsing engine that lets subscribers paste their network's balance/bundle SMS for instant structured AI tracking.
>
> 4. Deterministic usage simulation and visualization for monitoring weekly consumption patterns.

## 📂 Project Structure

```
paksim-insights/
├── app.py                # Main Streamlit application source code
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation and setup guide
└── .env                  # (Optional) Local environment variable file for GEMINI_API_KEY

```

## 📞 Pakistani Mobile Prefix Allocation

| Operator | Primary Prefixes | Balance USSD | Helpline | 
| ----- | ----- | ----- | ----- | 
| **Jazz / Warid** | `0300` - `0309`, `0320` - `0325` | `*111#` / `*117*2#` | 111 | 
| **Zong 4G** | `0310` - `0318` | `*222#` / `*102#` | 310 | 
| **Ufone 4G** | `0330` - `0337` | `*124#` / `*706#` | 333 | 
| **Telenor 4G** | `0340` - `0349` | `*444#` / `*999#` | 345 | 
| **SCOM (AJK & GB)** | `0355` | `*125#` | 111-726-626 | 

*Note: If a number was ported via Mobile Number Portability (MNP), the prefix denotes the original issuing network.*

## 🛠️ Prerequisites & Requirements

* Python 3.9, 3.10, or 3.11 installed on your system.

* Git installed on your computer ([Download Git](https://git-scm.com/)).

* A free Google AI Studio API key ([Get API Key](https://aistudio.google.com/)).

## 🚀 Step-by-Step GitHub & Local Setup Guide

### Step 1: Clone or Create Local Project Folder

Open your terminal or command prompt (CMD / PowerShell / Bash):

```
mkdir paksim-insights
cd paksim-insights

```

### Step 2: Create the Three Core Files

Create `app.py`, `requirements.txt`, and `README.md` inside this directory and copy their respective code.

### Step 3: Set Up a Python Virtual Environment

It is best practice to use an isolated virtual environment:

```
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS / Linux
python3 -m venv venv
source venv/bin/activate

```

### Step 4: Install Dependencies

Install all required libraries using `pip`:

```
pip install -r requirements.txt

```

### Step 5: (Optional) Configure Gemini API Key

Create a `.env` file in the project root:

```
GEMINI_API_KEY="your_actual_google_ai_studio_api_key_here"

```

*(Alternatively, you can paste the key directly into the Streamlit sidebar inside the app.)*

### Step 6: Test Locally

Launch the Streamlit development server:

```
streamlit run app.py

```

Your browser will open automatically at `http://localhost:8501`.

## 🐙 Publishing to GitHub

Follow these steps to upload your project to GitHub:

### 1. Initialize Local Git Repository

```
git init

```

### 2. Create a `.gitignore` File

Ensure your virtual environment and sensitive API keys are not pushed to GitHub:

```
# Create .gitignore
echo "venv/" >> .gitignore
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore

```

### 3. Stage and Commit Files

```
git add .
git commit -m "Initial commit: PakSim Network & AI Telecom Hub"

```

### 4. Create a Remote Repository on GitHub

1. Log in to [GitHub](https://github.com).

2. Click the **+** icon in the top right corner and select **New repository**.

3. Name your repository (e.g., `paksim-insights`).

4. Keep it **Public** (or Private) and leave README unchecked.

5. Click **Create repository**.

### 5. Link Local Repository to GitHub and Push

Replace `<YOUR_USERNAME>` with your GitHub username:

```
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/paksim-insights.git
git push -u origin main

```

## ☁️ Deploying to Streamlit Cloud (Free)

1. Navigate to [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.

2. Click **New app**.

3. Select your repository (`paksim-insights`), branch (`main`), and main file path (`app.py`).

4. Under **Advanced settings**, add your secret key:

   ```
   GEMINI_API_KEY = "your_google_ai_studio_api_key_here"
   
   ```

5. Click **Deploy!** Your app will be live with a shareable public URL.

## 📄 License

This project is open-source and distributed under the MIT License.