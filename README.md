# AI Security Red Team Assessment

## Overview

This project is an individual AI security red-team assessment conducted against a locally deployed and controlled machine-learning system.

The assessment simulates a red-team engagement against an AI/ML inference pipeline by:

* Reconnaissance of the model-serving API
* Analysis of a pre-trained CIFAR-10 image-classification model
* Testing the model with adversarial inputs
* Testing the serving pipeline with malformed and oversized inputs
* Demonstrating successful end-to-end adversarial attacks
* Measuring adversarial attack impact
* Implementing model and API mitigations
* Retesting the mitigations
* Containerizing the target with Docker
* Mapping findings to MITRE ATLAS and NIST AI RMF
* Documenting the assessment and AI-assisted development process

> **Scope:** All testing was performed against locally owned and controlled systems created for this assessment. No external systems, unauthorized infrastructure, or real personal data were targeted.

---

## Assessment Objectives

The assessment focuses on three main areas.

### 1. Adversarial Machine Learning

Determine whether the target model can be manipulated using adversarial inputs.

The primary attack used was:

* FGSM — Fast Gradient Sign Method

The assessment measures:

* Clean prediction
* Adversarial prediction
* Attack success
* Confidence
* Attack success rate (ASR)
* Effect of different perturbation magnitudes

### 2. AI/ML Pipeline Security

Assess weaknesses in the model-serving pipeline, including:

* API input validation
* Image decoding and validation
* File and image-size restrictions
* Error handling
* API information exposure
* Model serving
* Docker deployment
* Dependency management
* Server configuration

### 3. Security Mitigation

Implement and retest practical mitigations for identified weaknesses.

Two mitigation areas were evaluated:

* API input validation and resource controls
* Adversarial training for improved model robustness

---

# Target System

## Pre-trained Model

The assessment uses the publicly available pre-trained model:

`manasyesuarthana/cifar10-simple-cnn-pytorch`

The model was selected as a simple, reproducible CIFAR-10 CNN suitable for a controlled AI security assessment.

The model weights were downloaded and reconstructed locally. The target model was **not trained from scratch for this assessment**.

Model weights:

```text
model/weights/pytorch_model.bin
```

A defended model produced during the mitigation experiment is stored separately:

```text
model/weights/defended_model.pth
```

## Model Architecture

The reconstructed model contains:

```text
Input: CIFAR-10 RGB image
        │
        ▼
Conv1: 3 → 32
        │
        ▼
Conv2: 32 → 64
        │
        ▼
Conv3: 64 → 128
        │
        ▼
Flatten
        │
        ▼
FC1: 2048 → 512
        │
        ▼
FC2: 512 → 10
        │
        ▼
CIFAR-10 class prediction
```

The ten CIFAR-10 classes are:

```text
airplane
automobile
bird
cat
deer
dog
frog
horse
ship
truck
```

Each CIFAR-10 image is a `32 × 32` RGB image.

---

# Target Architecture

The final target architecture is:

```text
                    RED TEAM TESTER
                          │
             ┌────────────┴────────────┐
             │                         │
     Adversarial Images         Malformed Inputs
     API Requests               Oversized Images
     Reconnaissance
             │                         │
             └────────────┬────────────┘
                          ▼
                 Docker Container
                 ai-security-target
                          │
                          ▼
                     FastAPI
                     :8000
                    /       \
                   /         \
             /health       /predict
                              │
                              ▼
                    Input Validation
                              │
                    ┌─────────┴─────────┐
                    │                   │
                 Valid               Invalid
                    │                   │
                    ▼                400 / 413
              Preprocessing
                    │
                    ▼
                PyTorch CNN
                    │
                    ▼
                Prediction
```

The target API provides:

```text
GET  /health
POST /predict
```

The Dockerized service is exposed through port `8000`.

---

# Technology Stack

| Component           | Technology               |
| ------------------- | ------------------------ |
| Language            | Python 3.11              |
| ML Framework        | PyTorch                  |
| Dataset             | CIFAR-10                 |
| Model               | Pre-trained SimpleCNN    |
| API                 | FastAPI                  |
| Server              | Uvicorn                  |
| Image Processing    | Pillow                   |
| Containerization    | Docker                   |
| Adversarial Attack  | FGSM                     |
| Documentation       | Markdown                 |
| Security Frameworks | MITRE ATLAS, NIST AI RMF |
| Version Control     | Git / GitHub             |

---

# Project Structure

The implemented project is organized around the actual assessment workflow:

```text
ai-security-red-team-assessment/
│
├── api/
│   └── main.py
│
├── model/
│   ├── model.py
│   ├── inspect_model.py
│   ├── baseline.py
│   ├── predict.py
│   ├── fgsm.py
│   ├── fgsm_scan.py
│   ├── fgsm_evaluation.py
│   ├── fgsm_second.py
│   ├── adversarial_training.py
│   ├── test_defense.py
│   ├── clean_accuracy_comparison.py
│   └── weights/
│       ├── pytorch_model.bin
│       └── defended_model.pth
│
├── results/
│   ├── adversarial/
│   │   ├── clean_cat.png
│   │   ├── fgsm_cat_to_frog.png
│   │   ├── clean_frog.png
│   │   └── fgsm_frog_to_deer.png
│   ├── openapi.json
│   ├── reconnaissance.md
│   ├── attack_report.md
│   ├── pipeline_review.md
│   ├── model_robustness_mitigation.md
│   └── framework_mapping.md
│
├── requirements.txt
├── Dockerfile
├── AI_USAGE_LOG.md
└── README.md
```

---

# Red-Team Methodology

The assessment followed this workflow:

```text
Reconnaissance
      ↓
Attack Surface Identification
      ↓
Vulnerability Discovery
      ↓
Attack Development
      ↓
Attack Execution
      ↓
Evidence Collection
      ↓
Impact Analysis
      ↓
Mitigation
      ↓
Retesting
      ↓
Documentation
```

---

# Reconnaissance Findings

The local FastAPI target was tested for common serving-pipeline weaknesses.

### API Information Exposure

The FastAPI service exposed:

```text
/docs
/openapi.json
```

The OpenAPI specification revealed the available API structure and `/predict` file-upload interface.

The server also exposed a basic Uvicorn server header.

These findings represent information exposure and production-hardening considerations rather than standalone model-compromise vulnerabilities.

### Malformed Image Handling

Initially, a non-image file submitted to `/predict` resulted in:

```text
HTTP 500 Internal Server Error
```

The underlying image-decoding failure was not handled as a controlled client error.

The API was subsequently hardened to return:

```text
HTTP 400 Bad Request
{"detail":"Invalid image file."}
```

### Oversized Image Handling

A large `2000 × 2000` image was initially accepted and passed to inference.

The API was subsequently hardened with an image-dimension limit.

The same type of oversized image now returns:

```text
HTTP 413 Request Entity Too Large
{"detail":"Image dimensions are too large."}
```

Detailed reconnaissance findings are documented in:

```text
results/reconnaissance.md
```

---

# Adversarial Machine Learning

## FGSM

The Fast Gradient Sign Method was used to generate adversarial inputs.

The basic workflow was:

```text
Clean Image
     ↓
Correct Prediction
     ↓
Calculate Input Gradient
     ↓
Apply FGSM Perturbation
     ↓
Adversarial Image
     ↓
Incorrect Prediction
```

The main experiment used:

```text
epsilon = 0.03
```

---

# Successful Adversarial Examples

Two successful adversarial examples were generated.

## Attack 1 — Cat → Frog

```text
True class:          cat
Clean prediction:    cat
Adversarial input:   FGSM ε=0.03
Adversarial class:   frog
```

The adversarial image was then submitted to the Dockerized API.

API result:

```text
HTTP 200 OK

{
    "predicted_class": "frog",
    "confidence": 0.6578
}
```

Therefore, the adversarial input remained effective after passing through the complete serving pipeline.

Evidence:

```text
results/adversarial/clean_cat.png
results/adversarial/fgsm_cat_to_frog.png
```

## Attack 2 — Frog → Deer

```text
True class:          frog
Clean prediction:    frog
Adversarial input:   FGSM ε=0.03
Adversarial class:   deer
```

Dockerized API result:

```text
HTTP 200 OK

{
    "predicted_class": "deer",
    "confidence": 0.9526
}
```

Evidence:

```text
results/adversarial/clean_frog.png
results/adversarial/fgsm_frog_to_deer.png
```

The confidence values represent the model's confidence in the returned adversarial prediction; they are not attack-success percentages.

---

# Large-Scale FGSM Evaluation

The model was evaluated across the CIFAR-10 test set using multiple epsilon values.

| Epsilon | Accuracy | Attack Success Rate |
| ------: | -------: | ------------------: |
|    0.00 |  100.00% |               0.00% |
|    0.01 |   74.03% |              25.97% |
|    0.03 |   39.85% |              60.15% |
|    0.05 |   22.89% |              77.11% |
|    0.10 |    7.66% |              92.34% |

The attack success rate is interpreted according to the evaluation methodology used by the experiment.

At `ε = 0.03`, the experiment recorded a **60.15% attack success rate among the evaluated initially correct predictions**.

The complete experiment is implemented in:

```text
model/fgsm_evaluation.py
```

---

# Model Robustness Mitigation

Adversarial training was used as a model-level mitigation.

Configuration:

```text
Epsilon:       0.03
Epochs:        1
Batch size:    64
Learning rate: 0.0001
```

The defended model was saved as:

```text
model/weights/defended_model.pth
```

Using the same comparison methodology:

| Model    | Initially Correct | Successful FGSM Attacks |    ASR |
| -------- | ----------------: | ----------------------: | -----: |
| Original |              6114 |                    4158 | 68.01% |
| Defended |              6953 |                    2995 | 43.07% |

The observed ASR reduction was:

```text
68.01% → 43.07%
```

A clean-accuracy comparison also recorded:

```text
Original:  61.14%
Defended:  69.53%
```

These results are specific to this experiment. They do not establish that adversarial training universally provides the same improvement against other attacks or models.

Limitations include:

* Only one adversarial-training epoch was used.
* The primary attack evaluated was FGSM.
* Stronger attacks such as PGD were not implemented.
* The evaluation used a specific epsilon and model configuration.
* Robustness against black-box attacks was not evaluated.

Detailed results are documented in:

```text
results/model_robustness_mitigation.md
```

---

# API Security Mitigation

The serving API was hardened with:

### File-size restriction

Maximum file size:

```text
5 MB
```

### Image-dimension restriction

Maximum dimensions:

```text
1024 × 1024
```

### Image validation

Uploaded content is decoded and verified before inference.

Invalid image content now produces:

```text
HTTP 400
```

### Controlled error handling

Image-decoding failures are handled explicitly instead of producing an unhandled server exception.

### Retesting

The mitigated API was tested again using:

```text
Malformed image  → 400
Oversized image  → 413
Valid adversarial image → 200
```

Importantly, the API hardening controls malformed and oversized inputs but **does not eliminate adversarial ML vulnerability**. A valid adversarial image can still pass normal image validation and reach the model.

---

# Docker Deployment

The target was containerized using:

```text
python:3.11-slim
```

The image is:

```text
ai-security-target:latest
```

The container runs:

```text
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

The deployed service was verified with:

```powershell
docker run --rm -p 8000:8000 ai-security-target
```

Health check:

```text
GET /health
→ HTTP 200
→ {"status":"healthy"}
```

The Dockerized API was then tested with both successful adversarial examples.

This demonstrated:

```text
Adversarial Image
       ↓
Docker
       ↓
FastAPI
       ↓
Preprocessing
       ↓
PyTorch Model
       ↓
Incorrect Prediction
```

---

# Framework Mapping

## MITRE ATLAS

The adversarial ML findings were mapped to relevant MITRE ATLAS concepts, including:

* **AML.T0043 — Craft Adversarial Data**
* **AML.T0015 — Evade AI Model**

The assessment also considers attack verification as part of the red-team workflow.

Detailed mapping:

```text
results/framework_mapping.md
```

## NIST AI RMF

The assessment considers the four NIST AI RMF Core functions:

```text
GOVERN
MAP
MEASURE
MANAGE
```

The project applies these concepts through:

* **GOVERN:** documentation, AI usage tracking, reproducibility, and project controls
* **MAP:** defining the target, scope, attack surface, assumptions, and limitations
* **MEASURE:** baseline testing, FGSM evaluation, API testing, and mitigation measurements
* **MANAGE:** implementing and retesting model and API mitigations

Detailed mapping:

```text
results/framework_mapping.md
```

---

# Key Findings

| Area                 | Finding                        | Result                             |
| -------------------- | ------------------------------ | ---------------------------------- |
| ML Security          | FGSM adversarial vulnerability | Successful                         |
| ML Security          | Cat → Frog                     | Successful                         |
| ML Security          | Frog → Deer                    | Successful                         |
| API Security         | Invalid image handling         | 500 → 400 after mitigation         |
| API Security         | Oversized image handling       | Rejected with 413 after mitigation |
| Information Exposure | OpenAPI/docs exposure          | Identified                         |
| Information Exposure | Server fingerprinting          | Identified                         |
| Model Robustness     | Adversarial training           | ASR reduced in tested experiment   |
| Deployment           | Dockerized serving pipeline    | Successfully verified              |

---

# Main Evidence

### Adversarial examples

```text
results/adversarial/
```

### Reconnaissance

```text
results/reconnaissance.md
```

### Attack report

```text
results/attack_report.md
```

### Pipeline review

```text
results/pipeline_review.md
```

### Model mitigation

```text
results/model_robustness_mitigation.md
```

### Framework mapping

```text
results/framework_mapping.md
```

### API specification

```text
results/openapi.json
```

### AI usage documentation

```text
AI_USAGE_LOG.md
```

---

# Reproducibility

## Python Environment

Create the virtual environment:

```powershell
python -m venv venv
```

Activate on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run the API Locally

```powershell
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

## Run the Dockerized API

Build:

```powershell
docker build -t ai-security-target .
```

Run:

```powershell
docker run --rm -p 8000:8000 ai-security-target
```

Test:

```powershell
curl.exe -i http://127.0.0.1:8000/health
```

Test an adversarial image:

```powershell
curl.exe -i -X POST "http://127.0.0.1:8000/predict" -F "file=@results/adversarial/fgsm_cat_to_frog.png"
```

---

# Git Development History

The project was developed incrementally and documented through Git commits.

Recent assessment-stage commits include:

```text
5845edd  Add Docker deployment and framework mapping updates
bf6fca3  Add AI serving pipeline security review
76a40d6  Add AI security red team attack report
9121bc3  Add MITRE ATLAS and NIST AI RMF mapping
```

This commit history provides a development trail for the assessment.

---

# Limitations

This assessment was performed against a controlled local target and therefore does not represent a complete production security assessment.

Important limitations include:

* The target is a small CIFAR-10 CNN.
* The model is pre-trained and reconstructed locally.
* FGSM was the primary adversarial attack.
* PGD was not implemented.
* Black-box adversarial attacks were not evaluated.
* No real production traffic was used.
* No external infrastructure was tested.
* Rate limiting was considered but not implemented.
* Authentication was not implemented because the target was intentionally local.
* Container hardening was not evaluated as a full production container-security audit.
* The adversarial-training experiment used one epoch.
* Results are specific to the tested model, dataset, preprocessing, and attack configuration.

---

# Deliverables

The assessment includes:

* [x] Pre-trained AI/ML target
* [x] Model inspection and baseline evaluation
* [x] FastAPI serving pipeline
* [x] Pipeline reconnaissance
* [x] Successful adversarial example #1
* [x] Successful adversarial example #2
* [x] Large-scale FGSM evaluation
* [x] API security findings
* [x] Model robustness mitigation
* [x] API security mitigation
* [x] Dockerized deployment
* [x] End-to-end attack testing through Docker
* [x] Attack report
* [x] Pipeline security review
* [x] MITRE ATLAS mapping
* [x] NIST AI RMF mapping
* [x] AI Usage Log
* [x] Reproducible code and setup instructions
* [ ] 3–5 minute video walkthrough
* [ ] Final presentation/Q&A preparation

---

# AI Usage

AI tools were used as development assistants for:

* Understanding AI security concepts
* Understanding the CIFAR-10 model architecture
* Debugging implementation issues
* Reviewing security-testing approaches
* Explaining adversarial ML concepts
* Developing documentation
* Reviewing project structure
* Preparing presentation material

AI assistance is documented separately in:

```text
AI_USAGE_LOG.md
```

The final implementation and results were reviewed and tested locally by the project author.

---

# Scope and Rules of Engagement

## In Scope

* Locally controlled AI model
* Locally controlled API
* Locally running Docker container
* Self-generated adversarial examples
* Security testing of the project's own serving pipeline
* Model robustness experiments
* API security testing

## Out of Scope

* External systems
* Unauthorized infrastructure
* Other participants' systems
* Public production APIs
* Real personal data
* Third-party production services
* Systems not owned or controlled for this assessment

All testing was performed against the controlled assessment environment.

---

# Project Status

```text
FINAL TECHNICAL ASSESSMENT PHASE
```

Completed:

* [x] Pre-trained model selected and deployed
* [x] Model architecture inspected
* [x] Baseline evaluation
* [x] Prediction testing
* [x] FastAPI target
* [x] API reconnaissance
* [x] FGSM implementation
* [x] Successful adversarial examples
* [x] Large-scale FGSM evaluation
* [x] API hardening
* [x] Adversarial training mitigation
* [x] Mitigation testing
* [x] Docker deployment
* [x] End-to-end Docker attack testing
* [x] Attack report
* [x] Pipeline review
* [x] MITRE ATLAS mapping
* [x] NIST AI RMF mapping
* [x] AI usage documentation

Remaining submission tasks:

* [ ] Final README review
* [ ] Final GitHub push/verification
* [ ] 3–5 minute video walkthrough
* [ ] Final presentation preparation
* [ ] Final Q&A preparation

---

## Author

**Individual AI Security Red Team Assessment**

Developed as part of the Ethiopian Artificial Intelligence 7-day AI Security Red Team Challenge.
