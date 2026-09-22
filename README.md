# AI Security Red Team Assessment

## Overview

This project is an individual AI security red-team assessment conducted against a locally built and controlled machine-learning system.

The objective is to simulate a realistic red-team engagement against an AI/ML inference pipeline by:

* Building and training a PyTorch image-classification model.
* Serving the model through a local API.
* Identifying weaknesses in the ML model and serving pipeline.
* Creating successful adversarial inputs.
* Investigating system-level vulnerabilities and metadata leakage.
* Implementing and testing security mitigations.
* Mapping identified risks and mitigations to relevant MITRE ATLAS and NIST AI Risk Management Framework concepts.

> **Scope:** All attacks and security testing are performed exclusively against locally owned and controlled systems created for this assessment. No external systems or real personal data are targeted.

---

## Project Objectives

The assessment focuses on three main areas:

### 1. Adversarial Machine Learning

Investigate whether the image-classification model can be manipulated using adversarial inputs.

Planned techniques include:

* FGSM (Fast Gradient Sign Method)
* PGD (Projected Gradient Descent)
* Comparison of clean and adversarial predictions
* Measurement of attack impact

### 2. AI/ML Pipeline Security

Assess the security of the local model-serving pipeline, including:

* API input validation
* Error handling
* Model loading
* Model integrity
* Docker configuration
* Dependency management
* Logging
* Information disclosure

### 3. Security Mitigation

For identified weaknesses, implement practical mitigations and retest the system to determine whether the attack or vulnerability has been reduced or eliminated.

---

## Target Architecture

The initial target environment consists of:

```text
                 ┌──────────────────────┐
                 │   Attacker / Tester   │
                 │                      │
                 │ Adversarial Inputs   │
                 │ API Requests         │
                 │ Reconnaissance       │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │      FastAPI         │
                 │                      │
                 │   /predict           │
                 │   /health            │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │    PyTorch Model     │
                 │                      │
                 │     CIFAR-10 CNN     │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │    Logs / Metadata   │
                 └──────────────────────┘
```

The complete architecture will be updated as the project develops.

---

## Technology Stack

| Component            | Technology                                     |
| -------------------- | ---------------------------------------------- |
| Programming Language | Python                                         |
| Machine Learning     | PyTorch                                        |
| Dataset              | CIFAR-10                                       |
| API                  | FastAPI                                        |
| Containerization     | Docker                                         |
| Adversarial ML       | Custom implementations / open-source libraries |
| Testing              | Pytest                                         |
| Documentation        | Markdown                                       |
| Security Frameworks  | MITRE ATLAS, NIST AI RMF                       |

---

## Dataset

The project uses the CIFAR-10 dataset.

CIFAR-10 contains 10 image classes:

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

Each image is a `32 × 32` RGB image.

---

## Machine Learning Model

The initial model is a custom convolutional neural network (CNN) implemented using PyTorch.

The current architecture consists of:

```text
Input: 32 × 32 × 3
        │
        ▼
Convolution
        │
        ▼
ReLU
        │
        ▼
Max Pooling
        │
        ▼
Convolution
        │
        ▼
ReLU
        │
        ▼
Max Pooling
        │
        ▼
Flatten
        │
        ▼
Fully Connected Layer
        │
        ▼
10 Class Output
```

The trained model will be saved as:

```text
model/cifar10_cnn.pth
```

---

## Project Structure

```text
ai-security-red-team-assessment/
│
├── model/
│   ├── train.py
│   ├── model.py
│   └── cifar10_cnn.pth
│
├── api/
│   ├── main.py
│   ├── schemas.py
│   └── logging_config.py
│
├── attacks/
│   ├── adversarial_fgsm.py
│   ├── adversarial_pgd.py
│   ├── api_metadata.py
│   └── input_validation.py
│
├── defenses/
│   ├── input_validation.py
│   ├── adversarial_detection.py
│   └── secure_model_loading.py
│
├── tests/
│
├── data/
│
├── results/
│   ├── screenshots/
│   ├── adversarial_examples/
│   └── logs/
│
├── reports/
│   └── attack-report.md
│
├── video/
│   └── walkthrough.md
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── AI_USAGE_LOG.md
└── README.md
```

Some directories will be added as the assessment progresses.

---

## Planned Red-Team Methodology

The assessment will follow a simplified red-team workflow:

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

Each finding will include:

* Description
* Attack objective
* Methodology
* Evidence
* Observed impact
* Risk considerations
* Proposed mitigation
* Retest results

---

## Planned Adversarial ML Attacks

### FGSM

Fast Gradient Sign Method will be used to generate adversarial inputs by applying a small perturbation based on the gradient of the model loss with respect to the input.

The experiment will compare:

```text
Clean Image
     ↓
Prediction
     ↓
Adversarial Perturbation
     ↓
Adversarial Image
     ↓
Prediction
```

### PGD

Projected Gradient Descent will be used as an iterative adversarial attack.

The results will be compared with the FGSM experiment.

Attack results will include measurements such as:

* Original prediction
* Adversarial prediction
* Confidence
* Perturbation magnitude
* Attack success
* Model accuracy where applicable

---

## Pipeline Security Assessment

The Docker-based serving pipeline will be reviewed for weaknesses including:

### API

* Input validation
* File validation
* Request size limits
* Error handling
* Information disclosure
* Rate limiting considerations

### Model

* Model integrity
* Model loading
* Model file validation
* Model metadata exposure

### Docker

* Container privileges
* Exposed ports
* Configuration
* Secrets
* Filesystem permissions
* Dependency exposure

### Logging

* Excessive information
* Sensitive metadata
* Error information
* Request information

---

## Security Mitigations

Potential mitigations will be implemented based on the findings discovered during testing.

Examples include:

* Strict input validation
* Image size and format restrictions
* Controlled error responses
* Model integrity verification
* Reduced metadata exposure
* Secure model loading
* Container hardening
* Dependency pinning
* Appropriate logging controls
* Adversarial robustness techniques where applicable

Mitigations will be tested against the original findings whenever possible.

---

## MITRE ATLAS Mapping

Identified findings will be mapped to relevant MITRE ATLAS techniques where applicable.

The mapping will be documented using:

| Finding | MITRE ATLAS Technique | Evidence | Mitigation |
| ------- | --------------------- | -------- | ---------- |
| TBD     | TBD                   | TBD      | TBD        |

The table will be completed as findings are identified.

---

## NIST AI RMF Mapping

The assessment will also consider the NIST AI Risk Management Framework functions:

```text
GOVERN
MAP
MEASURE
MANAGE
```

Findings and mitigations will be mapped to relevant AI risk-management activities where applicable.

---

## Baseline Results

The baseline model performance will be recorded before adversarial testing.

Initial configuration:

```text
Dataset: CIFAR-10
Model: Custom CNN
Input: 32 × 32 RGB
Optimizer: Adam
Loss: CrossEntropyLoss
Epochs: 10
Batch Size: 64
Learning Rate: 0.001
Device: CPU/GPU depending on availability
```

Baseline accuracy:

```text
TBD
```

Baseline results will be updated after training and evaluation.

---

## Reproducibility

The project is designed to run locally using Python and Docker.

### Python Environment

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Train the Model

```bash
python model/train.py
```

Additional setup and execution instructions will be added as the API and Docker environment are implemented.

---

## Results

Results will be stored under:

```text
results/
```

Expected evidence includes:

* Clean images
* Adversarial images
* Prediction outputs
* Attack comparisons
* API responses
* Security testing screenshots
* Logs
* Mitigation/retest results

---

## Deliverables

The final repository will contain:

* [ ] Attack Report
* [ ] At least two successful adversarial attacks
* [ ] Pipeline security review
* [ ] Security mitigations
* [ ] MITRE ATLAS mapping
* [ ] NIST AI RMF mapping
* [ ] 3–5 minute video walkthrough
* [ ] AI Usage Log
* [ ] Reproducible code and setup instructions

Optional bonus investigations may be added if the core assessment is complete.

---

## AI Usage

AI tools may be used as assistants for:

* Understanding technical concepts
* Reviewing code
* Debugging
* Explaining security concepts
* Improving documentation

All AI assistance will be recorded in:

```text
AI_USAGE_LOG.md
```

The final implementation will be reviewed and understood by the author before submission.

---

## Scope and Rules of Engagement

This project follows a strict local testing scope.

### In Scope

* Locally trained model
* Locally running API
* Locally running Docker containers
* Self-generated datasets and logs
* Security testing of systems created for this assessment

### Out of Scope

* External systems
* Other participants' systems
* Public APIs
* Real personal data
* Unauthorized infrastructure
* Production systems

All security testing is performed against systems owned and controlled for this assessment.

---

## Project Status

Current phase:

```text
Phase 1 — Model Development
```

Current progress:

* [x] Repository created
* [x] Project structure created
* [ ] CIFAR-10 training pipeline
* [ ] Baseline evaluation
* [ ] Prediction API
* [ ] Docker container
* [ ] FGSM attack
* [ ] PGD attack
* [ ] Pipeline reconnaissance
* [ ] Metadata analysis
* [ ] Security mitigations
* [ ] MITRE ATLAS mapping
* [ ] NIST AI RMF mapping
* [ ] Attack report
* [ ] Video walkthrough
* [ ] Final testing

---

## Author

**Individual AI Security Red Team Assessment**

Project developed as part of the Ethiopian Artificial Intelligence 7-day AI Security Red Team Challenge.
