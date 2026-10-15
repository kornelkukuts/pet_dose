import datetime
import os
import csv
import io
import streamlit as st

st.set_page_config(
    page_title="PET / CT Dozis Kalkulátor",
    page_icon="☢️",
    layout="centered"
)

st.title("☢️ PET / CT Dozis Kalkulátor")
st.markdown("Számítsd ki a PET és CT vizsgálatok kombinált effektív dózisát a megadott paraméterek alapján.")

# Adatbázisok
pet_dict = {
    "C-11 metionin": {"c": 0.0055, "s": "ICRP Publ. 128"},
    "F-18 FDG": {"c": 0.0190, "s": "ICRP Publ. 106/128"},
    "Ga-68 DOTATATE / PSMA": {"c": 0.0230, "s": "ICRP Publ. 128"}
}

k_factors = {
    "Egesz test / Altalanos (0.015)": 0.015,
    "Has - Kismedence (0.015)": 0.015,
    "Mellkas - Has - Kismedence (0.015)": 0.015,
    "Mellkas (0.014)": 0.014,
    "Nyak (0.0059)": 0.0059,
    "Koponya (0.0021)": 0.0021
}

with st.form("dose_form"):
    st.subheader("Adatok megadása")
    taj = st.text_input("Beteg TAJ száma:")
    
    pet_name = st.selectbox("PET Radiofarmakon:", sorted(list(pet_dict.keys())))
    act = st.number_input("Beadott aktivitas (MBq):", min_value=0.1, value=370.0, step=10.0)
    
    col1, col2 = st.columns(2)
    with col1:
        ctdi = st.number_input("CTDIvol (mGy):", min_value=0.0, value=10.0, step=1.0)
    with col2:
        dlp = st.number_input("DLP (mGy*cm):", min_value=0.0, value=500.0, step=10.0)
        
    regio = st.selectbox("Anatomiai regio (k-tenyezo):", list(k_factors.keys()))
    
    submitted = st.form_submit_button("Szamitas es Osszegzes", type="primary")

if submitted:
    if act <= 0 or dlp < 0 or ctdi < 0:
        st.error("Negatív vagy nullás érték nem adható meg!")
    else:
        pet_data = pet_dict[pet_name]
        pet_coeff = pet_data["c"]
        pet_dose = act * pet_coeff
        
        k_val = k_factors[regio]
        ct_dose = k_val * dlp
        
        total_dose = pet_dose + ct_dose
        taj_clean_val = taj.strip() if taj.strip() else "Ismeretlen"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        st.markdown("---")
        st.subheader("Eredmények")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric(label="PET Dozis", value=f"{pet_dose:.2f} mSv")
            st.caption(f"Egyutthato: {pet_coeff} mSv/MBq")
        with col_res2:
            st.metric(label="CT Dozis", value=f"{ct_dose:.2f} mSv")
            st.caption(f"k-tenyezo: {k_val}")
        with col_res3:
            st.metric(label="TELJES TEST SUMMA", value=f"{total_dose:.2f} mSv")
            
        # CSV adatok előkészítése letöltéshez
        taj_clean = "".join(c for c in taj_clean_val if c.isalnum() or c in ("-", "_"))
        if not taj_clean:
            taj_clean = "Ismeretlen"
            
        filename = f"taj_{taj_clean}_dozis.csv"
        
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["Datum", "TAJ", "PET_Farmakon", "Aktivitas_MBq", "PET_Egyutthato", "PET_Dozis_mSv", "CT_Regio", "CTDI_mGy", "DLP_mGycm", "k_tenyezo", "CT_Dozis_mSv", "Osszes_Dozis_mSv"])
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
        ])
        
        csv_data = output.getvalue().encode("utf-8-sig")
        
        st.download_button(
            label="📥 Eredmény mentése CSV-be",
            data=csv_data,
            file_name=filename,
            mime="text/csv"
        )
