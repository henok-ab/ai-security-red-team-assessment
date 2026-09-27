\# AI Security Red Team Attack Report



\## 1. Executive Summary



This assessment simulated a red-team operation against a locally deployed CIFAR-10 image-classification AI system.



The target consisted of a pre-trained PyTorch convolutional neural network exposed through a FastAPI inference service.



The assessment examined both:



1\. \*\*Model-level security and robustness\*\*

2\. \*\*AI serving-pipeline security\*\*



The main model-level attack used the Fast Gradient Sign Method (FGSM) to create adversarial images that caused the model to produce incorrect predictions.



Two successful end-to-end attacks were demonstrated:



| Attack    | Clean prediction | Adversarial prediction | Epsilon | API result              |

| --------- | ---------------- | ---------------------- | ------: | ----------------------- |

| Example 1 | Cat              | Frog                   |    0.03 | Frog, 65.78% confidence |

| Example 2 | Frog             | Deer                   |    0.03 | Deer, 95.26% confidence |



The attacks successfully passed through the FastAPI `/predict` endpoint, demonstrating that the vulnerability existed not only in an offline model test but also through the serving pipeline.



A larger evaluation was also performed. Using the same methodology for comparing the original and defended models, the original model had a \*\*68.01% FGSM attack success rate\*\* at epsilon 0.03 among images that were initially classified correctly.



An adversarial-training defense was then implemented. The defended model reduced the measured FGSM attack success rate to \*\*43.07%\*\*.



The serving pipeline also contained input-validation weaknesses. Invalid image content originally resulted in HTTP 500 errors, while oversized images were accepted for inference. API hardening changed these behaviors to controlled HTTP 400 and HTTP 413 responses.



The assessment therefore demonstrated both successful attacks and corresponding mitigation experiments.



\---



\# 2. Target System



\## 2.1 AI Model



The target was the pre-trained:



`manasyesuarthana/cifar10-simple-cnn-pytorch`



The model performs CIFAR-10 image classification.



The reconstructed architecture contains:



```text

Input

&#x20; ↓

Conv1: 3 → 32

&#x20; ↓

Conv2: 32 → 64

&#x20; ↓

Conv3: 64 → 128

&#x20; ↓

FC1: 2048 → 512

&#x20; ↓

FC2: 512 → 10

&#x20; ↓

CIFAR-10 class prediction

```



The ten output classes are:



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



\## 2.2 Serving Pipeline



The model was exposed through a FastAPI service.



Main endpoints:



```text

GET  /health

POST /predict

GET  /docs

GET  /openapi.json

```



The `/predict` endpoint accepts an uploaded image and returns:



```json

{

&#x20; "predicted\_class": "frog",

&#x20; "confidence": 0.6578

}

```



The target was operated locally during the assessment.



\---



\# 3. Threat Model



The red-team attacker was assumed to have access to the model's prediction interface.



The assessment considered an attacker capable of:



\* Sending images to the inference endpoint.

\* Observing model predictions and confidence values.

\* Crafting adversarial images.

\* Sending malformed files.

\* Sending unusually large images.

\* Inspecting publicly exposed API documentation.

\* Repeatedly testing the endpoint.



The assessment was conducted against a locally controlled system.



No external production system or third-party service was attacked.



\---



\# 4. Reconnaissance



The first stage examined the exposed serving interface before attempting model attacks.



\## 4.1 Health Endpoint



Request:



```text

GET /health

```



Response:



```json

{

&#x20; "status": "healthy"

}

```



The endpoint confirmed that the inference service was active.



The response also exposed the server software through the HTTP response headers.



This was recorded as a minor information-disclosure/hardening observation rather than a standalone critical vulnerability.



\---



\## 4.2 OpenAPI Documentation



The following resources were accessible:



```text

/docs

/openapi.json

```



The OpenAPI specification revealed:



\* Available endpoints.

\* HTTP methods.

\* `/predict` request structure.

\* File-upload parameter.

\* API metadata.



This provides useful information to an attacker performing reconnaissance.



The OpenAPI specification was saved as:



```text

results/openapi.json

```



\---



\# 5. API Input Validation Testing



\## 5.1 Invalid Image Content



A plain-text file was submitted to `/predict` while using an image filename.



Example:



```text

fake\_image.jpg

```



The original application attempted to decode the content as an image.



\### Original result



```text

HTTP 500 Internal Server Error

```



The server logs showed an image-decoding exception.



The traceback was not returned directly to the client, but the application nevertheless produced an uncontrolled server error.



\### Security impact



Repeated malformed requests could cause unnecessary exception handling and processing overhead.



This was not treated as a confirmed denial-of-service vulnerability because a resource-exhaustion threshold was not established.



\### Mitigation



Image decoding was placed inside controlled exception handling.



Invalid image content now produces:



```text

HTTP 400 Bad Request

```



with:



```json

{

&#x20; "detail": "Invalid image file."

}

```



\---



\# 6. Oversized Image Testing



A 2000×2000 image was submitted to the original endpoint.



\### Original result



The API accepted the image and performed inference.



This demonstrated that the application did not initially enforce an image-dimension limit.



\### Security concern



Large inputs can consume additional memory and processing resources.



The test therefore identified a missing input constraint in the serving layer.



\### Mitigation



The API was updated with:



```text

Maximum file size: 5 MB

Maximum width: 1024 pixels

Maximum height: 1024 pixels

```



The same 2000×2000 test image subsequently produced:



```text

HTTP 413 Request Entity Too Large

```



with:



```json

{

&#x20; "detail": "Image dimensions are too large."

}

```



\---



\# 7. FGSM Adversarial Attack



\## 7.1 Attack Objective



The objective was to determine whether a small, intentionally crafted modification to an image could cause the model to misclassify it.



FGSM was selected because it is simple, reproducible, and suitable for demonstrating adversarial-example behavior against a small image classifier.



The attack uses the gradient of the loss with respect to the input image.



Conceptually:



```text

Original image

&#x20;     ↓

Model prediction

&#x20;     ↓

Calculate loss

&#x20;     ↓

Calculate input gradient

&#x20;     ↓

Apply perturbation

&#x20;     ↓

Adversarial image

&#x20;     ↓

Model prediction

```



The perturbation was generated using epsilon:



```text

ε = 0.03

```



\---



\# 8. Successful Attack #1 — Cat to Frog



The first demonstrated attack used CIFAR-10 test image index 0.



\### Clean input



```text

True class:       cat

Clean prediction: cat

```



An FGSM perturbation with epsilon 0.03 was applied.



\### Adversarial result



```text

True class:          cat

Adversarial class:   frog

Attack successful:   True

```



The resulting image was saved as:



```text

results/adversarial/fgsm\_cat\_to\_frog.png

```



The clean image was saved as:



```text

results/adversarial/clean\_cat.png

```



\---



\# 9. End-to-End API Attack #1



The adversarial image was then submitted to the actual FastAPI endpoint.



Request:



```text

POST /predict

```



Result:



```json

{

&#x20; "predicted\_class": "frog",

&#x20; "confidence": 0.6578

}

```



The model therefore returned:



```text

Expected: cat

Returned: frog

Confidence: 65.78%

```



This demonstrated that the adversarial input remained effective after passing through the serving pipeline.



\---



\# 10. Successful Attack #2 — Frog to Deer



A second independent adversarial example was generated using CIFAR-10 test image index 4.



\### Clean input



```text

True class:       frog

Clean prediction: frog

```



FGSM was applied with:



```text

ε = 0.03

```



\### Adversarial result



```text

True class:          frog

Adversarial class:   deer

Attack successful:   True

```



Evidence files:



```text

results/adversarial/clean\_frog.png

results/adversarial/fgsm\_frog\_to\_deer.png

```



\---



\# 11. End-to-End API Attack #2



The second adversarial image was submitted to `/predict`.



The API returned:



```json

{

&#x20; "predicted\_class": "deer",

&#x20; "confidence": 0.9526

}

```



Therefore:



```text

Expected: frog

Returned: deer

Confidence: 95.26%

```



The confidence value describes the model's confidence in its returned class; it does not mean that the attack itself had a 95.26% success probability.



\---



\# 12. FGSM Quantitative Evaluation



The attack was evaluated across the CIFAR-10 test set using multiple epsilon values.



Results from the large FGSM evaluation were:



| Epsilon | Accuracy | Attack Success Rate |

| ------: | -------: | ------------------: |

|    0.00 |  100.00% |               0.00% |

|    0.01 |   74.03% |              25.97% |

|    0.03 |   39.85% |              60.15% |

|    0.05 |   22.89% |              77.11% |

|    0.10 |    7.66% |              92.34% |



The attack success rate was calculated according to the experiment's conditional methodology.



It measures successful attacks among samples that were initially correctly classified.



The results show that increasing perturbation strength increased the observed FGSM attack success rate.



\---



\# 13. Model Robustness Mitigation



\## 13.1 Defense



Adversarial training was selected as the model-level mitigation.



The original model was fine-tuned using adversarial examples generated during training.



Configuration:



```text

Epsilon:       0.03

Epochs:        1

Batch size:    64

Learning rate: 0.0001

Optimizer:     Adam

Loss:          Cross Entropy

```



The resulting model was saved as:



```text

model/weights/defended\_model.pth

```



\---



\# 14. Defense Evaluation



The original and defended models were evaluated using the same FGSM evaluation methodology.



\### Clean accuracy



| Model    | Clean accuracy |

| -------- | -------------: |

| Original |         61.14% |

| Defended |         69.53% |



The defended model improved measured clean accuracy by 8.39 percentage points in this experiment.



\### FGSM robustness



| Model    | Initially correct | Successful attacks | FGSM ASR |

| -------- | ----------------: | -----------------: | -------: |

| Original |             6,114 |              4,158 |   68.01% |

| Defended |             6,953 |              2,995 |   43.07% |



The measured FGSM ASR decreased:



```text

68.01% → 43.07%

```



This represents a reduction of:



```text

24.94 percentage points

```



The defense therefore reduced susceptibility to the tested FGSM attack but did not eliminate adversarial vulnerability.



\---



\# 15. API Security Mitigation



The serving pipeline was hardened independently from the model.



Implemented controls included:



```text

Input content validation

&#x20;       ↓

Invalid image → HTTP 400



File-size restriction

&#x20;       ↓

Files > 5 MB → HTTP 413



Image-dimension restriction

&#x20;       ↓

Images > 1024×1024 → HTTP 413



Controlled exception handling

&#x20;       ↓

Image decoding failures do not become HTTP 500

```



The valid adversarial image was retested after these changes.



The model still returned:



```json

{

&#x20; "predicted\_class": "deer",

&#x20; "confidence": 0.9526

}

```



This is important because the API hardening was designed to address malformed and oversized inputs; it was not expected to eliminate model-level adversarial examples.



\---



\# 16. MITRE ATLAS Mapping



The adversarial-image portion of the assessment maps directly to MITRE ATLAS techniques concerning adversarial data and model evasion.



\## AML.T0043 — Craft Adversarial Data



The FGSM process created modified input data specifically intended to produce an incorrect model result.



The two generated examples were:



```text

Cat → Frog

Frog → Deer

```



MITRE describes Craft Adversarial Data as modifying inputs to cause a desired effect such as misclassification.



\## AML.T0015 — Evade AI Model



The adversarial examples were used to cause the deployed classifier to incorrectly identify the image.



This corresponds to MITRE's Evade AI Model technique, which describes adversarial inputs that prevent an AI model from correctly identifying input content.



\## Verification of the Attack



The adversarial images were submitted to the actual `/predict` inference endpoint after being generated.



This provided live verification that the crafted examples remained effective through the target serving pipeline.



MITRE ATLAS includes Verify Attack as a technique associated with confirming that an attack works against the target model.



\---



\# 17. NIST AI RMF Mapping



The assessment also follows the NIST AI RMF approach.



NIST AI RMF 1.0 organizes AI risk-management activities into:



```text

GOVERN

MAP

MEASURE

MANAGE

```



NIST describes the framework as a continuous risk-management approach rather than a rigid sequence.



\### MAP



The assessment documented:



\* Model architecture.

\* Input and output behavior.

\* API endpoints.

\* Threat assumptions.

\* Attack surface.

\* Model and serving-pipeline limitations.



\### MEASURE



The assessment measured:



\* Clean accuracy.

\* FGSM attack success.

\* FGSM behavior at multiple epsilon values.

\* API behavior for malformed inputs.

\* API behavior for oversized images.

\* Original-versus-defended model performance.



NIST specifically recommends security testing, red-team exercises, metrics, and documentation of results within the MEASURE function.



\### MANAGE



The identified risks were followed by mitigation:



```text

Model vulnerability

&#x20;       ↓

Adversarial training



Malformed input vulnerability

&#x20;       ↓

Image validation and exception handling



Oversized input vulnerability

&#x20;       ↓

Size and dimension limits

```



NIST's MANAGE function covers responding to and documenting risks identified through assessment activities.



\### GOVERN



The project maintained:



\* AI usage documentation.

\* Attack evidence.

\* Reproducible scripts.

\* Mitigation documentation.

\* Git history.

\* Documented limitations.



These artifacts support accountability and traceability throughout the assessment.



\---



\# 18. Findings Summary



| ID   | Finding                                        | Evidence                                | Mitigation                                 |

| ---- | ---------------------------------------------- | --------------------------------------- | ------------------------------------------ |

| F-01 | Adversarial-example vulnerability              | Cat → Frog                              | Adversarial training                       |

| F-02 | Adversarial-example vulnerability              | Frog → Deer                             | Adversarial training                       |

| F-03 | High FGSM attack success                       | 68.01% ASR                              | Adversarial training reduced ASR to 43.07% |

| F-04 | Invalid image causes uncontrolled server error | HTTP 500                                | Content validation + exception handling    |

| F-05 | Oversized images accepted                      | 2000×2000 image processed               | Dimension limit                            |

| F-06 | API information exposure                       | `/docs`, `/openapi.json`, server header | Documented as hardening consideration      |



\---



\# 19. Limitations



The assessment has several important limitations.



\### Model limitations



The robustness experiment used:



\* One CIFAR-10 model.

\* One primary attack method: FGSM.

\* One main defense configuration.

\* One epsilon value for the mitigation comparison.

\* One training epoch for adversarial training.



The results therefore should not be interpreted as proof of robustness against all adversarial attacks.



Additional testing could include:



\* PGD.

\* Black-box attacks.

\* Different epsilon values.

\* Transfer attacks.

\* Other adversarial defenses.

\* Longer adversarial-training schedules.



\### API limitations



The malformed-input testing demonstrated controlled error handling but did not establish a denial-of-service threshold.



No claim is made that the original API could definitely be taken down through resource exhaustion.



\### Deployment limitations



The assessment was performed against a locally controlled FastAPI service.



The results should therefore be interpreted as a security assessment of the constructed target environment, not as a claim about production systems.



\---



\# 20. Final Security Assessment



The red-team assessment demonstrated that the target AI system had vulnerabilities at both the \*\*model\*\* and \*\*serving-pipeline\*\* levels.



At the model level, FGSM successfully generated adversarial images that caused incorrect predictions. Two examples were verified through the actual inference API.



At the serving-pipeline level, malformed image content produced uncontrolled HTTP 500 responses and oversized images were initially accepted without dimension restrictions.



Mitigations were then implemented and tested.



Adversarial training reduced the measured FGSM attack success rate from:



```text

68.01% → 43.07%

```



while API hardening changed malformed-input behavior from:



```text

HTTP 500 → HTTP 400

```



and oversized-image behavior from successful inference to:



```text

HTTP 413

```



The assessment therefore demonstrates an iterative red-team process:



```text

Reconnaissance

&#x20;     ↓

Attack

&#x20;     ↓

Measure

&#x20;     ↓

Identify vulnerabilities

&#x20;     ↓

Implement mitigations

&#x20;     ↓

Retest

&#x20;     ↓

Document residual risk

```



The most important remaining finding is that adversarial training reduced but did not eliminate the model's susceptibility to FGSM. Further robustness testing would be required before making broader security or robustness claims.



