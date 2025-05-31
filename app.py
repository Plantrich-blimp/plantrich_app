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

# ✅ INTEGRATED ONBOARDING DROPDOWN
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

# ✅ Keep the rest of your working Mutual Fund, AIF, PMS, Equity logic as-is
elif menu == "📊 Product Vault" and sub_menu == "Mutual Funds":
    # YOUR EXISTING MUTUAL FUND LOGIC GOES HERE (already in your last working version)
    pass

elif menu == "📊 Product Vault" and sub_menu == "AIF":
    # YOUR EXISTING AIF LOGIC GOES HERE (already in your last working version)
    pass

elif menu == "📊 Product Vault" and sub_menu == "PMS":
    # YOUR EXISTING PMS LOGIC GOES HERE (already in your last working version)
    pass

elif menu == "📊 Product Vault" and sub_menu == "Direct Equity":
    # YOUR EXISTING EQUITY LOGIC GOES HERE (already in your last working version)
    pass
