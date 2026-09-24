import pyodbc
import pandas as pd

# SQL Server connection
conn = pyodbc.connect(
    'driver={SQL Server};'
    'server=Desktop-22KARJS\\SQLEXPRESS;'
    'database=EcommerceAnalytics;'
    'Trusted_Connection=yes;'
)

query ="""
WITH rfm_base AS (
    SELECT
        CustomerID,
        DATEDIFF(DAY, MAX(InvoiceDate), '2011-12-10') AS Recency,
        COUNT(DISTINCT InvoiceNo) AS Frequency,
        SUM(Quantity * UnitPrice) AS Monetary
    FROM online_retail
    WHERE CustomerID IS NOT NULL
      AND Quantity > 0
      AND InvoiceDate IS NOT NULL
    GROUP BY CustomerID
)
SELECT
    CustomerID,
    Recency,
    Frequency,
    Monetary,
    CASE
        WHEN Monetary >= 5000 AND Frequency >= 10 THEN 'High Value'
        WHEN Monetary >= 1000 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS CustomerSegment,
    CASE
        WHEN Recency > 180 THEN 'High Churn Risk'
        WHEN Recency > 90 THEN 'Medium Churn Risk'
        ELSE 'Active'
    END AS ChurnStatus
FROM rfm_base
ORDER BY Monetary DESC;"""


df_rfm = pd.read_sql(query, conn)

print(df_rfm.head(10))
print(f"\nTotal customers: {len(df_rfm)}")

print("\n--- Customer Segment Counts ---")
print(df_rfm['CustomerSegment'].value_counts())

print("\n--- Churn Status Counts ---")
print(df_rfm['ChurnStatus'].value_counts())

conn.close()

import matplotlib.pyplot as plt

# Customer Segment Distribution
plt.figure(figsize=(8,5))
df_rfm['CustomerSegment'].value_counts().plot(kind='bar', color=['#4CAF50', '#2196F3', '#FF9800'])
plt.title('Customer Segment Distribution')
plt.xlabel('Segment')
plt.ylabel('Number of Customers')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('segment_chart.png')

#Churn Status Distribution
plt.figure(figsize=(8,5))
df_rfm['ChurnStatus'].value_counts().plot(kind='bar', color=['#4CAF50', '#F44336', '#FFC107'])
plt.title('Customer Churn Status Distribution')
plt.xlabel('Churn Status')
plt.ylabel('Number of Customers')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('churn_chart.png')
plt.show()


# CLV
df_rfm['AvgOrderValue'] = df_rfm['Monetary'] / df_rfm['Frequency']

#Total Monetary value
df_rfm['CLV'] = df_rfm['Monetary']

# Top 10 High CLV customers
print("\n--- Top 10 Customers by CLV ---")
print(df_rfm[['CustomerID', 'Recency', 'Frequency', 'AvgOrderValue', 'CLV', 'CustomerSegment']].sort_values(by='CLV', ascending=False).head(10))

# Segment-wise Average CLV
print("\n--- Average CLV by Segment ---")
print(df_rfm.groupby('CustomerSegment')['CLV'].mean().sort_values(ascending=False))

# Segment-wise Total Revenue Contribution
print("\n--- Total Revenue by Segment ---")
print(df_rfm.groupby('CustomerSegment')['CLV'].sum().sort_values(ascending=False))

