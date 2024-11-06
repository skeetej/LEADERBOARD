import pandas as pd
import streamlit as st
import io
import subprocess

# Define the file path for the leaderboard dataframe
LEADERBOARD_FILE = "leaderboard.csv"

# Load the leaderboard dataframe from file (if it exists)
try:
    leaderboard_df = pd.read_csv(LEADERBOARD_FILE)
except FileNotFoundError:
    leaderboard_df = pd.DataFrame(columns=["TEAM NAME", "BALANCE"])

# Dictionary mapping team names to their CSV files
team_csv_files = {
    'TECH': None,
    'INDUSTRIALS': None,
    'CONSUMER STAPLES': None,
    'CONSUMER DISCRETIONARY': None,
    'FINANCIALS': None,
    'ENERGY': None,
    'HEALTHCARE': None
}

# Store the team_csv_files dictionary in session state
if 'team_csv_files' not in st.session_state:
    st.session_state.team_csv_files = team_csv_files

# Function to update the dictionary
def update_team_csv_files(team_name, csv_file):
    if team_name in st.session_state.team_csv_files:
        st.session_state.team_csv_files[team_name] = csv_file
    else:
        st.error("Team not found.")

# Streamlit app
st.set_page_config()

col1, col2 = st.columns([1, 4])

with col1:
    st.image("SMIP.png", width=150)

with col2:
    st.title("SMIP TRADING LEADERBOARD")

# Create a placeholder for the dataframe
df_placeholder = st.empty()

# Display the leaderboard
def display_leaderboard():
    global leaderboard_df
    current_balance = []

    for team, csv_file in st.session_state.team_csv_files.items():
        if csv_file is None:
            current_balance.append(0)
        elif isinstance(csv_file, str):
            current_balance.append(0)
        else:
            df = pd.read_csv(io.StringIO(csv_file.getvalue().decode('utf-8')))
            balance_before = df.iloc[0, 1]
            balance_after = df.iloc[0, 2]

            if balance_after is None or balance_after == 'N/A':
                current_balance.append(balance_before)
            elif balance_before == balance_after:
                current_balance.append(balance_before)
            else:
                current_balance.append(balance_after)

    leaderboard_df = pd.DataFrame(
        {'TEAM NAME': list(st.session_state.team_csv_files.keys()), 'BALANCE': current_balance})

    # Sort by BALANCE in descending order
    leaderboard_df = leaderboard_df.sort_values(by='BALANCE', ascending=False)

    # Update RANK column
    leaderboard_df['RANK'] = leaderboard_df['BALANCE'].rank(method='dense', ascending=False).astype(int)

    # Format BALANCE column as dollar value with 2 decimal places
    leaderboard_df['BALANCE'] = leaderboard_df['BALANCE'].apply(lambda x: "${:,.2f}".format(x))

    # Reorder columns
    leaderboard_df = leaderboard_df[['RANK', 'TEAM NAME', 'BALANCE']]

    return leaderboard_df

# Display the initial leaderboard
leaderboard_df = display_leaderboard()
df_placeholder.dataframe(leaderboard_df, hide_index=True, width=1200)

##################################################################################################################

# Input field to update a team
with st.form("update_team"):
    team_name = st.selectbox("Select Team", list(st.session_state.team_csv_files.keys()))
    csv_file = st.file_uploader("CSV File", type=["csv"])
    submitted = st.form_submit_button("Update Team")

    if submitted:
        if csv_file:
            if "account-history" in csv_file.name:
                update_team_csv_files(team_name, csv_file)
                leaderboard_df = display_leaderboard()
                df_placeholder.dataframe(leaderboard_df, hide_index=True, width=1200)  # Update the dataframe
                st.success("Team updated successfully!")

                # Save the updated dataframe to a CSV file
                leaderboard_df.to_csv(LEADERBOARD_FILE, index=False)

                # Commit the changes to Git
                subprocess.run(["git", "add", LEADERBOARD_FILE])
                subprocess.run(["git", "commit", "-m", "Update leaderboard"])

                # Push the changes to Streamlit Cloud
                subprocess.run(["streamlit", "cloud", "push"])
            else:
                st.error("Please upload Account History CSV file.")
        else:
            st.error("Please select a CSV file.")

#################################################################################################################

import time
from datetime import datetime

# Set the target date
target_date = datetime(2024, 12, 4)  # Replace with your desired date

# Calculate the time difference between now and the target date
now = datetime.now()
time_diff = target_date - now

# Convert the time difference to seconds
total_seconds = time_diff.total_seconds()

# Create a progress bar
ph = st.empty()

# Countdown loop
for secs in range(int(total_seconds), 0, -1):
    # Calculate the remaining time
    days, remainder = divmod(secs, 86400)  # 86400 seconds in a day
    hours, remainder = divmod(remainder, 3600)  # 3600 seconds in an hour
    minutes, seconds = divmod(remainder, 60)

    # Format the remaining time
    time_str = f"{days:02d} DAYS, {hours:02d}H:{minutes:02d}M:{seconds:02d}S"

    # Update the progress bar
    ph.metric("TRADING TIME LEFT", time_str)

    # Wait for 1 second
    time.sleep(1)

ph.metric("TRADING TIME LEFT", "NO MORE TIME!")