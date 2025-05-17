import pandas as pd
import matplotlib.pyplot as plt

# Read the log file
with open("prepared_access_logs", "r") as file:
    lines = file.readlines()

# Graph: Pie chart of 200s, 400s, 500s
def statusRequests():
    # Extract status codes from lines
    status_codes = [int(line.split(' - ')[3]) for line in lines]

    # Group status codes into categories (200s, 300s, 400s, 500s)
    categories = [f"{status // 100}00s" for status in status_codes]

    # Count occurrences of each category
    category_counts = pd.Series(categories).value_counts().sort_index()

    # Plot the pie chart
    category_counts.plot.pie(
        labels=None,
        autopct='%1.1f%%', 
        startangle=90, 
        title='HTTP Status Code Distribution', 
        figsize=(6, 6),
        colors = ['paleturquoise', 'azure', 'pink', 'hotpink']
    )
    plt.legend(category_counts.index, title='Status Code Categories', loc='upper left', bbox_to_anchor=(1, 1))

    plt.ylabel('')  # Remove the y-axis label
    plt.tight_layout()
    plt.show()

statusRequests()
