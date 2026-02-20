import streamlit as st
from data_engine import generate_data
from model_engine import train_model, predict_energy
from optimizer import detect_inefficiency

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from datetime import datetime


# =====================================================
# PDF GENERATOR
# =====================================================

def generate_pdf_report(
    building_type,
    area,
    floors,
    hvac_type,
    actual_energy,
    predicted_energy,
    predicted_cost,
    emissions,
    trees_required,
):
    file_path = "EnergySense_Report.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("EnergySense - Digital Twin Report", styles["Heading1"]))
    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"],
        )
    )
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Building Configuration", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(
            f"""
            Building Type: {building_type}<br/>
            Total Area: {area} sqm<br/>
            Floors: {floors}<br/>
            HVAC Type: {hvac_type}
            """,
            styles["Normal"],
        )
    )

    elements.append(Spacer(1, 20))

    data = [
        ["Metric", "Value"],
        ["Actual Energy (kWh)", round(actual_energy, 2)],
        ["Predicted Energy (kWh)", round(predicted_energy, 2)],
        ["Predicted Cost (₹)", round(predicted_cost, 2)],
        ["CO₂ Emissions (kg)", round(emissions, 2)],
        ["Trees Required to Offset", round(trees_required, 1)],
    ]

    table = Table(data, colWidths=[260, 180])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))

    elements.append(table)
    doc.build(elements)
    return file_path


# =====================================================
# MAIN APP
# =====================================================

def main():
    st.set_page_config(layout="wide")

    st.title("⚡ EnergySense Digital Twin")
    st.caption("Smart Energy Optimization for Commercial Buildings")

    st.markdown("---")

    # =====================================================
    # DIGITAL TWIN CONFIGURATION
    # =====================================================

    st.markdown("## 🏢 Building Configuration")

    col1, col2, col3 = st.columns(3)

    building_type = col1.selectbox(
        "Building Type",
        ["Office", "Educational", "Mall", "Hospital"]
    )

    area = col2.number_input("Total Area (sqm)", 1000, 50000, 5000, step=500)
    floors = col3.number_input("Number of Floors", 1, 50, 5)

    col4, col5 = st.columns(2)

    hvac_type = col4.selectbox(
        "HVAC System Type",
        ["Central HVAC", "VRV/VRF", "Split Units"]
    )

    intensity_level = col5.selectbox(
        "Energy Intensity",
        ["Low", "Medium", "High"]
    )

    # =====================================================
    # BASE DATA
    # =====================================================

    base_df = generate_data()

    # Building area scaling
    area_multiplier = area / 5000
    floor_multiplier = floors / 5

    intensity_map = {"Low": 0.9, "Medium": 1.0, "High": 1.2}
    hvac_map = {
        "Central HVAC": 1.2,
        "VRV/VRF": 1.1,
        "Split Units": 1.0,
    }

    building_multiplier = area_multiplier * floor_multiplier
    intensity_multiplier = intensity_map[intensity_level]
    hvac_multiplier = hvac_map[hvac_type]

    # Apply digital twin scaling
    base_df["energy_kwh"] *= building_multiplier * intensity_multiplier * hvac_multiplier
    base_df["occupancy"] *= building_multiplier

    model = train_model(base_df)
    base_df["prediction"] = predict_energy(model, base_df)

    actual_energy = base_df["energy_kwh"].sum()

    st.markdown("---")

    # =====================================================
    # EXECUTIVE SNAPSHOT
    # =====================================================

    st.markdown("## 📊 Executive Snapshot")

    st.metric("Total Energy Usage (kWh)", round(actual_energy, 2))
    st.line_chart(base_df[["energy_kwh", "prediction"]])

    # =====================================================
    # CLIMATE
    # =====================================================

    emission_factor = 0.82
    emissions = actual_energy * emission_factor
    trees_required = emissions / 21
    predicted_cost = actual_energy * 8

    colX, colY = st.columns(2)
    colX.metric("CO₂ Emissions (kg)", round(emissions, 2))
    colY.metric("Trees Required to Offset", round(trees_required, 1))

    st.markdown("---")

    # =====================================================
    # PDF EXPORT
    # =====================================================

    st.markdown("## 📄 Export Digital Twin Report")

    if st.button("Generate PDF Report"):
        pdf_path = generate_pdf_report(
            building_type,
            area,
            floors,
            hvac_type,
            actual_energy,
            actual_energy,
            predicted_cost,
            emissions,
            trees_required,
        )

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="Download Report",
                data=f,
                file_name="EnergySense_DigitalTwin_Report.pdf",
                mime="application/pdf",
            )


if __name__ == "__main__":
    main()