import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import pandas as pd
import random
import io
import os
from datetime import datetime

# ============================================================
# PARKVISION AI
# Intelligent Urban Parking Analytics & Space Optimisation
# ============================================================

st.set_page_config(
    page_title="ParkVision AI",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(59,130,246,0.08), transparent 25%),
        radial-gradient(circle at 90% 20%, rgba(16,185,129,0.07), transparent 25%),
        #07111f;
    color: #f8fafc;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1627 0%, #07111f 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] * {
    color: #e5edf7;
}

/* Main container */

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* Hero */

.hero {
    padding: 38px;
    border-radius: 28px;
    background:
        linear-gradient(135deg,
            rgba(30,64,175,0.35),
            rgba(6,78,59,0.22)),
        rgba(15,23,42,0.88);
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 20px 60px rgba(0,0,0,0.28);
    margin-bottom: 25px;
}

.hero-badge {
    display: inline-block;
    padding: 7px 14px;
    border-radius: 999px;
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.25);
    color: #86efac;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.hero-title {
    font-size: 52px;
    line-height: 1.05;
    font-weight: 800;
    margin-top: 18px;
    margin-bottom: 12px;
}

.hero-title span {
    color: #60a5fa;
}

.hero-subtitle {
    font-size: 18px;
    color: #a9b8cc;
    max-width: 850px;
    line-height: 1.7;
}

/* Cards */

.metric-card {
    padding: 22px;
    border-radius: 20px;
    background: rgba(15,23,42,0.82);
    border: 1px solid rgba(255,255,255,0.08);
    min-height: 135px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.16);
}

.metric-label {
    color: #94a3b8;
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.metric-value {
    font-size: 36px;
    font-weight: 800;
    margin-top: 8px;
    color: #f8fafc;
}

.metric-small {
    color: #64748b;
    font-size: 12px;
    margin-top: 5px;
}

/* Section */

.section-title {
    font-size: 27px;
    font-weight: 750;
    margin-top: 30px;
    margin-bottom: 16px;
}

.section-description {
    color: #94a3b8;
    margin-bottom: 20px;
}

/* Info cards */

.info-card {
    padding: 24px;
    border-radius: 20px;
    background: rgba(15,23,42,0.72);
    border: 1px solid rgba(255,255,255,0.07);
    height: 100%;
}

.info-card h3 {
    margin-top: 0;
    font-size: 19px;
}

.info-card p {
    color: #9fb0c5;
    line-height: 1.7;
}

/* Status */

.status-low {
    padding: 18px 22px;
    border-radius: 16px;
    background: rgba(34,197,94,0.10);
    border: 1px solid rgba(34,197,94,0.25);
}

.status-moderate {
    padding: 18px 22px;
    border-radius: 16px;
    background: rgba(234,179,8,0.10);
    border: 1px solid rgba(234,179,8,0.25);
}

.status-high {
    padding: 18px 22px;
    border-radius: 16px;
    background: rgba(239,68,68,0.10);
    border: 1px solid rgba(239,68,68,0.25);
}

/* Buttons */

.stButton > button {
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.10);
    font-weight: 700;
}

/* File uploader */

[data-testid="stFileUploader"] {
    background: rgba(15,23,42,0.55);
    border-radius: 18px;
}

/* Footer */

.footer {
    margin-top: 50px;
    padding: 25px;
    text-align: center;
    color: #64748b;
    border-top: 1px solid rgba(255,255,255,0.07);
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_demo_analysis(image):
    """
    Temporary demonstration analyzer.

    This allows the dashboard to work before the trained
    computer vision model is connected.

    Later this function will be replaced by the real model.
    """

    width, height = image.size

    # Demo slot count
    total_slots = 20

    # Deterministic result based on image size
    seed_value = width + height
    random.seed(seed_value)

    occupied = random.randint(5, 17)
    available = total_slots - occupied

    occupancy = (occupied / total_slots) * 100

    return total_slots, occupied, available, occupancy


def get_congestion(occupancy):
    if occupancy < 40:
        return "LOW", "🟢", "Parking availability is good. Plenty of spaces are available."
    elif occupancy <= 75:
        return "MODERATE", "🟠", "Parking is moderately busy. Limited spaces may remain."
    else:
        return "HIGH", "🔴", "Parking is highly occupied. Consider another parking area."


def get_recommendation(occupancy, available):

    if available == 0:
        return (
            "🔴 Parking Full",
            "No available spaces were detected. Consider searching for another parking location."
        )

    if occupancy > 75:
        return (
            "⚠️ High Occupancy",
            f"Only {available} parking spaces remain. Consider another nearby parking area."
        )

    if occupancy >= 40:
        return (
            "🟠 Moderate Availability",
            f"{available} spaces are available. Proceed, but availability is becoming limited."
        )

    return (
        "🟢 Parking Available",
        f"{available} spaces are currently available. You can proceed to park."
    )


def generate_parking_overlay(image, total_slots, occupied):
    """
    Creates a visual demonstration overlay.

    The current version generates slot regions for UI demonstration.
    Once the trained model is connected, these boxes will come from
    actual computer vision predictions.
    """

    img = image.copy().convert("RGB")

    draw = ImageDraw.Draw(img)

    width, height = img.size

    columns = 5
    rows = int(np.ceil(total_slots / columns))

    slot_width = width / columns
    slot_height = height / rows

    slot_number = 0

    for r in range(rows):

        for c in range(columns):

            if slot_number >= total_slots:
                break

            x1 = int(c * slot_width + 8)
            y1 = int(r * slot_height + 8)

            x2 = int((c + 1) * slot_width - 8)
            y2 = int((r + 1) * slot_height - 8)

            if slot_number < occupied:
                label = "OCCUPIED"
                fill = (220, 38, 38)
            else:
                label = "AVAILABLE"
                fill = (34, 197, 94)

            # Transparent-like effect using outline
            draw.rectangle(
                [x1, y1, x2, y2],
                outline=fill,
                width=5
            )

            # Slot number
            draw.rectangle(
                [x1 + 4, y1 + 4, x1 + 85, y1 + 29],
                fill=fill
            )

            draw.text(
                (x1 + 8, y1 + 7),
                f"Slot {slot_number + 1}",
                fill="white"
            )

            slot_number += 1

    return img


def create_slot_dataframe(total_slots, occupied):

    data = []

    for i in range(total_slots):

        status = "Occupied" if i < occupied else "Available"

        data.append({
            "Slot": f"Slot {i + 1}",
            "Status": status,
            "Confidence": f"{random.randint(91, 99)}%"
        })

    return pd.DataFrame(data)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🚗 ParkVision AI")

    st.markdown(
        "<p style='color:#8fa3b8;'>Intelligent Urban Parking Analytics</p>",
        unsafe_allow_html=True
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Overview",
            "🅿️ Parking Analyzer",
            "📊 Analytics",
            "🧠 AI Model",
            "🧪 Testing",
            "ℹ️ About Project"
        ]
    )

    st.divider()

    st.markdown("### System Status")

    st.success("● Dashboard Online")

    st.caption("Computer Vision Engine")
    st.caption("Parking Intelligence Layer")
    st.caption("Streamlit Interface")

    st.divider()

    st.caption("ParkVision AI • 2026")


# ============================================================
# OVERVIEW PAGE
# ============================================================

if page == "🏠 Overview":

    st.markdown("""
    <div class="hero">

        <div class="hero-badge">
            ● AI-POWERED SMART CITY SOLUTION
        </div>

        <div class="hero-title">
            ParkVision <span>AI</span>
        </div>

        <div class="hero-subtitle">
            Intelligent parking occupancy detection and space optimisation
            powered by computer vision and machine learning.
            Turn parking images into real-time availability insights,
            congestion analysis and actionable recommendations.
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>Transforming Parking with AI</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='section-description'>"
        "ParkVision AI analyzes parking environments and converts visual "
        "information into simple, decision-ready parking intelligence."
        "</div>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>👁️ Computer Vision</h3>
            <p>
            Analyze parking images to identify individual parking
            spaces and determine their occupancy status.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>📊 Smart Analytics</h3>
            <p>
            Calculate occupancy, availability and congestion levels
            to transform predictions into useful parking insights.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="info-card">
            <h3>🧠 Decision Support</h3>
            <p>
            Generate recommendations that help users decide whether
            to proceed with parking or search for another location.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>How ParkVision Works</div>",
        unsafe_allow_html=True
    )

    steps = st.columns(5)

    workflow = [
        ("01", "Upload", "Parking image"),
        ("02", "Detect", "Parking spaces"),
        ("03", "Classify", "Occupied / Empty"),
        ("04", "Analyse", "Availability"),
        ("05", "Recommend", "Smart action")
    ]

    for col, (num, title, description) in zip(steps, workflow):

        with col:

            st.markdown(f"""
            <div class="info-card" style="text-align:center;">
                <div style="
                    font-size:13px;
                    color:#60a5fa;
                    font-weight:800;
                ">
                    {num}
                </div>

                <h3>{title}</h3>

                <p>{description}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>Core Capabilities</div>",
        unsafe_allow_html=True
    )

    features = [
        "Slot-level parking occupancy",
        "Available-space calculation",
        "Occupancy percentage",
        "Congestion classification",
        "Visual parking overlays",
        "Intelligent recommendations",
        "Interactive Streamlit dashboard",
        "Testing and performance analysis"
    ]

    feature_cols = st.columns(4)

    for i, feature in enumerate(features):

        with feature_cols[i % 4]:

            st.markdown(
                f"""
                <div style="
                    padding:14px;
                    margin-bottom:12px;
                    background:rgba(15,23,42,0.65);
                    border:1px solid rgba(255,255,255,0.07);
                    border-radius:14px;
                ">
                ✓ {feature}
                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# PARKING ANALYZER
# ============================================================

elif page == "🅿️ Parking Analyzer":

    st.markdown("""
    <div class="hero">

        <div class="hero-badge">
            LIVE PARKING ANALYSIS
        </div>

        <div class="hero-title">
            Parking <span>Analyzer</span>
        </div>

        <div class="hero-subtitle">
            Upload a parking lot image and generate parking
            occupancy insights.
        </div>

    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Parking Lot Image",
        type=["jpg", "jpeg", "png"],
        help="Upload a clear image of a parking area."
    )

    if uploaded_file is not None:

        image = Image.open(uploaded_file)

        st.session_state.uploaded_image = image

        st.markdown(
            "<div class='section-title'>Parking Analysis</div>",
            unsafe_allow_html=True
        )

        if st.button(
            "🚀 Analyze Parking",
            use_container_width=True
        ):

            with st.spinner("AI is analyzing the parking environment..."):

                total_slots, occupied, available, occupancy = (
                    create_demo_analysis(image)
                )

                congestion, icon, explanation = get_congestion(
                    occupancy
                )

                recommendation, recommendation_text = (
                    get_recommendation(
                        occupancy,
                        available
                    )
                )

                overlay = generate_parking_overlay(
                    image,
                    total_slots,
                    occupied
                )

                slot_df = create_slot_dataframe(
                    total_slots,
                    occupied
                )

                st.session_state.analysis_data = {
                    "total": total_slots,
                    "occupied": occupied,
                    "available": available,
                    "occupancy": occupancy,
                    "congestion": congestion,
                    "overlay": overlay,
                    "slots": slot_df,
                    "recommendation": recommendation,
                    "recommendation_text": recommendation_text
                }

                st.session_state.analysis_done = True

        if st.session_state.analysis_done:

            data = st.session_state.analysis_data

            st.markdown(
                "<div class='section-title'>Parking Overview</div>",
                unsafe_allow_html=True
            )

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Slots</div>
                    <div class="metric-value">{data["total"]}</div>
                    <div class="metric-small">Detected parking spaces</div>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Occupied</div>
                    <div class="metric-value">{data["occupied"]}</div>
                    <div class="metric-small">Currently occupied</div>
                </div>
                """, unsafe_allow_html=True)

            with c3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Available</div>
                    <div class="metric-value">{data["available"]}</div>
                    <div class="metric-small">Spaces available</div>
                </div>
                """, unsafe_allow_html=True)

            with c4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Occupancy</div>
                    <div class="metric-value">{data["occupancy"]:.1f}%</div>
                    <div class="metric-small">Parking utilisation</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(
                "<div class='section-title'>Visual Detection</div>",
                unsafe_allow_html=True
            )

            left, right = st.columns(2)

            with left:

                st.image(
                    image,
                    caption="Original Parking Image",
                    use_container_width=True
                )

            with right:

                st.image(
                    data["overlay"],
                    caption="ParkVision AI Analysis",
                    use_container_width=True
                )

            st.markdown(
                "<div class='section-title'>Parking Status</div>",
                unsafe_allow_html=True
            )

            if data["congestion"] == "LOW":

                st.markdown(
                    f"""
                    <div class="status-low">
                        <h3>{icon} Low Congestion</h3>
                        <p>{explanation}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif data["congestion"] == "MODERATE":

                st.markdown(
                    f"""
                    <div class="status-moderate">
                        <h3>{icon} Moderate Congestion</h3>
                        <p>{explanation}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"""
                    <div class="status-high">
                        <h3>{icon} High Congestion</h3>
                        <p>{explanation}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown(
                "<div class='section-title'>🧠 AI Recommendation</div>",
                unsafe_allow_html=True
            )

            st.info(
                f"**{data['recommendation']}**\n\n"
                f"{data['recommendation_text']}"
            )

            st.markdown(
                "<div class='section-title'>Slot-Level Results</div>",
                unsafe_allow_html=True
            )

            st.dataframe(
                data["slots"],
                use_container_width=True,
                hide_index=True
            )

    else:

        st.info(
            "👆 Upload a parking image above to start the analysis."
        )


# ============================================================
# ANALYTICS
# ============================================================

elif page == "📊 Analytics":

    st.markdown("""
    <div class="hero">

        <div class="hero-badge">
            PARKING INTELLIGENCE
        </div>

        <div class="hero-title">
            Parking <span>Analytics</span>
        </div>

        <div class="hero-subtitle">
            Understand parking utilisation and availability
            through clear visual analytics.
        </div>

    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.analysis_done:

        st.info(
            "Run an analysis from the Parking Analyzer page first."
        )

    else:

        data = st.session_state.analysis_data

        st.markdown(
            "<div class='section-title'>Utilisation Summary</div>",
            unsafe_allow_html=True
        )

        chart_data = pd.DataFrame({
            "Status": ["Occupied", "Available"],
            "Spaces": [
                data["occupied"],
                data["available"]
            ]
        })

        st.bar_chart(
            chart_data.set_index("Status")
        )

        st.markdown(
            "<div class='section-title'>Occupancy Distribution</div>",
            unsafe_allow_html=True
        )

        percentage_data = pd.DataFrame({
            "Category": ["Occupied", "Available"],
            "Percentage": [
                data["occupancy"],
                100 - data["occupancy"]
            ]
        })

        st.dataframe(
            percentage_data,
            use_container_width=True,
            hide_index=True
        )

        st.markdown(
            "<div class='section-title'>Congestion Interpretation</div>",
            unsafe_allow_html=True
        )

        st.write(
            f"""
            **Current occupancy:** {data["occupancy"]:.1f}%

            **Congestion level:** {data["congestion"]}

            **Available spaces:** {data["available"]}

            The system classifies parking utilisation according to
            predefined occupancy thresholds.
            """
        )


# ============================================================
# AI MODEL
# ============================================================

elif page == "🧠 AI Model":

    st.markdown("""
    <div class="hero">

        <div class="hero-badge">
            MACHINE LEARNING ENGINE
        </div>

        <div class="hero-title">
            AI <span>Model</span>
        </div>

        <div class="hero-subtitle">
            Model development, evaluation and computer vision
            pipeline information.
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>Model Architecture</div>",
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info-card">

    <h3>🧠 Parking Occupancy Classification</h3>

    <p>
    ParkVision AI is designed around a computer vision pipeline
    that identifies whether individual parking spaces are
    occupied or empty.
    </p>

    <p>
    The assignment permits either a crop-based classification
    approach or a full-image detection approach. The final
    trained model will be connected to this dashboard after
    model development.
    </p>

    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>Training Configuration</div>",
        unsafe_allow_html=True
    )

    model_info = pd.DataFrame({
        "Parameter": [
            "Image Size",
            "Training Epochs",
            "Dataset Split",
            "Task",
            "Output Classes"
        ],
        "Configuration": [
            "224 × 224 pixels",
            "15–30 epochs",
            "70% / 15% / 15%",
            "Binary Classification",
            "Occupied / Empty"
        ]
    })

    st.dataframe(
        model_info,
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        "<div class='section-title'>Evaluation Metrics</div>",
        unsafe_allow_html=True
    )

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("Accuracy", "—")

    with m2:
        st.metric("Validation Accuracy", "—")

    with m3:
        st.metric("Test Accuracy", "—")

    st.warning(
        "Model metrics will be displayed here after the real "
        "training model is connected."
    )


# ============================================================
# TESTING
# ============================================================

elif page == "🧪 Testing":

    st.markdown("""
    <div class="hero">

        <div class="hero-badge">
            VALIDATION & ROBUSTNESS
        </div>

        <div class="hero-title">
            Model <span>Testing</span>
        </div>

        <div class="hero-subtitle">
            Evaluate ParkVision AI using unseen parking images
            and challenging real-world conditions.
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>Testing Conditions</div>",
        unsafe_allow_html=True
    )

    conditions = [
        ("☀️", "Bright Lighting", "Test detection under strong daylight."),
        ("☁️", "Cloudy Conditions", "Evaluate reduced contrast and shadows."),
        ("🌧️", "Rainy Conditions", "Evaluate reflections and visibility."),
        ("📐", "Different Angles", "Test different camera perspectives."),
        ("🚗", "Partial Occlusion", "Evaluate partially visible vehicles.")
    ]

    cols = st.columns(5)

    for col, condition in zip(cols, conditions):

        icon, title, description = condition

        with col:

            st.markdown(
                f"""
                <div class="info-card">
                    <h3>{icon}</h3>
                    <strong>{title}</strong>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        "<div class='section-title'>Testing Checklist</div>",
        unsafe_allow_html=True
    )

    checks = [
        "Test using unseen images",
        "Evaluate different lighting conditions",
        "Evaluate different camera angles",
        "Record incorrect predictions",
        "Analyse false positives",
        "Analyse false negatives",
        "Improve dataset based on errors"
    ]

    for check in checks:

        st.checkbox(
            check,
            key=f"check_{check}"
        )


# ============================================================
# ABOUT PROJECT
# ============================================================

elif page == "ℹ️ About Project":

    st.markdown("""
    <div class="hero">

        <div class="hero-badge">
            ARTIFICIAL INTELLIGENCE • MACHINE LEARNING
        </div>

        <div class="hero-title">
            About <span>ParkVision AI</span>
        </div>

        <div class="hero-subtitle">
            A smart-city computer vision solution for intelligent
            parking monitoring and space optimisation.
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>The Problem</div>",
        unsafe_allow_html=True
    )

    st.write("""
    Urban parking areas often lack real-time information about
    available spaces. Drivers may spend unnecessary time searching
    for parking, contributing to congestion, fuel consumption and
    frustration.

    ParkVision AI addresses this problem by analysing parking lot
    images and identifying which parking spaces are occupied or
    available.
    """)

    st.markdown(
        "<div class='section-title'>The Solution</div>",
        unsafe_allow_html=True
    )

    st.write("""
    The system combines computer vision, machine learning,
    parking analytics and an interactive Streamlit dashboard.

    Instead of providing only raw predictions, ParkVision AI
    transforms the predictions into meaningful information such as
    total spaces, occupied spaces, available spaces, occupancy
    percentage, congestion level and parking recommendations.
    """)

    st.markdown(
        "<div class='section-title'>Technology Stack</div>",
        unsafe_allow_html=True
    )

    technologies = pd.DataFrame({
        "Technology": [
            "Python",
            "Streamlit",
            "Computer Vision",
            "Machine Learning",
            "Pandas",
            "NumPy",
            "Pillow"
        ],
        "Purpose": [
            "Application development",
            "Interactive web dashboard",
            "Parking image analysis",
            "Occupancy prediction",
            "Data analysis",
            "Numerical processing",
            "Image processing"
        ]
    })

    st.dataframe(
        technologies,
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        "<div class='section-title'>Project Pipeline</div>",
        unsafe_allow_html=True
    )

    st.code("""
Parking Image
      ↓
Image Preprocessing
      ↓
Computer Vision Model
      ↓
Slot Occupancy Detection
      ↓
Occupied / Available
      ↓
Parking Analytics
      ↓
Congestion Classification
      ↓
Recommendation Engine
      ↓
Streamlit Dashboard
""")

    st.markdown(
        "<div class='section-title'>Assignment Alignment</div>",
        unsafe_allow_html=True
    )

    st.success(
        "✓ Problem definition\n\n"
        "✓ Data preprocessing\n\n"
        "✓ Machine learning model\n\n"
        "✓ Parking insight logic\n\n"
        "✓ Streamlit dashboard\n\n"
        "✓ Testing and deployment\n\n"
        "✓ GitHub documentation"
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">

    <strong>ParkVision AI</strong><br>

    Intelligent Urban Parking Analytics & Space Optimisation

    <br><br>

    Built with Python • Machine Learning • Computer Vision • Streamlit

</div>
""", unsafe_allow_html=True)
