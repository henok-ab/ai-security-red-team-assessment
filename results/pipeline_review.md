# AI Serving Pipeline Security Review

## 1. Overview

The target AI system consists of a pre-trained CIFAR-10 image-classification model exposed through a FastAPI inference service.

The pipeline accepts an uploaded image, validates and preprocesses the input, passes it to the PyTorch model, and returns a predicted class and confidence value.

The assessment reviewed the pipeline from an attacker's perspective, focusing on:

* API exposure
* Input validation
* File handling
* Resource limits
* Error handling
* Model inference
* Information disclosure
* Adversarial input handling

---

## 2. Pipeline Architecture

```text
                 Attacker / Client
                       │
                       ▼
                FastAPI Server
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
     /health        /docs        /openapi.json
                       │
                       ▼
                   /predict
                       │
                       ▼
                 File Upload
                       │
                       ▼
              Input Validation
                       │
                       ▼
              Image Decoding
                       │
                       ▼
              Preprocessing
                       │
                       ▼
                PyTorch CNN
                       │
                       ▼
             Prediction + Confidence
                       │
                       ▼
                    Client
```

---

# 3. Component Review

## 3.1 FastAPI Server

The model is exposed through a FastAPI application running locally.

The main prediction endpoint is:

```text
POST /predict
```

The endpoint accepts an uploaded file.

### Security observation

The API provides a simple and accessible interface to the model, but the original implementation relied heavily on the image decoder to determine whether uploaded content was valid.

This created uncontrolled behavior when invalid content was submitted.

### Mitigation

The API was updated to explicitly handle invalid image content and return a controlled HTTP response.

---

# 4. Endpoint Exposure

The following endpoints were discovered during reconnaissance:

| Endpoint        | Purpose                       | Security observation                 |
| --------------- | ----------------------------- | ------------------------------------ |
| `/health`       | Service health                | Reveals service availability         |
| `/predict`      | Model inference               | Main attack surface                  |
| `/docs`         | Interactive API documentation | Exposes API structure                |
| `/openapi.json` | API specification             | Exposes endpoint and request details |

The `/predict` endpoint represents the primary attack surface because attacker-controlled data reaches the model.

---

# 5. Input Validation

## 5.1 Original Behavior

The original prediction pipeline effectively performed:

```text
Uploaded bytes
      ↓
Image.open()
      ↓
RGB conversion
      ↓
Preprocessing
      ↓
Model inference
```

There was no explicit controlled exception handling around image decoding.

When a non-image file was submitted, the server returned:

```text
HTTP 500 Internal Server Error
```

This indicated that malformed input could trigger an application-level exception.

---

## 5.2 Hardened Behavior

The updated pipeline performs validation before inference:

```text
Uploaded bytes
      ↓
Check file size
      ↓
Decode and verify image
      ↓
Check dimensions
      ↓
Convert to RGB
      ↓
Preprocess
      ↓
Model inference
```

Invalid image content now produces:

```text
HTTP 400 Bad Request
```

Oversized images produce:

```text
HTTP 413 Request Entity Too Large
```

This separates invalid client input from unexpected server failures.

---

# 6. File-Size Protection

The hardened API includes:

```text
MAX_FILE_SIZE = 5 MB
```

The purpose is to prevent unnecessarily large uploaded files from reaching the image-processing stage.

If the upload exceeds the configured limit, the request is rejected before inference.

This provides a basic resource-consumption control.

---

# 7. Image-Dimension Protection

The hardened API also limits image dimensions:

```text
Maximum width:  1024 pixels
Maximum height: 1024 pixels
```

During reconnaissance, a 2000×2000 image was accepted by the original API and passed to inference.

After the mitigation was implemented, the same class of oversized input produced:

```text
HTTP 413 Request Entity Too Large
```

This demonstrates successful mitigation of the tested oversized-input condition.

---

# 8. Error Handling

## Original

Invalid image content:

```text
HTTP 500
```

The server logs contained an image-decoding exception.

Although the traceback was not returned to the external client, returning HTTP 500 for attacker-controlled invalid input indicates that expected input-validation failures were not handled explicitly.

## Mitigated

Invalid image content:

```text
HTTP 400
{
    "detail": "Invalid image file."
}
```

This provides a controlled response without exposing internal exception details to the client.

---

# 9. Adversarial Input Handling

An important distinction exists between **API validation** and **model robustness**.

The API hardening controls protect the serving infrastructure from malformed and oversized inputs.

They do not determine whether a valid image is adversarial.

For example, the adversarial frog-to-deer image remained a valid image after the API hardening changes.

The API returned:

```json
{
  "predicted_class": "deer",
  "confidence": 0.9526
}
```

Therefore:

```text
API validation
     ≠
Model adversarial robustness
```

Both layers require separate security controls.

---

# 10. Model Layer

The model receives validated image data and performs classification.

The model-level red-team test demonstrated that valid adversarial images can cause incorrect predictions.

Example:

```text
Clean image:
frog

Adversarial image:
deer
```

This means that even when the API correctly validates the file as an image, the input may still be malicious from the model's perspective.

The implemented model-level mitigation was adversarial training.

---

# 11. Information Exposure

The following resources were accessible during testing:

```text
/docs
/openapi.json
```

The OpenAPI document provides information about the API structure and request format.

The HTTP response also identified the server software through the `Server` header.

These observations are considered information-disclosure/hardening concerns.

They were not treated as standalone critical vulnerabilities because the assessment did not demonstrate direct compromise resulting from this information.

### Potential production hardening

Depending on deployment requirements:

* Restrict interactive API documentation.
* Avoid exposing unnecessary API metadata.
* Minimize server-identification headers.
* Place the API behind an appropriate gateway or reverse proxy.
* Require authentication for sensitive endpoints.

---

# 12. Security Controls Before and After Mitigation

| Control                             | Original       | Hardened                              |
| ----------------------------------- | -------------- | ------------------------------------- |
| Image decoding error handling       | Missing        | Implemented                           |
| Invalid-image rejection             | HTTP 500       | HTTP 400                              |
| File-size limit                     | Not enforced   | 5 MB                                  |
| Dimension limit                     | Not enforced   | 1024×1024                             |
| Controlled oversized-input response | No             | HTTP 413                              |
| Adversarial robustness defense      | Original model | Adversarially trained model           |
| API documentation exposure          | Present        | Documented as hardening consideration |

---

# 13. Pipeline Security Findings

### Finding P-01 — Uncontrolled malformed-image errors

**Severity:** Low/Medium

**Evidence:**

Invalid image content produced HTTP 500.

**Impact:**

Malformed requests can trigger application exceptions and consume processing resources.

**Mitigation:**

Image decoding exceptions are caught and converted into HTTP 400 responses.

---

### Finding P-02 — Missing image-dimension restrictions

**Severity:** Medium

**Evidence:**

A 2000×2000 image was accepted by the original API.

**Impact:**

Large image processing can increase memory and CPU consumption.

**Mitigation:**

Images larger than 1024×1024 are rejected with HTTP 413.

---

### Finding P-03 — API information exposure

**Severity:** Low

**Evidence:**

The `/docs` and `/openapi.json` resources were accessible, and the HTTP response exposed the server software.

**Impact:**

Provides attackers with additional information about the API implementation and attack surface.

**Mitigation recommendation:**

Restrict API documentation and minimize unnecessary implementation information in production deployments.

---

### Finding P-04 — Model remains vulnerable to valid adversarial images

**Severity:** High within the tested model-security scope

**Evidence:**

FGSM generated successful adversarial examples that were accepted by the API.

Example:

```text
Frog → Deer
95.26% returned confidence
```

**Impact:**

An attacker capable of crafting adversarial inputs can cause incorrect model predictions.

**Mitigation:**

Adversarial training reduced measured FGSM ASR:

```text
68.01% → 43.07%
```

However, residual vulnerability remained.

---

# 14. Defense-in-Depth Architecture

The assessment suggests treating the AI system as multiple security layers:

```text
                 External Client
                       │
                       ▼
             ┌───────────────────┐
             │ API Security      │
             │                  │
             │ Size limits       │
             │ Content validation│
             │ Rate limiting*    │
             │ Authentication*   │
             └─────────┬─────────┘
                       │
                       ▼
             ┌───────────────────┐
             │ Input Processing  │
             │                  │
             │ Decode image      │
             │ Dimension checks  │
             │ Preprocessing     │
             └─────────┬─────────┘
                       │
                       ▼
             ┌───────────────────┐
             │ Model Security    │
             │                  │
             │ Robust training   │
             │ Adversarial tests │
             │ Monitoring*       │
             └─────────┬─────────┘
                       │
                       ▼
                  Prediction
```

`*` indicates controls recommended for a production deployment but not implemented as part of this assessment.

---

# 15. Pipeline Security Conclusion

The assessment demonstrated that securing an AI application requires more than protecting the neural-network weights.

The original system had weaknesses at multiple layers:

```text
API layer
   ↓
Malformed-input handling

Resource layer
   ↓
Missing size/dimension restrictions

Information layer
   ↓
API documentation/server information

Model layer
   ↓
Adversarial-example vulnerability
```

The implemented mitigations improved both the serving pipeline and model robustness.

However, the remaining FGSM vulnerability demonstrates that API hardening alone cannot provide model security.

A production AI system should therefore use defense in depth across:

* API security
* Input validation
* Resource controls
* Model robustness
* Monitoring
* Authentication and authorization
* Rate limiting
* Security testing
