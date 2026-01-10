import pandas as pd
import numpy as np

# --- 1. INDIA'S ELECTORAL MAP (Real Seat Counts) ---
# Format: "State": [Lok_Sabha_Seats, Assembly_Seats, Security_Tier]
# Tier 1 = Normal, Tier 2 = Sensitive (High Security), Tier 3 = Conflict (Max Security)
STATE_DATA = {
    "Andhra Pradesh": [25, 175, 1], "Arunachal Pradesh": [2, 60, 2],
    "Assam": [14, 126, 2], "Bihar": [40, 243, 2],
    "Chhattisgarh": [11, 90, 2], "Goa": [2, 40, 1],
    "Gujarat": [26, 182, 1], "Haryana": [10, 90, 1],
    "Himachal Pradesh": [4, 68, 1], "Jharkhand": [14, 81, 2],
    "Karnataka": [28, 224, 1], "Kerala": [20, 140, 2],
    "Madhya Pradesh": [29, 230, 1], "Maharashtra": [48, 288, 1],
    "Manipur": [2, 60, 3], "Meghalaya": [2, 60, 2],
    "Mizoram": [1, 40, 1], "Nagaland": [1, 60, 2],
    "Odisha": [21, 147, 2], "Punjab": [13, 117, 1],
    "Rajasthan": [25, 200, 1], "Sikkim": [1, 32, 1],
    "Tamil Nadu": [39, 234, 1], "Telangana": [17, 119, 1],
    "Tripura": [2, 60, 2], "Uttar Pradesh": [80, 403, 1],
    "Uttarakhand": [5, 70, 1], "West Bengal": [42, 294, 3],
    "Delhi (NCT)": [7, 70, 1], "Jammu & Kashmir": [5, 90, 3]
}

# --- 2. UNIT ECONOMICS (in INR) ---
COSTS = {
    # Capital (Assets) - ONOE requires 2x sets (one for MP, one for MLA)
    "EVM_Set": 45000,           # BU + CU + VVPAT
    "VVPAT_Slip_Storage": 5000, # Per vault
    
    # Operational (Running) - These are saved in ONOE
    "Polling_Staff_Wage": 18000,# Per person for election period
    "Security_Co_Cost": 2.5,    # Crores per Company (Travel + Logistics)
    "Transport_Vehicle": 6000,  # Per vehicle per day
    "Webcasting_Cam": 1500,     # Per booth
    
    # Consumables
    "Indelible_Ink": 180,       # Per vial
}

# Assumptions
BOOTHS_PER_ASSEMBLY_SEAT = 250  # Avg booths per MLA constituency
STAFF_PER_BOOTH = 6             # Presiding + Polling officers
VEHICLES_PER_BOOTH = 0.8        # Shared transport
SECURITY_CO_SIZE = 100          # Jawans per company

data_rows = []

def generate_financials():
    for state, specs in STATE_DATA.items():
        ls_seats, as_seats, tier = specs
        
        # Derived Metrics
        total_booths = as_seats * BOOTHS_PER_ASSEMBLY_SEAT
        total_staff = total_booths * STAFF_PER_BOOTH
        
        # Security Multiplier (Higher for sensitive states)
        sec_mult = 1.5 if tier == 2 else (2.5 if tier == 3 else 1.0)
        req_companies = (ls_seats * 15) * sec_mult # Base logic: 15 companies per LS seat area
        
        # --- SCENARIO 1: STANDARD CYCLE (SEPARATE ELECTIONS) ---
        # Cost = Cost of LS Election (Funded by Center) + Cost of Assembly (Funded by State)
        
        # A. EVM Procurement (Standard) - We reuse machines, so inventory is 1.2x of booths
        std_evm_cost = (total_booths * 1.2 * COSTS["EVM_Set"]) / 10**7
        
        # B. Staff Wages (Paid Twice: Once for LS, Once for Assembly)
        std_staff_cost = (total_staff * COSTS["Polling_Staff_Wage"] * 2) / 10**7
        
        # C. Security Deployment (Moved Twice)
        std_sec_cost = (req_companies * COSTS["Security_Co_Cost"] * 2) 
        
        # D. Logistics (Vehicles rented twice)
        std_log_cost = (total_booths * VEHICLES_PER_BOOTH * COSTS["Transport_Vehicle"] * 2) / 10**7
        
        # --- SCENARIO 2: ONOE CYCLE (SIMULTANEOUS) ---
        
        # A. EVM Procurement (ONOE) - Need 2 sets per booth simultaneously (Inventory 2.4x)
        onoe_evm_cost = (total_booths * 2.4 * COSTS["EVM_Set"]) / 10**7
        
        # B. Staff Wages (Paid Once + 20% Hike for extra work)
        onoe_staff_cost = (total_staff * (COSTS["Polling_Staff_Wage"] * 1.2)) / 10**7
        
        # C. Security Deployment (Moved Once)
        onoe_sec_cost = (req_companies * COSTS["Security_Co_Cost"] * 1)
        
        # D. Logistics (Vehicles rented once, maybe slightly larger trucks)
        onoe_log_cost = (total_booths * VEHICLES_PER_BOOTH * (COSTS["Transport_Vehicle"] * 1.1)) / 10**7

        # --- APPEND DETAILED ROWS ---
        
        # 1. CAPITAL (EVMs)
        data_rows.append({
            "State": state, "Category": "Capital Assets", "Line_Item": "EVM Procurement",
            "Details": "Ballot & Control Units", "Funding": "Center (LS) / State (VS)",
            "Standard_Cycle_Cost_Cr": round(std_evm_cost, 2),
            "ONOE_Cycle_Cost_Cr": round(onoe_evm_cost, 2),
            "Impact": "Cost Increase", "Variance_Cr": round(onoe_evm_cost - std_evm_cost, 2)
        })

        # 2. OPERATIONAL (Human Resources)
        data_rows.append({
            "State": state, "Category": "Human Resources", "Line_Item": "Polling Staff Wages",
            "Details": "Remuneration for Teachers/Govt Staff", "Funding": "Shared",
            "Standard_Cycle_Cost_Cr": round(std_staff_cost, 2),
            "ONOE_Cycle_Cost_Cr": round(onoe_staff_cost, 2),
            "Impact": "Savings", "Variance_Cr": round(onoe_staff_cost - std_staff_cost, 2)
        })

        # 3. SECURITY (CAPF)
        data_rows.append({
            "State": state, "Category": "Security", "Line_Item": "CAPF Logistics",
            "Details": "Train/Air Movement of Forces", "Funding": "Center",
            "Standard_Cycle_Cost_Cr": round(std_sec_cost, 2),
            "ONOE_Cycle_Cost_Cr": round(onoe_sec_cost, 2),
            "Impact": "Savings", "Variance_Cr": round(onoe_sec_cost - std_sec_cost, 2)
        })
        
        # 4. LOGISTICS (Transport)
        data_rows.append({
            "State": state, "Category": "Logistics", "Line_Item": "Last Mile Transport",
            "Details": "Trucks/Buses for Booth Setup", "Funding": "State",
            "Standard_Cycle_Cost_Cr": round(std_log_cost, 2),
            "ONOE_Cycle_Cost_Cr": round(onoe_log_cost, 2),
            "Impact": "Savings", "Variance_Cr": round(onoe_log_cost - std_log_cost, 2)
        })

generate_financials()
df = pd.DataFrame(data_rows)

# --- ADDING THE 'LOK SABHA' vs 'ASSEMBLY' SPLIT FOR VISUALIZATION ---
# We calculate total savings/cost per state
df_summary = df.groupby('State')[['Standard_Cycle_Cost_Cr', 'ONOE_Cycle_Cost_Cr']].sum().reset_index()
df_summary['Net_Savings'] = df_summary['Standard_Cycle_Cost_Cr'] - df_summary['ONOE_Cycle_Cost_Cr']

print("Data Generation Complete. Preview:")
print(df.head(10))

# Save to CSV
df.to_csv("onoe_complete_india_data.csv", index=False)