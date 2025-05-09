# PM Assist Dashboard

An AI-powered dashboard that provides real-time visibility into project metrics and component-wise work distribution through interactive visualizations and automated email notifications. Built using Streamlit and JIRA integration, this tool streamlines project management by offering dynamic filtering, automated reminders, and actionable insights for maintaining proper ticket categorization.

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   JIRA_URL=your_jira_url
   JIRA_EMAIL=your_jira_email
   JIRA_TOKEN=your_jira_token
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_specific_password
   SENDER_EMAIL=your_email@gmail.com
   ```
4. Run the dashboard:
   ```bash
   streamlit run dashboard.py
   ```

## Features

- Real-time JIRA data visualization
- Component-wise work distribution
- Automated email notifications for tickets without components
- Dynamic filtering by date range and components
- Interactive charts and tables
- Detailed issue tracking 