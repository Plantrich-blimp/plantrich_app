import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Plantrich App", layout="wide")

menu = st.sidebar.radio("Navigation", ["🗞 Onboarding Process", "📊 Product Vault"])
sub_menu = None
if menu == "📊 Product Vault":
    sub_menu = st.sidebar.radio("Select Product Type", ["Mutual Funds", "AIF", "PMS", "Direct Equity"])

@st.cache_data
def load_mutual_funds():
    df = pd.read_excel("product_vault.xlsx", sheet_name="Mutual Funds")
    df.columns = df.columns.str.strip()
    return df

@st.cache_data
def load_aif_data():
    try:
        df = pd.read_excel("product_vault.xlsx", sheet_name="AIF")
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

df_mf = load_mutual_funds()
df_aif = load_aif_data()
# --------------------- ONBOARDING PROCESS ---------------------
if menu == "🗞 Onboarding Process":
    st.title("🗞 Onboarding Process")
    onboarding_file = "Onboarding data.xlsx"

    try:
        onboarding_excel = pd.ExcelFile(onboarding_file)
        sheet_names = onboarding_excel.sheet_names
        selected_sheet = st.selectbox("Select Section", sheet_names)
        df_selected = pd.read_excel(onboarding_file, sheet_name=selected_sheet)
        st.dataframe(df_selected, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading onboarding file: {e}")

elif menu == "📊 Product Vault" and sub_menu == "Mutual Funds":
    st.title("📊 Product Vault – Mutual Fund Portfolio Engine")
    st.subheader("Step 1: Select Your Risk Profile")
    risk_profile = st.selectbox("", ["Aggressive", "Moderate", "Conservative"])

    asset_allocations = {
        "Aggressive": {"Equity": 75, "Debt": 20, "Commodity": 5},
        "Moderate": {"Equity": 65, "Debt": 30, "Commodity": 5},
        "Conservative": {"Equity": 45, "Debt": 45, "Commodity": 10}
    }
    st.subheader("Step 2: Asset Class Allocation")
    st.table(pd.DataFrame(asset_allocations[risk_profile].items(), columns=["Asset Class", "% Allocation"]))

    mf_allocation = {
        "Aggressive": {"LargeCap": 23, "Midcap": 19, "SmallCap": 11, "Flexicap": 15, "Sector": 8, "Debt": 20, "Commodity": 5},
        "Moderate": {"LargeCap": 23, "Midcap": 13, "SmallCap": 7, "Flexicap": 23, "Sector": 0, "Debt": 30, "Commodity": 5},
        "Conservative": {"LargeCap": 20, "Midcap": 5, "SmallCap": 2, "Flexicap": 18, "Sector": 0, "Debt": 45, "Commodity": 10}
    }
    st.subheader("Step 3: Mutual Fund Category Allocation")
    st.table(pd.DataFrame(mf_allocation[risk_profile].items(), columns=["Category", "% Allocation"]))

    st.subheader("Step 4: Enter Your Investment Amount")
    amount = st.number_input("Total Investment Amount (INR)", min_value=1000, step=1000)
    if amount:
        st.subheader("Step 5: Portfolio Allocation & Fund Recommendations")
        alloc_df = pd.DataFrame(mf_allocation[risk_profile].items(), columns=["Category", "Allocation %"])
        alloc_df["Amount"] = alloc_df["Allocation %"] * amount / 100
        st.markdown("##### Allocation Summary")
        st.dataframe(alloc_df, use_container_width=True)

        st.markdown("##### 🔍 Filter Options")
        selected_categories = st.multiselect("Select categories to view:", options=alloc_df["Category"].tolist(), default=alloc_df["Category"].tolist())
        min_cagr, max_cagr = st.slider("Filter by CAGR (%)", 0.0, 25.0, (0.0, 25.0), 0.5)
        min_rating = st.slider("Minimum Plantrich Rating", 0.0, 5.0, 0.0, 0.1)

        selected_funds = []
        st.markdown("### 📋 Select Your Preferred Funds")

        for _, row in alloc_df.iterrows():
            category = row["Category"]
            cat_amount = row["Amount"]
            if category not in selected_categories:
                continue

            st.markdown(f"#### {category} – ₹{int(cat_amount):,}")
            filtered = df_mf[
                (df_mf["Category"] == category) &
                (df_mf["CAGR"] >= min_cagr) &
                (df_mf["CAGR"] <= max_cagr) &
                (df_mf["Plantrich Rating"] >= min_rating)
            ]

            if filtered.empty:
                st.warning("No matching funds found.")
                continue

            for i, fund in filtered.iterrows():
                label = f"{fund['Fund Name']} (CAGR: {fund['CAGR']}%, Rating: {fund['Plantrich Rating']})"
                if st.checkbox(label, key=f"{category}_{i}"):
                    selected_funds.append({
                        "Category": category,
                        "Fund Name": fund["Fund Name"],
                        "CAGR": fund["CAGR"],
                        "Plantrich Rating": fund["Plantrich Rating"],
                        "Exit Load": fund["Exit Load"],
                        "Amount Allocated": int(cat_amount)
                    })
        if selected_funds:
            st.subheader("📊 Final Portfolio Summary")
            portfolio_df = pd.DataFrame(selected_funds)
            st.dataframe(portfolio_df, use_container_width=True)

            csv = portfolio_df.to_csv(index=False).encode('utf-8')
            st.download_button("📅 Download Portfolio as CSV", data=csv, file_name='recommended_portfolio.csv', mime='text/csv')

            st.markdown("### 📈 Portfolio Visuals & Growth Projection")
            fig1, ax1 = plt.subplots()
            ax1.pie(portfolio_df["Amount Allocated"], labels=portfolio_df["Fund Name"], autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            st.pyplot(fig1)

            years = [0, 1, 2, 3, 4, 5]
            growth_data = {
                fund["Fund Name"]: [fund["Amount Allocated"] * ((1 + fund["CAGR"]/100) ** y) for y in years]
                for fund in selected_funds
            }
            growth_df = pd.DataFrame(growth_data, index=years)
            st.line_chart(growth_df)

            st.caption("📈 Projections assume CAGR remains constant over 5 years. No withdrawals or rebalancing.")
        else:
            st.info("Select at least one fund to generate your portfolio.")

elif menu == "📊 Product Vault" and sub_menu == "AIF":
    st.title("💼 Alternative Investment Funds (AIF)")

    if df_aif.empty:
        st.warning("AIF data not found in the Excel file (sheet name: 'AIF').")
    else:
        df_aif.columns = df_aif.columns.str.strip()

        categories = df_aif["Category"].dropna().unique().tolist()
        selected_category = st.selectbox("Select AIF Category", ["All"] + categories)

        filtered_aifs = df_aif.copy()
        if selected_category != "All":
            filtered_aifs = filtered_aifs[filtered_aifs["Category"] == selected_category]

        if "Horizon" in filtered_aifs.columns:
            horizons = filtered_aifs["Horizon"].dropna().unique().tolist()
            selected_horizon = st.multiselect("Select Investment Horizon", options=horizons, default=horizons)
            filtered_aifs = filtered_aifs[filtered_aifs["Horizon"].isin(selected_horizon)]

        min_cagr = st.slider("Minimum CAGR (%)", 0.0, 25.0, 0.0, 0.5)
        filtered_aifs = filtered_aifs[filtered_aifs["CAGR"] >= min_cagr]

        min_investment = st.number_input("Maximum Minimum Investment (INR)", min_value=0, value=10000000, step=100000)
        if "Minimum Investment" in filtered_aifs.columns:
            filtered_aifs = filtered_aifs[filtered_aifs["Minimum Investment"] <= min_investment]
        display_cols = ["Fund Name", "AMC", "Category", "CAGR", "Plantrich Rating", "Minimum Investment"]
        available_cols = [col for col in display_cols if col in filtered_aifs.columns]

        if not filtered_aifs.empty and available_cols:
            st.dataframe(filtered_aifs[available_cols], use_container_width=True)

            st.markdown("### 📋 Select AIFs for Projection & Details")
            selected_aifs = []
            for i, row in filtered_aifs.iterrows():
                label = f"{row['Fund Name']} (CAGR: {row['CAGR']}%, Rating: {row['Plantrich Rating']})"
                if st.checkbox(label, key=f"aif_{i}"):
                    selected_aifs.append(row)

            if selected_aifs:
                selected_df = pd.DataFrame(selected_aifs)

                invest_amount = st.number_input("Enter Investment Amount per AIF (INR)", min_value=10000, value=100000, step=10000)

                st.subheader("📈 AIF Growth Projection (5 Years)")
                years = [0, 1, 2, 3, 4, 5]
                growth_data = {}
                for _, fund in selected_df.iterrows():
                    fv = [invest_amount * ((1 + fund["CAGR"] / 100) ** y) for y in years]
                    growth_data[fund["Fund Name"]] = fv
                growth_df = pd.DataFrame(growth_data, index=years)
                st.line_chart(growth_df)
                st.caption("📈 Projections assume CAGR remains constant over 5 years. No withdrawals or rebalancing.")

                st.subheader("📊 Comparison Table of Selected AIFs")
                compare_cols = ["Fund Name", "AMC", "Category", "CAGR", "Plantrich Rating", "Minimum Investment"]
                st.dataframe(selected_df[[col for col in compare_cols if col in selected_df.columns]], use_container_width=True)
                if "Investment rationale" in selected_df.columns:
                    st.markdown("### 📌 Investment Rationales for Selected AIFs")
                    for _, row in selected_df.iterrows():
                        if pd.notna(row["Investment rationale"]):
                            with st.expander(row["Fund Name"]):
                                st.write(row["Investment rationale"])

elif menu == "📊 Product Vault" and sub_menu == "PMS":
    st.title("📊 PMS (Portfolio Management Services)")

    try:
        df_pms = pd.read_excel("product_vault.xlsx", sheet_name="PMS")
        df_pms.columns = df_pms.columns.str.strip()

        st.subheader("📋 PMS Filter")
        categories = df_pms["Category"].dropna().unique().tolist()
        selected_category = st.selectbox("Select PMS Category", ["All"] + categories)

        filtered_pms = df_pms.copy()
        if selected_category != "All":
            filtered_pms = filtered_pms[filtered_pms["Category"] == selected_category]

        horizons = filtered_pms["Horizon"].dropna().unique().tolist()
        selected_horizon = st.multiselect("Select Horizon", horizons, default=horizons)
        filtered_pms = filtered_pms[filtered_pms["Horizon"].isin(selected_horizon)]

        st.dataframe(filtered_pms, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading PMS data: {e}")
elif menu == "📊 Product Vault" and sub_menu == "Direct Equity":
    st.title("📈 Direct Equity")

    try:
        df_equity = pd.read_excel("product_vault.xlsx", sheet_name="Equity")
        df_equity.columns = df_equity.columns.str.strip()

        st.subheader("📋 Filter by Horizon")
        horizons = df_equity["Horizon"].dropna().unique().tolist()
        selected_horizon = st.radio("Select Horizon", options=horizons)
        filtered_equity = df_equity[df_equity["Horizon"] == selected_horizon]

        st.dataframe(filtered_equity, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading Equity data: {e}")
