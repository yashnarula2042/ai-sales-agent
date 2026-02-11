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

## 4. Deploy on Railway (Recommended)
1. Log in to [Railway.app](https://railway.app/).
2. Click **+ New Project** and select **Deploy from GitHub repo**.
3. Select your **`ai-sales-agent`** repository.
4. Click **Deploy Now**.
5. Once the project is created, go to the **Variables** tab and add:
   - `GEMINI_API_KEY`: Your key
   - `SENDER_NAME`: Your name
   - `SENDER_EMAIL`: Your email
   - `SMTP_SERVER`: `smtp.gmail.com`
   - `SMTP_PORT`: `587`
   - `SMTP_USERNAME`: Your email
   - `SMTP_PASSWORD`: Your App Password
   - `MEETING_LINK`: Your booking link
6. Railway will automatically detect the `Procfile` and redeploy.
7. Go to the **Settings** tab, find the **Networking** section, and click **Generate Domain** to get your public URL.

## 5. Alternative: Deploy on Render
(Instructions for Render are still available if needed in the previous version of this guide).

## 4. Verification
- Once the build is complete, Render will provide a URL (e.g., `https://ai-sales-agent.onrender.com`).
- Navigate to the URL to access your Soft UI Dashboard online!

> [!WARNING]
> **Data Persistence**: Local storage on Render's free tier is ephemeral. Uploaded CSVs and lead history will reset on every redeploy. For long-term data, connect to a Render PostgreSQL service.
