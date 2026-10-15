# -*- coding: cp1252 -*-
import datetime
import os
import csv
import io
import streamlit as st

st.set_page_config(
    page_title="PET / CT Dózis Kalkulátor",
    page_icon="☢️",
    layout="centered"
)

st.title("☢️ PET / CT Dózis Kalkulátor")
st.markdown("Számítsd ki a PET és CT vizsgálatok kombinált effektív dózisát a megadott paraméterek alapján[cite: 6].")

# Adatbázisok a Tkinter app alapján[cite: 6]
pet_dict = {
    "C-11 metionin": {"c": 0.0055, "s": "ICRP Publ. 128"},
    "F-18 FDG": {"c": 0.0190, "s": "ICRP Publ. 106/128"},
    "Ga-68 DOTATATE / PSMA": {"c": 0.0230, "s": "ICRP Publ. 128"}
}

k_factors = {
    "Egész test / Általános (0.015)": 0.015,
    "Has - Kismedence (0.015)": 0.015,
    "Mellkas - Has - Kismedence (0.015)": 0.015,
    "Mellkas (0.014)": 0.014,
    "Nyak (0.0059)": 0.0059,
    "Koponya (0.0021)": 0.0021
}

with st.form("dose_form"):
    st.subheader("Adatok megadása")[cite: 6]
    taj = st.text_input("Beteg TAJ száma:")[cite: 6]
    
    pet_name = st.selectbox("PET Radiofarmakon:", sorted(list(pet_dict.keys())))[cite: 6]
    act = st.number_input("Beadott aktivitás (MBq):", min_value=0.1, value=370.0, step=10.0)[cite: 6]
    
    col1, col2 = st.columns(2)
    with col1:
        ctdi = st.number_input("CTDIvol (mGy):", min_value=0.0, value=10.0, step=1.0)[cite: 6]
    with col2:
        dlp = st.number_input("DLP (mGy*cm):", min_value=0.0, value=500.0, step=10.0)[cite: 6]
        
    regio = st.selectbox("Anatómiai régió (k-tényező):", list(k_factors.keys()))[cite: 6]
    
    submitted = st.form_submit_button("Számítás és Összegzés", type="primary")[cite: 6]

if submitted:
    if act <= 0 or dlp < 0 or ctdi < 0:
        st.error("Negatív vagy nullás érték nem adható meg!")[cite: 6]
    else:
        pet_data = pet_dict[pet_name][cite: 6]
        pet_coeff = pet_data["c"][cite: 6]
        pet_dose = act * pet_coeff[cite: 6]
        
        k_val = k_factors[regio][cite: 6]
        ct_dose = k_val * dlp[cite: 6]
        
        total_dose = pet_dose + ct_dose[cite: 6]
        taj_clean_val = taj.strip() if taj.strip() else "Ismeretlen"[cite: 6]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")[cite: 6]
        
        st.markdown("---")
        st.subheader("Eredmények")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric(label="PET Dózis", value=f"{pet_dose:.2f} mSv")
            st.caption(f"Együttható: {pet_coeff} mSv/MBq")[cite: 6]
        with col_res2:
            st.metric(label="CT Dózis", value=f"{ct_dose:.2f} mSv")
            st.caption(f"k-tényező: {k_val}")[cite: 6]
        with col_res3:
            st.metric(label="TELJES TEST SUMMA", value=f"{total_dose:.2f} mSv")
            
        # CSV adatok előkészítése letöltéshez
        taj_clean = "".join(c for c in taj_clean_val if c.isalnum() or c in ("-", "_"))[cite: 6]
        if not taj_clean:
            taj_clean = "Ismeretlen"[cite: 6]
            
        filename = f"taj_{taj_clean}_dozis.csv"[cite: 6]
        
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")[cite: 6]
        writer.writerow(["Dátum", "TAJ", "PET_Farmakon", "Aktivitás_MBq", "PET_Együttható", "PET_Dózis_mSv", "CT_Régió", "CTDI_mGy", "DLP_mGycm", "k_tényező", "CT_Dózis_mSv", "Összes_Dózis_mSv"])[cite: 6]
        writer.writerow([
            timestamp,
            taj_clean_val,
            pet_name,
            str(act).replace(".", ","),
            str(pet_coeff).replace(".", ","),
            f"{pet_dose:.2f}".replace(".", ","),
            regio,
            str(ctdi).replace(".", ","),
            str(dlp).replace(".", ","),
            str(k_val).replace(".", ","),
            f"{ct_dose:.2f}".replace(".", ","),
            f"{total_dose:.2f}".replace(".", ",")
        ])[cite: 6]
        
        csv_data = output.getvalue().encode("cp1252", errors="ignore")[cite: 6]
        
        st.download_button(
            label="📥 Eredmény mentése CSV-be",
            data=csv_data,
            file_name=filename,
            mime="text/csv"
        )[cite: 6]
