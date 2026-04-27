# Biopsia virtual renal del donante

Aplicación web en castellano para estimar, de forma orientativa, resultados de biopsia renal de día cero a partir de parámetros básicos del donante.

Inspirada en:

Yoo et al. A Machine Learning-Driven Virtual Biopsy System For Kidney Transplant Patients. Nature Communications. 2024.

## Salidas de la aplicación

La app estima:

- Probabilidad de arteriosclerosis, cv, moderada/severa
- Probabilidad de hialinosis arteriolar, ah, moderada/severa
- Probabilidad de IFTA moderada/severa
- Distribución aproximada Banff 0, 1, 2 y 3
- Porcentaje estimado de glomerulosclerosis

## Variables de entrada

- Edad
- Sexo
- Tipo de donante: vivo o fallecido
- Donación tras muerte circulatoria, DCD
- Muerte por causa cerebrovascular
- Hipertensión
- Diabetes
- HCV
- IMC
- Creatinina sérica
- Proteinuria

## Advertencia

Esta aplicación no reproduce el ensemble original validado del artículo.

Es una aproximación heurística autocontenida, diseñada para demostración, docencia y exploración conceptual.

No debe usarse como dispositivo médico, herramienta diagnóstica autónoma ni sustituto de una biopsia real o del juicio clínico.

## Despliegue en Render

Configuración recomendada:

- Build Command: `pip install -r requirements.txt`
- Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Ejemplos incluidos

La aplicación incluye presets basados en la Figura 3 del artículo:

### Figura 3A

- Edad: 63 años
- Sexo: femenino
- Donante fallecido
- DCD: sí
- Muerte cerebrovascular: no
- Hipertensión: no
- Diabetes: no
- HCV: no
- IMC: 22
- Creatinina: 2.0 mg/dL
- Proteinuria: no

### Figura 3B

- Edad: 51 años
- Sexo: masculino
- Donante fallecido
- DCD: no
- Muerte cerebrovascular: sí
- Hipertensión: sí
- Diabetes: no
- HCV: no
- IMC: 35.7
- Creatinina: 1.1 mg/dL
- Proteinuria: no

## Archivos del proyecto

- `app.py`
- `requirements.txt`
- `README.md`

## Nota sobre archivos grandes

No se incluye el ZIP del modelo original en este repositorio para mantener la aplicación ligera y compatible con GitHub y Render gratuitos.
