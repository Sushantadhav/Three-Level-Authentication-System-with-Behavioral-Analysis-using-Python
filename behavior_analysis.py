import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Step 1 – SQLite DB connect karo
conn = sqlite3.connect("database.db")

# Step 2 – behavior_logs table load karo
df = pd.read_sql_query("SELECT * FROM behavior_logs", conn)

print("\n===== BEHAVIOR ANALYSIS REPORT =====")
print("Total Actions Recorded:", len(df))

# Step 3 – Action-wise count (column ka naam check)
action_col = None
if 'action_type' in df.columns:
    action_col = 'action_type'
elif 'action' in df.columns:
    action_col = 'action'

if action_col:
    print("\nAction Type Counts:")
    print(df[action_col].value_counts())
else:
    print("\n❌ No action_type/action column found in behavior_logs table.")

# Step 4 – Agar time_taken column hai to average time
if 'time_taken' in df.columns:
    print("\nAverage Time per Action (seconds):")
    print(df.groupby(action_col)['time_taken'].mean())

# Step 5 – Suspicious pattern: 3+ failed logins
if action_col:
    failed_users = df[df[action_col] == 'login_fail']
    if 'username' in df.columns:
        fail_count = failed_users['username'].value_counts()
        sus = fail_count[fail_count > 3]
        if not sus.empty:
            print("\n⚠ Suspicious Users (Multiple Failed Logins):")
            print(sus)

# Step 6 – Visualization
if action_col:
    df[action_col].value_counts().plot(kind='bar', color='skyblue')
    plt.title("Behavior Actions Distribution")
    plt.xlabel("Action Type")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()

# Close DB connection
conn.close()
