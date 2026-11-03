
import streamlit as st
import pandas as pd
import joblib
import os
import numpy as np

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="VariantAI",
    page_icon="🧬",
    layout="centered"
)

# --------------------------------------------------
# Application header
# --------------------------------------------------
st.title("🧬 VariantAI")
st.subheader("Protein Variant Pathogenicity Prediction")

st.write(
    "An explainable machine-learning research prototype "
    "for exploring protein variant classifications."
)

st.warning(
    "Research and educational use only. Predictions are not "
    "clinical diagnoses or independently validated classifications."
)

# --------------------------------------------------
# Model loading
# --------------------------------------------------
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "variantai_model.pkl"
)

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

if not os.path.exists(MODEL_PATH):
    st.error(
        "Model file not found. Place variantai_model.pkl "
        "inside the models folder."
    )
    st.stop()

try:
    model = load_model()
except Exception as error:
    st.error(f"Could not load model: {error}")
    st.stop()

# --------------------------------------------------
# Variant input form
# --------------------------------------------------
st.markdown("### Enter variant details")

gene = st.text_input(
    "Gene name",
    placeholder="e.g., BRCA1"
)

amino_acids = list("ACDEFGHIKLMNPQRSTVWY")

original_aa = st.selectbox(
    "Original amino acid",
    amino_acids
)

position = st.number_input(
    "Amino-acid position",
    min_value=1,
    value=100,
    step=1
)

new_aa = st.selectbox(
    "New amino acid",
    amino_acids,
    index=1
)

# --------------------------------------------------
# Prediction
# --------------------------------------------------
if st.button("Predict variant class", type="primary"):

    if not gene.strip():
        st.warning("Please enter a gene name.")

    elif original_aa == new_aa:
        st.warning("Choose a different amino acid.")

    else:
        # Match the feature names used during model training
        input_data = pd.DataFrame([{
            "Gene": gene.strip().split(",")[0].strip(),
            "Original_AA": original_aa,
            "New_AA": new_aa,
            "Position_log": np.log1p(position)
        }])

        try:
            prediction = int(model.predict(input_data)[0])

            st.markdown("### Prediction")

            if prediction == 1:
                st.error("Pathogenic-labelled class predicted")
            else:
                st.success("Benign-labelled class predicted")

            if hasattr(model, "predict_proba"):
                probabilities = model.predict_proba(input_data)[0]

                results = pd.DataFrame({
                    "Model class": [
                        str(c) for c in model.classes_
                    ],
                    "Probability": [
                        f"{p:.2%}" for p in probabilities
                    ]
                })

                st.write("Model output probabilities")
                st.dataframe(results, hide_index=True)

            st.caption(
                "Predictions reflect patterns learned from the training "
                "data and may be inaccurate. They are not clinical "
                "classifications and must not guide medical decisions."
            )

        except Exception as error:
            st.error(f"Prediction failed: {error}")
