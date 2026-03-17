
import pandas as pd
import numpy as np

customers = "company_revenue.csv"
customers = pd.read_csv(customers)

def convert_suffix(x):
    if pd.isna(x):
        return np.nan
    x = str(x).lower()
    if "k" in x:
        return float(x.replace("k", "")) * 1_000
    elif "m" in x:
        return float(x.replace("m", "")) * 1_000_000
    else:
        return float(x)
        
missing_markers = ["", " ", "—", "--", "N/A", "nan"]

customers["Revenue"] = customers ["Revenue"].replace(missing_markers, np.nan)
customers["Revenue"] = customers["Revenue"].str.replace("£", "", regex=False)
customers["Revenue"] = customers["Revenue"].str.replace(",", "", regex=False)
customers["Year"] = pd.to_numeric(customers["Year"].astype(str).str.replace("FY", ""), errors="coerce")
customers["Year"] = customers["Year"].astype(int)
customers["Revenue"] = customers["Revenue"].apply(convert_suffix)

customers = customers.sort_values("Revenue", ascending=False)

top_companies = customers[customers["Revenue"] >= 7500]

top_companies.to_csv("top_Companies.csv", index=False)

print(top_companies)
