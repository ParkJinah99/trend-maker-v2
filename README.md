# trend-maker-v2

Sure! Here's your complete `README.md` content in markdown format — you can copy and paste it directly:

```markdown
# 🚀 TrendMaker — Local Development Setup

This project includes a FastAPI backend and a React frontend. Follow the instructions below to run everything locally for development and testing.

---

## 📦 Project Structure

```

trend-maker-v2/
├── backend/
│   ├── main.py
│   ├── agents.py
│   └── ...
├── frontend/
│   ├── package.json
│   └── ...
└── README.md

````

---

## 🐍 Backend (FastAPI)

### ▶️ How to Run the Backend

1. Open a terminal and navigate to the backend folder:

```bash
cd backend
````

2. Create and activate a Python virtual environment:

```bash
# Create venv (only once)
python -m venv venv

# Activate venv (Windows)
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the FastAPI server:

```bash
uvicorn main:app --reload
```

5. Open your browser to:

```
http://localhost:8000/docs
```

> ✅ You should see the FastAPI Swagger UI

---

## 💻 Frontend (React)

### ▶️ How to Run the Frontend

1. Open a **new terminal** and navigate to the frontend folder:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the frontend development server:

```bash
npm run dev
```

4. Open your browser:


> ✅ You should see the frontend application running

---

## 🧪 Development Tips

* Keep the backend and frontend running in **separate terminals**
* Make sure your backend uses **local imports** (e.g., `from agents import run_multi_agent`) so it works when running inside `backend/`
* If your frontend makes API calls, ensure CORS is enabled in the FastAPI backend

---

## 🛠 Troubleshooting

* If `uvicorn` is not recognized, make sure your virtual environment is activated
* If you get `ModuleNotFoundError`, check your import paths or try running from the project root
* For API errors from the frontend, verify the backend is running on port `8000`

---

## ✅ You're Ready to Go!

Once both servers are running, you can start developing and testing your application locally.

```

Let me know if you want to include `requirements.txt`, `.env` setup, or any DB instructions too!
```
