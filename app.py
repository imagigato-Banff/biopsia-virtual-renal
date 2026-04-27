import streamlit as st
from math import exp

st.set_page_config(
    page_title="Biopsia virtual renal",
    page_icon="🩺",
    layout="wide"
)

CUTOFFS = {
    "cv": 0.582,
    "ah": 0.596,
    "ifta": 0.637,
}

EXAMPLES = {
    "Personalizado": {
        "edad": 50,
        "sexo": "Masculino",
        "tipo_donante": "Fallecido",
        "dcd": "No",
        "muerte_cerebrovascular": "No",
        "hipertension": "No",
        "diabetes": "No",
        "hcv": "No",
        "imc": 26.0,
        "creatinina": 1.2,
        "proteinuria": "No",
    },
    "Figura 3A del artículo": {
        "edad": 63,
        "sexo": "Femenino",
        "tipo_donante": "Fallecido",
        "dcd": "Sí",
        "muerte_cerebrovascular": "No",
        "hipertension": "No",
        "diabetes": "No",
        "hcv": "No",
        "imc": 22.0,
        "creatinina": 2.0,
        "proteinuria": "No",
    },
    "Figura 3B del artículo": {
        "edad": 51,
        "sexo": "Masculino",
        "tipo_donante": "Fallecido",
        "dcd": "No",
        "muerte_cerebrovascular": "Sí",
        "hipertension": "Sí",
        "diabetes": "No",
        "hcv": "No",
        "imc": 35.7,
        "creatinina": 1.1,
        "proteinuria": "No",
    },
}


def clip(x, low, high):
    return max(low, min(high, x))


def sigmoid(x):
    return 1.0 / (1.0 + exp(-x))


def normalize_probs(values):
    safe = [max(0.0, float(v)) for v in values]
    total = sum(safe)
    if total == 0:
        return [0.25, 0.25, 0.25, 0.25]
    return [v / total for v in safe]


def n_age(age):
    return clip((age - 45.0) / 20.0, -2.5, 3.0)


def n_bmi(bmi):
    return clip((bmi - 26.0) / 6.0, -2.5, 3.0)


def n_creat(creat):
    return clip((creat - 1.0) / 0.8, -2.5, 4.0)


def yes_no_to_int(value):
    return 1 if value == "Sí" else 0


def sex_to_int(value):
    return 1 if value == "Masculino" else 0


def donor_type_to_int(value):
    return 1 if value == "Fallecido" else 0


def compute_risks(p):
    male = sex_to_int(p["sexo"])
    deceased = donor_type_to_int(p["tipo_donante"])
    dcd = yes_no_to_int(p["dcd"])
    cvd = yes_no_to_int(p["muerte_cerebrovascular"])
    htn = yes_no_to_int(p["hipertension"])
    dm = yes_no_to_int(p["diabetes"])
    hcv = yes_no_to_int(p["hcv"])
    prot = yes_no_to_int(p["proteinuria"])

    age = n_age(p["edad"])
    bmi = n_bmi(p["imc"])
    cr = n_creat(p["creatinina"])

    # Riesgo aproximado de lesión moderada/severa: Banff 2-3.
    # Fórmulas heurísticas inspiradas en la importancia relativa de variables del artículo.
    cv = sigmoid(
        -2.85
        + 1.10 * age
        + 0.60 * cr
        + 0.80 * bmi
        + 1.00 * htn
        + 0.65 * cvd
        + 0.10 * dcd
        + 0.18 * dm
        + 0.18 * prot
        + 0.10 * male
        + 0.12 * deceased
        + 0.05 * hcv
    )

    ah = sigmoid(
        -2.35
        + 0.90 * age
        + 0.35 * cr
        + 0.65 * bmi
        + 0.30 * htn
        + 0.80 * cvd
        + 0.05 * dcd
        + 0.25 * dm
        + 0.35 * prot
        + 0.15 * male
        + 0.10 * deceased
        + 0.05 * hcv
    )

    ifta = sigmoid(
        -2.20
        + 1.00 * age
        + 0.55 * cr
        + 0.50 * bmi
        + 0.65 * htn
        + 0.40 * cvd
        + 0.05 * dcd
        + 0.35 * dm
        + 0.30 * prot
        + 0.10 * male
        + 0.10 * deceased
        + 0.05 * hcv
    )

    # Estimación heurística del porcentaje de glomerulosclerosis.
    glom = (
        3.3
        + 3.0 * ((p["edad"] - 47.0) / 15.0)
        + 1.4 * ((p["imc"] - 27.0) / 5.5)
        + 2.0 * ((p["creatinina"] - 1.2) / 0.8)
        + 1.8 * htn
        + 1.4 * cvd
        + 0.4 * deceased
        + 0.4 * dcd
        + 0.3 * male
        + 0.3 * dm
        + 0.5 * prot
        + 0.2 * hcv
    )
    glom = clip(glom, 0.0, 45.0)

    return {
        "cv": cv,
        "ah": ah,
        "ifta": ifta,
        "glom": glom,
    }


def ordinal_probs_cv(risk):
    mild_share = clip(0.28 + 0.45 * risk, 0.18, 0.70)
    severe_share = clip(0.26 + 0.45 * risk, 0.18, 0.78)

    p1 = (1.0 - risk) * mild_share
    p0 = (1.0 - risk) - p1
    p3 = risk * severe_share
    p2 = risk - p3
    return normalize_probs([p0, p1, p2, p3])


def ordinal_probs_ah(risk):
    mild_share = clip(0.12 + 0.65 * risk, 0.10, 0.70)
    severe_share = clip(0.48 - 0.12 * risk, 0.25, 0.55)

    p1 = (1.0 - risk) * mild_share
    p0 = (1.0 - risk) - p1
    p3 = risk * severe_share
    p2 = risk - p3
    return normalize_probs([p0, p1, p2, p3])


def ordinal_probs_ifta(risk):
    mild_share = clip(0.45 + 0.35 * risk, 0.35, 0.80)
    severe_share = clip(0.10 + 0.65 * risk, 0.12, 0.75)

    p1 = (1.0 - risk) * mild_share
    p0 = (1.0 - risk) - p1
    p3 = risk * severe_share
    p2 = risk - p3
    return normalize_probs([p0, p1, p2, p3])


def classify(prob, cutoff):
    if prob >= cutoff:
        return "Predominio probable de lesión moderada/severa"
    if prob >= cutoff - 0.10:
        return "Zona intermedia / interpretar con prudencia"
    return "Predominio probable de lesión ausente o leve"


def p_to_pct(x):
    return f"{x * 100:.1f}%"


def show_lesion_block(title, key, risk, probs):
    labels = ["Banff 0", "Banff 1", "Banff 2", "Banff 3"]

    st.subheader(title)
    st.progress(int(round(risk * 100)))
    st.write(f"**Probabilidad moderada/severa, Banff 2-3:** {p_to_pct(risk)}")
    st.write(f"**Interpretación orientativa:** {classify(risk, CUTOFFS[key])}")
    st.write(f"**Cut-off de referencia del artículo:** {CUTOFFS[key]:.3f}")

    lines = []
    for label, prob in zip(labels, probs):
        lines.append(f"- **{label}:** {p_to_pct(prob)}")

    st.markdown("\n".join(lines))


st.title("Biopsia virtual renal del donante")
st.caption(
    "Aplicación orientativa en castellano inspirada en Yoo et al., Nature Communications 2024. "
    "No sustituye una biopsia real ni reproduce el ensemble original validado."
)

st.warning(
    "Esta herramienta es una aproximación heurística. No debe utilizarse como dispositivo médico, "
    "herramienta diagnóstica autónoma ni sustituto del juicio clínico o anatomopatológico."
)

preset_name = st.selectbox(
    "Ejemplo rápido",
    list(EXAMPLES.keys()),
    index=0,
    help="Puedes cargar los casos clínicos de la Figura 3 y luego modificar cualquier dato."
)
preset = EXAMPLES[preset_name]

sex_options = ["Masculino", "Femenino"]
donor_options = ["Vivo", "Fallecido"]
yn_options = ["No", "Sí"]


def idx(options, value):
    return options.index(value) if value in options else 0


with st.form("biopsia_virtual_form"):
    st.markdown("## Datos del donante")

    col1, col2, col3 = st.columns(3)

    with col1:
        edad = st.number_input(
            "Edad del donante, años",
            min_value=18,
            max_value=90,
            value=int(preset["edad"])
        )
        sexo = st.selectbox(
            "Sexo",
            sex_options,
            index=idx(sex_options, preset["sexo"])
        )
        tipo_donante = st.selectbox(
            "Tipo de donante",
            donor_options,
            index=idx(donor_options, preset["tipo_donante"])
        )
        imc = st.number_input(
            "IMC, kg/m²",
            min_value=10.0,
            max_value=60.0,
            value=float(preset["imc"]),
            step=0.1
        )

    with col2:
        creatinina = st.number_input(
            "Creatinina sérica, mg/dL",
            min_value=0.1,
            max_value=15.0,
            value=float(preset["creatinina"]),
            step=0.1
        )
        hipertension = st.selectbox(
            "Hipertensión",
            yn_options,
            index=idx(yn_options, preset["hipertension"])
        )
        diabetes = st.selectbox(
            "Diabetes",
            yn_options,
            index=idx(yn_options, preset["diabetes"])
        )
        proteinuria = st.selectbox(
            "Proteinuria",
            yn_options,
            index=idx(yn_options, preset["proteinuria"])
        )

    with col3:
        hcv = st.selectbox(
            "Hepatitis C, HCV",
            yn_options,
            index=idx(yn_options, preset["hcv"])
        )
        dcd = st.selectbox(
            "Donación tras muerte circulatoria, DCD",
            yn_options,
            index=idx(yn_options, preset["dcd"])
        )
        muerte_cerebrovascular = st.selectbox(
            "Muerte por causa cerebrovascular",
            yn_options,
            index=idx(yn_options, preset["muerte_cerebrovascular"])
        )

    submitted = st.form_submit_button("Calcular biopsia virtual")

if submitted:
    if tipo_donante == "Vivo":
        dcd = "No"
        muerte_cerebrovascular = "No"
        st.info("En donante vivo se fuerzan DCD = No y muerte cerebrovascular = No.")

    if tipo_donante == "Fallecido" and dcd == "Sí" and muerte_cerebrovascular == "Sí":
        st.error(
            "Revisión requerida: en esta versión simplificada no se permite marcar simultáneamente "
            "DCD = Sí y muerte cerebrovascular = Sí."
        )
        st.stop()

    patient = {
        "edad": edad,
        "sexo": sexo,
        "tipo_donante": tipo_donante,
        "dcd": dcd,
        "muerte_cerebrovascular": muerte_cerebrovascular,
        "hipertension": hipertension,
        "diabetes": diabetes,
        "hcv": hcv,
        "imc": imc,
        "creatinina": creatinina,
        "proteinuria": proteinuria,
    }

    results = compute_risks(patient)
    cv_probs = ordinal_probs_cv(results["cv"])
    ah_probs = ordinal_probs_ah(results["ah"])
    ifta_probs = ordinal_probs_ifta(results["ifta"])

    st.markdown("## Resultado resumido")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("cv moderada/severa", p_to_pct(results["cv"]))
    m2.metric("ah moderada/severa", p_to_pct(results["ah"]))
    m3.metric("IFTA moderada/severa", p_to_pct(results["ifta"]))
    m4.metric("Glomerulosclerosis estimada", f"{results['glom']:.1f}%")

    st.markdown("## Detalle por lesión")

    c1, c2 = st.columns(2)

    with c1:
        show_lesion_block("Arteriosclerosis, cv", "cv", results["cv"], cv_probs)
        st.markdown("---")
        show_lesion_block("Hialinosis arteriolar, ah", "ah", results["ah"], ah_probs)

    with c2:
        show_lesion_block("Fibrosis intersticial y atrofia tubular, IFTA", "ifta", results["ifta"], ifta_probs)
        st.markdown("---")
        st.subheader("Glomerulosclerosis")
        st.progress(int(round(min(results["glom"], 100))))
        st.write(f"**Porcentaje estimado de glomerulosclerosis:** {results['glom']:.1f}%")

    with st.expander("Ver datos usados en el cálculo"):
        for key, value in patient.items():
            st.write(f"**{key}:** {value}")

else:
    st.info("Rellena el formulario y pulsa «Calcular biopsia virtual».")
