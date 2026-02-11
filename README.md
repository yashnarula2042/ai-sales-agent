# AI Cold Email Sales Agent

A powerful, automated agent that personalizes cold emails using AI and sends them to your leads to convert them into clients for website design services.

## Features
- **CSV Lead Import**: Easily upload your warm leads.
- **AI Personalization**: Uses GPT-4o to write unique, high-converting emails for each lead.
- **Automated Delivery**: Sends emails via SMTP (Gmail, Outlook, etc.).
- **Modern Dashboard**: Monitor your pipeline and stats in real-time.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   - Copy `.env.example` to `.env`.
   - Add your `OPENAI_API_KEY`.
   - Add your SMTP credentials (for Gmail, use an [App Password](https://myaccount.google.com/apppasswords)).

3. **Run the Dashboard**:
   ```bash
   python -m src.app
   ```
   Open `http://localhost:5000` in your browser.

4. **Import Leads**:
   - Prepare a CSV with at least an `email` column.
   - Upload it via the dashboard.

5. **Start Automation**:
   - Click "Start Automation Cycle" to begin the email outreach.

## Project Structure
- `src/`: Core logic and dashboard.
- `data/`: Database and uploaded CSVs.
- `logs/`: Application logs.
