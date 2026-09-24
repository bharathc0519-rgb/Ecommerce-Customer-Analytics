create Database EcommerceAnalytics
USE ECommerceAnalytics;

CREATE TABLE online_retail (
    InvoiceNo VARCHAR(20),
    StockCode VARCHAR(20),
    Description VARCHAR(255),
    Quantity INT,
    InvoiceDate DATETIME,
    UnitPrice DECIMAL(10,2),
    CustomerID INT NULL,
    Country VARCHAR(100)
);

USE EcommerceAnalytics;
select count(*) AS TotalRows from online_retail;
select top 10 * from online_retail;

select count(*) as MissingCustomerID 
from online_retail 
where CustomerID IS NULL;

select 
    customerID,
    datediff(day, Max(invoicedate),'2011-12-10') as Recency,
    count(distinct InvoiceNo) as Frequency,
    sum(quantity * UnitPrice) as monetary
from online_retail
where customerID is not null
    and Quantity > 0
    Group By CustomerID
    Order By Monetary DESC
SELECT CustomerID, InvoiceDate 
FROM online_retail 
WHERE CustomerID = 12346;

with rfm_base as (
    select 
        CustomerID,
        DATEDIFF(DAY, MAX(InvoiceDate), '2011-12-10') as Recency,
        COUNT(distinct InvoiceNo) as Frequency,
        SUM(Quantity * UnitPrice) as Monetary
    from online_retail
    where CustomerID IS NOT NULL
      AND Quantity > 0
      AND InvoiceDate IS NOT NULL
    group by CustomerID
)
SELECT 
    CustomerID,
    Recency,
    Frequency,
    Monetary,
    case 
        when Monetary >= 5000 AND Frequency >= 10 THEN 'High Value'
        when Monetary >= 1000 THEN 'Medium Value'
        else 'Low Value'
    end as CustomerSegment,
    case
        when Recency > 180 THEN 'High Churn Risk'
        when Recency > 90 THEN 'Medium Churn Risk'
        else 'Active'
    end as ChurnStatus
from rfm_base
order by Monetary DESC; 

-- Summary: Segment-wise Customer Count & Revenue
;WITH rfm_base2 AS (
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
),
rfm_segments2 AS (
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
    FROM rfm_base2
)
SELECT 
    CustomerSegment,
    ChurnStatus,
    COUNT(*) AS NumberOfCustomers,
    SUM(Monetary) AS TotalRevenue,
    AVG(Monetary) AS AvgRevenuePerCustomer
FROM rfm_segments2
GROUP BY CustomerSegment, ChurnStatus
ORDER BY TotalRevenue DESC;