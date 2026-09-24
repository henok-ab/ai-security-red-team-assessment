# API Reconnaissance

## 1. Target

The target is a locally controlled FastAPI service serving a pretrained CIFAR-10 image classification model.

**Base URL:**

`http://127.0.0.1:8000`

**Scope:** All testing was performed against the locally controlled model and API.

---

## 2. Discovered Endpoints

| Method | Endpoint   | Purpose                       |
| ------ | ---------- | ----------------------------- |
| GET    | `/health`  | Service health check          |
| POST   | `/predict` | Image classification          |
| GET    | `/docs`    | Interactive API documentation |

The `/docs` endpoint exposes the available API operations and their input structure.

---

## 3. Test 1 — Missing File

### Request

```text
POST /predict
```

No file was supplied.

### Response

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "file"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

### HTTP Status

```text
422 Unprocessable Entity
```

### Observation

FastAPI correctly validates that the required `file` field is present before the prediction function executes.

### Security Assessment

No vulnerability was identified from this test.

---

## 4. Test 2 — Invalid File

### Request

A plain text file named `test.txt` was uploaded to:

```text
POST /predict
```

### Response

```text
500 Internal Server Error
```

### Server Exception

The backend produced:

```text
PIL.UnidentifiedImageError:
cannot identify image file <_io.BytesIO object at ...>
```

The exception originated from:

```text
api/main.py
image = Image.open(...)
```

### Observation

The application does not catch image parsing exceptions before they propagate to the ASGI error handler.

### Security Impact

Malformed or unsupported uploads can cause an unhandled application exception and produce an HTTP 500 response.

If detailed exceptions were exposed through an inappropriate production configuration, implementation details could potentially be disclosed.

### Assessment

**Confirmed finding: Unhandled invalid-image exception.**

---

## 5. Test 3 — Incorrect MIME Type

### Test

The same text file was uploaded while declaring its MIME type as:

```text
image/jpeg
```

### Result

```text
500 Internal Server Error
```

The backend again produced:

```text
PIL.UnidentifiedImageError
```

### Observation

The application does not blindly trust the declared MIME type. Pillow attempts to parse the actual file contents and rejects the text file.

However, the resulting parsing exception remains unhandled.

### Assessment

The test did **not** demonstrate MIME-type trust.

Instead, it confirmed that invalid file contents can still trigger an unhandled exception.

---

## 6. Test 4 — Large Image

### Test Input

A valid:

```text
2000 × 2000 RGB JPEG
```

was uploaded to:

```text
POST /predict
```

### Response

```json
{
  "predicted_class": "dog",
  "confidence": 0.362
}
```

### Observation

The API successfully processed an image significantly larger than the model's native input size of `32 × 32`.

The preprocessing pipeline contains:

```python
transforms.Resize((32, 32))
```

Therefore, the image is resized before being passed to the CNN.

### Security Consideration

No explicit application-level maximum upload size or image dimension check is currently implemented before image processing.

Large uploads could increase memory or CPU consumption if the service were exposed to untrusted clients at scale.

### Assessment

**Potential availability/resource-consumption weakness identified.**

No denial-of-service testing was performed.

---

## 7. Summary of Findings

| ID   | Test                | Result                | Assessment                                     |
| ---- | ------------------- | --------------------- | ---------------------------------------------- |
| R-01 | Missing file        | 422                   | Correct validation                             |
| R-02 | Invalid file        | 500                   | Confirmed unhandled exception                  |
| R-03 | Incorrect MIME type | 500                   | Content is parsed; exception remains unhandled |
| R-04 | 2000×2000 image     | Successful prediction | Potential resource-consumption weakness        |

---

## 8. Current Attack Surface

The current service exposes:

```text
                    FastAPI Service
                          │
          ┌───────────────┼───────────────┐
          │               │               │
       /health         /predict          /docs
                          │
                     File Upload
                          │
                  ┌───────┴────────┐
                  │                │
             File parsing      Preprocessing
                  │                │
              Pillow          Resize 32×32
                                   │
                                   ↓
                              SimpleCNN
                                   │
                                   ↓
                              Prediction
```

The `/predict` endpoint is the primary attack surface for subsequent adversarial ML testing.

---

## 9. Recommended Pipeline Improvements

Based on the reconnaissance performed so far:

1. Validate uploaded file type and image content.
2. Catch image parsing exceptions and return controlled 4xx responses.
3. Enforce maximum upload size.
4. Enforce maximum image dimensions before expensive processing.
5. Configure production error handling so stack traces are not exposed to clients.
6. Consider rate limiting for publicly exposed prediction endpoints.
7. Continue testing model-specific and adversarial-input behavior.

---

## 10. Next Phase

The next phase is **ML reconnaissance and adversarial testing**.

The first planned attack is the **Fast Gradient Sign Method (FGSM)** against a known CIFAR-10 test image.

The objective is to compare:

```text
Clean image
    ↓
Correct prediction

        versus

Adversarial image
    ↓
Incorrect prediction
```

A successful attack will be saved as evidence for the final red-team assessment.
