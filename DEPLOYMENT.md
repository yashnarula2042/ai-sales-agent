# Deployment Guide: AI Sales Agent Dashboard

Follow these steps to deploy your AI Sales Agent online using **Render** (Recommended) or **Railway**.

## 1. Prerequisites
- A **GitHub** account.
- A **Render.com** account (Free tier is sufficient).
- Your [GEMINI_API_KEY](https://aistudio.google.com/app/apikey).
- SMTP Credentials (e.g., App Password for Gmail).

## 2. Prepare Repository
1. Initialize a git repository in your project folder:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for deployment"
   ```
2. Create a new repository on GitHub and push your code:
   ```bash
   git remote add origin YOUR_GITHUB_REPO_URL
   git branch -M main
   git push -u origin main
   ```

## 3. Deploy on Render
1. Log in to [Render](https://dashboard.render.com/).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub repository.
4. **Configuration Settings**:
   - **Name**: `ai-sales-agent`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class eventlet -w 1 src.app:app`
5. **Environment Variables**: Click **Advanced** and add your `.env` variables:
   - `GEMINI_API_KEY`: Your key
   - `SENDER_NAME`: Your name
   - `SENDER_EMAIL`: Your email
   - `SMTP_SERVER`: `smtp.gmail.com`
   - `SMTP_PORT`: `587`
   - `SMTP_USERNAME`: Your email
   - `SMTP_PASSWORD`: Your App Password
   - `MEETING_LINK`: Your booking link
6. Click **Create Web Service**.

## 4. Verification
- Once the build is complete, Render will provide a URL (e.g., `https://ai-sales-agent.onrender.com`).
- Navigate to the URL to access your Soft UI Dashboard online!

> [!WARNING]
> **Data Persistence**: Local storage on Render's free tier is ephemeral. Uploaded CSVs and lead history will reset on every redeploy. For long-term data, connect to a Render PostgreSQL service.
