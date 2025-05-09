import streamlit as st
from jira import JIRA
import pandas as pd
from dotenv import load_dotenv
import os
import plotly.express as px
from datetime import datetime, timedelta
import plotly.graph_objects as go
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load credentials
load_dotenv()

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

# Initialize session state for page navigation and selected developer
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'selected_developer' not in st.session_state:
    st.session_state.selected_developer = None

# Custom CSS for professional styling with Paytm brand colors
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #ffffff;
        padding: 1rem;
        overflow-y: auto;
        height: 100vh;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
        padding: 1rem 0.5rem;
        overflow-y: auto;
        height: 100vh;
    }
    
    /* Content area styling */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        overflow-y: auto;
    }
    
    /* Ensure proper spacing between elements */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Make sure expander is visible */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border: 1px solid #e5e7eb;
        border-radius: 0.375rem;
        padding: 0.5rem;
        margin: 0.5rem 0;
    }
    
    /* Ensure proper height for charts */
    .stPlotlyChart {
        height: auto !important;
        min-height: 400px;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #00b9f1;  /* Paytm blue */
        color: white;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 0.375rem;
        border: none;
        transition: all 0.2s;
    }
    .stButton button:hover {
        background-color: #0095c8;  /* Darker Paytm blue */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Back to Home button styling */
    .back-home-button {
        background-color: #002e6e !important;  /* Paytm dark blue */
        color: white !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 0.375rem !important;
        border: none !important;
        position: fixed !important;
        top: 1rem !important;
        left: 1rem !important;
        z-index: 1000 !important;
        font-size: 1rem !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        transition: all 0.2s !important;
    }
    .back-home-button:hover {
        background-color: #001f4d !important;  /* Darker Paytm blue */
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Title styling */
    h1, h2, h3 {
        color: #002e6e;  /* Paytm dark blue */
        font-weight: 700;
        margin: 0.5rem 0;
    }
    h1 {
        font-size: 1.8rem;
    }
    h2 {
        font-size: 1.5rem;
    }
    h3 {
        font-size: 1.2rem;
    }
    
    /* Metric cards styling */
    .stMetric {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-left: 4px solid #00b9f1;  /* Paytm blue accent */
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background-color: white;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
        margin: 0.5rem 0;
    }
    
    /* Selectbox styling */
    .stSelectbox {
        background-color: white;
        border-radius: 0.375rem;
        border: 1px solid #e5e7eb;
        margin: 0.25rem 0;
    }
    
    /* Date input styling */
    .stDateInput {
        background-color: white;
        border-radius: 0.375rem;
        border: 1px solid #e5e7eb;
        margin: 0.25rem 0;
    }
    
    /* Success message styling */
    .stSuccess {
        background-color: #d1fae5;
        color: #065f46;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #059669;
    }
    
    /* Error message styling */
    .stError {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc2626;
    }
</style>
""", unsafe_allow_html=True)

# Create header with logo and title
def create_header(page_title):
    col1, col2, col3 = st.columns([0.15, 0.7, 0.15])
    
    # Logo in the left column
    with col1:
        try:
            st.image("static/logo.png", width=80)
        except:
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Paytm_Logo_%28standalone%29.svg/2560px-Paytm_Logo_%28standalone%29.svg.png", width=80)
    
    # Title in the center column
    with col2:
        st.markdown(f"<h1 style='text-align: center; margin: 0; padding: 0;'>{page_title}</h1>", unsafe_allow_html=True)
    
    # Empty right column for balance
    with col3:
        st.write("")

# Sidebar menu with improved styling
st.sidebar.markdown("### Menu")
st.sidebar.markdown("### Tech Alignment")
qa_util = st.sidebar.button("QA Utilisation", key="qa_util")
dev_util = st.sidebar.button("Dev Utilisation", key="dev_util")

# Initialize JIRA connection
try:
    JIRA_URL = os.getenv("JIRA_URL")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    JIRA_TOKEN = os.getenv("JIRA_TOKEN")
    
    jira = JIRA(server=JIRA_URL, token_auth=(JIRA_TOKEN))
    user = jira.current_user()
    st.sidebar.success(f"Connected to Jira as: {user}")
except Exception as e:
    st.error(f"Failed to connect to Jira: {e}")
    st.stop()

# Fetch JIRA data
try:
    JQL = 'project = PGP AND status not in (Queue) ORDER BY updated DESC'
    issues = jira.search_issues(JQL, maxResults=100)
    
    # Handle Task Category field properly
    task_category = getattr(issues[0].fields, 'customfield_21928', None)
    if task_category:
        if hasattr(task_category, 'value'):
            task_category = task_category.value
        elif hasattr(task_category, 'name'):
            task_category = task_category.name
        else:
            task_category = str(task_category)
    else:
        task_category = 'Not Set'

    # Calculate ticket aging
    try:
        created_date = datetime.strptime(issues[0].fields.created[:10], '%Y-%m-%d')
        current_date = datetime.now()
        aging_days = (current_date - created_date).days
    except Exception as e:
        aging_days = 0

    data = []
    for issue in issues:
        data.append({
            "Key": issue.key,
            "Summary": issue.fields.summary,
            "Component": getattr(issue.fields.components[0], "name", "No Component") if issue.fields.components else "No Component",
            "Status": issue.fields.status.name,
            "Assignee": getattr(issue.fields.assignee, "displayName", "Unassigned"),
            "Created": issue.fields.created[:10],
            "Issue Type": issue.fields.issuetype.name,
            "Priority": issue.fields.priority.name if hasattr(issue.fields, 'priority') else "No Priority",
            "Task Category": task_category,
            "Aging (Days)": aging_days
        })
    
    df = pd.DataFrame(data)
    
    # Display raw data information
    st.sidebar.markdown("### Data Processing Information")
    st.sidebar.markdown(f"**Total Records Processed:** {len(df)}")
    st.sidebar.markdown(f"**Unique Components:** {len(df['Component'].unique())}")
    st.sidebar.markdown(f"**Unique Statuses:** {len(df['Status'].unique())}")
    st.sidebar.markdown(f"**Unique Assignees:** {len(df['Assignee'].unique())}")

    # Handle Dev Utilization view
    if dev_util or st.session_state.current_page == 'dev_util':
        st.session_state.current_page = 'dev_util'
        
        # Create header with page title
        create_header("Developer Resource Utilization")
        
        # Back to Home button
        if st.button("← Back to Home", key="back_home", help="Return to main dashboard"):
            st.session_state.current_page = 'home'
            st.session_state.selected_developer = None
            st.rerun()
        
        # Get unique assignees and sort them
        assignees = sorted(df['Assignee'].unique())
        
        # Add assignee dropdown with a default value
        if not assignees:
            st.warning("No developers found in the data.")
        else:
            # Use a callback to handle selection changes
            def on_developer_change():
                st.session_state.current_page = 'dev_util'
            
            selected_assignee = st.selectbox(
                "Select Developer",
                options=assignees,
                index=0 if st.session_state.selected_developer is None else assignees.index(st.session_state.selected_developer),
                key="developer_select",
                on_change=on_developer_change
            )
            
            # Update session state
            st.session_state.selected_developer = selected_assignee
            
            # Filter data for selected assignee
            assignee_df = df[df['Assignee'] == selected_assignee]
            
            if assignee_df.empty:
                st.warning(f"No data found for {selected_assignee}")
            else:
                # Calculate metrics
                total_tickets = len(assignee_df)
                status_counts = assignee_df['Status'].value_counts()
                
                # Display metrics in columns with improved styling
                st.markdown("### Key Metrics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Tickets", total_tickets)
                with col2:
                    st.metric("In Progress", len(assignee_df[assignee_df['Status'] == 'In Progress']))
                with col3:
                    st.metric("Done", len(assignee_df[assignee_df['Status'] == 'Done']))
                with col4:
                    st.metric("To Do", len(assignee_df[assignee_df['Status'] == 'To Do']))
                
                # Display detailed ticket information
                st.markdown("### Detailed Ticket Information")
                st.dataframe(
                    assignee_df,
                    column_config={
                        "Key": st.column_config.TextColumn("JIRA Key", width="medium"),
                        "Summary": st.column_config.TextColumn("Summary", width="large"),
                        "Component": st.column_config.TextColumn("Component", width="medium"),
                        "Status": st.column_config.TextColumn("Status", width="medium"),
                        "Priority": st.column_config.TextColumn("Priority", width="medium"),
                        "Created": st.column_config.TextColumn("Created Date", width="medium"),
                        "Issue Type": st.column_config.TextColumn("Issue Type", width="medium"),
                        "Task Category": st.column_config.TextColumn("Task Category", width="medium"),
                        "Aging (Days)": st.column_config.NumberColumn("Aging (Days)", width="medium", format="%d")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # Status Distribution
                st.markdown("### Status Distribution")
                fig = px.bar(
                    x=status_counts.index,
                    y=status_counts.values,
                    title=f"Status Distribution for {selected_assignee}",
                    labels={'x': 'Status', 'y': 'Number of Tickets'},
                    color=status_counts.values,
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Download button
                csv = assignee_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download Developer Data",
                    csv,
                    f"{selected_assignee}_jira_data.csv",
                    "text/csv",
                    key='download-csv'
                )

    else:
        # Original dashboard view
        st.session_state.current_page = 'home'
        st.session_state.selected_developer = None
        
        # Create header with page title
        create_header("PG Board Dashboard")
        
        # Component and Date Range Filters at the top
        st.markdown("### Filters")
        filter_col1, filter_col2 = st.columns(2)
        
        # Calculate default date range (last 1 month)
        default_end_date = datetime.now()
        default_start_date = default_end_date - timedelta(days=30)
        
        with filter_col1:
            all_components = ["All"] + sorted(df['Component'].unique().tolist())
            selected_component = st.selectbox("Select Component", all_components)
        
        with filter_col2:
            date_col1, date_col2 = st.columns(2)
            with date_col1:
                start_date = st.date_input(
                    "Start Date",
                    value=default_start_date,
                    min_value=pd.to_datetime(df['Created'].min()),
                    max_value=default_end_date
                )
            with date_col2:
                end_date = st.date_input(
                    "End Date",
                    value=default_end_date,
                    min_value=start_date,
                    max_value=datetime.now()
                )

        # Build dynamic JQL query
        jql_parts = ['project = PGP', 'status not in (Queue)']
        
        # Add component filter if selected
        if selected_component != "All":
            jql_parts.append(f'component = "{selected_component}"')
        
        # Add date range filter
        jql_parts.append(f'created >= "{start_date}"')
        jql_parts.append(f'created <= "{end_date}"')
        
        # Combine JQL parts
        dynamic_jql = ' AND '.join(jql_parts)
        
        # Display current JQL for verification
        st.sidebar.markdown("### Current JQL Query")
        st.sidebar.code(dynamic_jql, language="sql")
        
        # Fetch data using dynamic JQL
        try:
            issues = jira.search_issues(dynamic_jql, maxResults=1000)
            
            # Process fetched data
            data = []
            for issue in issues:
                components = [c.name for c in issue.fields.components] if issue.fields.components else ['No Component']
                data.append({
                    "Key": issue.key,
                    "Summary": issue.fields.summary,
                    "Component": components[0],
                    "Status": issue.fields.status.name,
                    "Assignee": getattr(issue.fields.assignee, "displayName", "Unassigned"),
                    "Created": issue.fields.created[:10],
                    "Issue Type": issue.fields.issuetype.name,
                    "Priority": issue.fields.priority.name if hasattr(issue.fields, 'priority') else "No Priority"
                })
            
            filtered_df = pd.DataFrame(data)
            
            if filtered_df.empty:
                st.warning("No issues found matching the selected criteria.")
                st.stop()
            
            # Add JQL query summary
            days_range = (end_date - start_date).days
            no_component_count = filtered_df[filtered_df['Component'] == 'No Component']['Component'].count()
            
            st.markdown(f"""
            **Query Summary:**
            - Total Issues: {len(filtered_df)}
            - Date Range: Last {days_range} days ({start_date} to {end_date})
            - Component: {selected_component}
            - Statuses: {', '.join(filtered_df['Status'].unique())}
            - Note: {no_component_count} ticket(s) are not assigned to any component. These tickets are excluded from the above distribution for better visibility of assigned components.
            """)
            
            # Add email reminder button for tickets without components
            if no_component_count > 0:
                st.markdown("### Component Assignment Reminder")
                st.markdown("Would you like to send reminder emails to ticket owners for adding components?")
                if st.button("Send Component Reminder Emails"):
                    with st.spinner("Sending reminder emails..."):
                        if send_component_reminder_emails(filtered_df):
                            st.success("Reminder emails sent successfully!")
                        else:
                            st.error("Failed to send reminder emails. Please check the email configuration.")
            
            # Add Component Distribution Pie Chart
            st.markdown("### Component Distribution")
            
            # Calculate aging for each ticket first
            filtered_df['Aging (Days)'] = filtered_df['Created'].apply(
                lambda x: (datetime.now() - pd.to_datetime(x)).days
            )
            
            # Calculate component-wise totals
            component_totals = filtered_df.groupby('Component').size().reset_index(name='Total')
            
            # Separate No Component entries
            no_component_count = component_totals[component_totals['Component'] == 'No Component']['Total'].sum() if 'No Component' in component_totals['Component'].values else 0
            component_totals = component_totals[component_totals['Component'] != 'No Component']
            
            # Sort by total
            component_totals = component_totals.sort_values('Total', ascending=False)
            
            # Create hover text with status breakdown
            hover_text = []
            for component in component_totals['Component']:
                component_data = filtered_df[filtered_df['Component'] == component]
                status_breakdown = component_data['Status'].value_counts()
                breakdown_text = '<br>'.join([f"{status}: {count}" for status, count in status_breakdown.items()])
                hover_text.append(f"<b>{component}</b><br>Total: {len(component_data)}<br><br>Status Breakdown:<br>{breakdown_text}")
            
            # Create pie chart
            fig = go.Figure(data=[go.Pie(
                labels=component_totals['Component'],
                values=component_totals['Total'],
                hoverinfo='text',
                text=hover_text,
                textinfo='label+value',
                textposition='outside',
                hole=.3,
                marker=dict(
                    colors=px.colors.qualitative.Set3,
                    line=dict(color='#ffffff', width=2)
                )
            )])
            
            # Update layout
            fig.update_layout(
                title='Component-wise Ticket Distribution',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                ),
                height=600,
                margin=dict(t=100, b=100)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add collapsible component-wise table
            with st.expander("View Component-wise Details", expanded=False):
                # Create detailed component table
                component_details = []
                for component in component_totals['Component']:
                    component_data = filtered_df[filtered_df['Component'] == component]
                    status_counts = component_data['Status'].value_counts()
                    component_details.append({
                        'Component': component,
                        'Total Tickets': len(component_data),
                        'Status Breakdown': '<br>'.join([f"{status}: {count}" for status, count in status_counts.items()]),
                        'Avg Age (Days)': round(component_data['Aging (Days)'].mean(), 1),
                        'Latest Ticket': component_data['Created'].max(),
                        'Oldest Ticket': component_data['Created'].min()
                    })
                
                # Convert to DataFrame and sort by total tickets
                component_df = pd.DataFrame(component_details)
                component_df = component_df.sort_values('Total Tickets', ascending=False)
                
                # Display the table
                st.dataframe(
                    component_df,
                    column_config={
                        "Component": st.column_config.TextColumn(
                            "Component",
                            width="medium"
                        ),
                        "Total Tickets": st.column_config.NumberColumn(
                            "Total Tickets",
                            width="small",
                            format="%d"
                        ),
                        "Status Breakdown": st.column_config.TextColumn(
                            "Status Breakdown",
                            width="large",
                            help="Breakdown of tickets by status"
                        ),
                        "Avg Age (Days)": st.column_config.NumberColumn(
                            "Avg Age (Days)",
                            width="small",
                            format="%.1f"
                        ),
                        "Latest Ticket": st.column_config.TextColumn(
                            "Latest Ticket",
                            width="small"
                        ),
                        "Oldest Ticket": st.column_config.TextColumn(
                            "Oldest Ticket",
                            width="small"
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )

            # Work Volume Matrix
            st.markdown("### Work Volume Matrix")
            st.markdown("Component-wise work distribution")
            
            # Create matrix data
            matrix_data = pd.pivot_table(
                filtered_df,
                values='Key',
                index=['Component'],
                columns=['Status'],
                aggfunc='count',
                fill_value=0
            )
            
            # Calculate total
            matrix_data['Total'] = matrix_data.sum(axis=1)
            
            # Sort by total
            matrix_data = matrix_data.sort_values('Total', ascending=False)
            
            # Display matrix with custom styling
            def highlight_total(val):
                if isinstance(val, (int, float)):
                    if val >= 10:
                        return 'background-color: #002e6e; color: white'
                    elif val >= 5:
                        return 'background-color: #00b9f1; color: white'
                    elif val >= 2:
                        return 'background-color: #e5e7eb; color: black'
                    else:
                        return 'background-color: #f3f4f6; color: black'
                return ''

            # Format the dataframe for display
            display_matrix = matrix_data.copy()
            
            # Apply styling
            styled_matrix = display_matrix.style.map(
                highlight_total,
                subset=['Total']
            ).format({
                'Total': '{:.0f}'
            })
            
            # Display matrix with adjusted column widths
            st.dataframe(
                styled_matrix,
                use_container_width=True,
                height=400
            )

            # Show additional metrics only when "All" components are selected
            if selected_component == "All":
                # Status Distribution by Component
                st.markdown("### Status Distribution by Component")
                status_dist = px.bar(
                    filtered_df,
                    x='Component',
                    color='Status',
                    title='Work Items Distribution by Status',
                    height=400,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                status_dist.update_layout(
                    xaxis=dict(
                        title='Component',
                        tickangle=45,
                        tickfont=dict(size=12, color='#002e6e')
                    ),
                    yaxis=dict(
                        title='Number of Work Items',
                        tickfont=dict(size=12, color='#002e6e')
                    ),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(t=100, b=100)
                )
                st.plotly_chart(status_dist, use_container_width=True)

                # Create clickable JIRA links using Streamlit's link format
                filtered_df['JIRA Link'] = filtered_df.apply(
                    lambda row: f"[{row['Key']}]({JIRA_URL}/browse/{row['Key']})",
                    axis=1
                )
                
                # Sort by created date in descending order
                filtered_df = filtered_df.sort_values('Created', ascending=False)
                
                # Detailed View with proper heading
                st.markdown("### Detailed Issue List")
                st.markdown("Sorted by creation date (newest first)")
                
                # Reorder columns for better visibility
                display_columns = [
                    'JIRA Link', 'Issue Type', 'Assignee', 
                    'Status', 'Component', 'Created', 'Aging (Days)', 'Summary'
                ]
                
                # Configure column widths and formatting
                st.dataframe(
                    filtered_df[display_columns],
                    column_config={
                        "JIRA Link": st.column_config.LinkColumn(
                            "JIRA ID",
                            width="small",
                            help="Click to open in JIRA"
                        ),
                        "Issue Type": st.column_config.TextColumn(
                            "Issue Type",
                            width="small"
                        ),
                        "Assignee": st.column_config.TextColumn(
                            "Assignee",
                            width="small"
                        ),
                        "Status": st.column_config.TextColumn(
                            "Status",
                            width="small"
                        ),
                        "Component": st.column_config.TextColumn(
                            "Component",
                            width="small"
                        ),
                        "Created": st.column_config.TextColumn(
                            "Created Date",
                            width="small"
                        ),
                        "Aging (Days)": st.column_config.NumberColumn(
                            "Aging (Days)",
                            width="small",
                            format="%d",
                            help="Days since ticket creation"
                        ),
                        "Summary": st.column_config.TextColumn(
                            "Summary",
                            width="large",
                            max_chars=100
                        )
                    },
                    hide_index=True,
                    use_container_width=True,
                    height=400
                )

        except Exception as e:
            st.error(f"Error fetching JIRA data: {e}")
            st.stop()

except Exception as e:
    st.error(f"Error fetching JIRA data: {e}")
    st.stop()

def send_component_reminder_emails(df):
    """Send reminder emails to assignees/reporters of tickets without components."""
    if SMTP_USERNAME is None or SMTP_PASSWORD is None or SENDER_EMAIL is None:
        st.error("Email configuration is missing. Please set SMTP_USERNAME, SMTP_PASSWORD, and SENDER_EMAIL in .env file.")
        return False
    
    no_component_tickets = df[df['Component'] == 'No Component']
    if no_component_tickets.empty:
        st.info("No tickets found without components.")
        return True
    
    try:
        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        success_count = 0
        for _, ticket in no_component_tickets.iterrows():
            # Prepare email content
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['Subject'] = f"Action Required: Add Component to JIRA Ticket {ticket['Key']}"
            
            # Get assignee email (you might need to modify this based on your JIRA setup)
            assignee_email = ticket.get('Assignee Email', '')
            if not assignee_email:
                continue
            
            msg['To'] = assignee_email
            
            # Create email body
            body = f"""
            Hello,

            This is a reminder that the following JIRA ticket needs a component assigned:

            Ticket: {ticket['Key']}
            Summary: {ticket['Summary']}
            Status: {ticket['Status']}
            Created: {ticket['Created']}

            Please add an appropriate component to this ticket at your earliest convenience.

            You can access the ticket here: {JIRA_URL}/browse/{ticket['Key']}

            Best regards,
            PM Assist Bot
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server.send_message(msg)
            success_count += 1
        
        server.quit()
        st.success(f"Successfully sent reminder emails for {success_count} tickets.")
        return True
        
    except Exception as e:
        st.error(f"Error sending emails: {str(e)}")
        return False
