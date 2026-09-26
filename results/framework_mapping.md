\# MITRE ATLAS and NIST AI RMF Framework Mapping



\## 1. Purpose



This document maps the findings and mitigation activities from the AI Security Red Team Assessment to the MITRE ATLAS adversarial machine learning knowledge base and the NIST AI Risk Management Framework (AI RMF).



The assessment focused on two main areas:



1\. Model-level robustness against adversarial examples.

2\. Security and robustness of the model-serving API.



\---



\## 2. MITRE ATLAS Mapping



\### 2.1 Adversarial Example / Model Evasion



The primary model-level attack was a Fast Gradient Sign Method (FGSM) adversarial-example attack.



The attacker started with a valid CIFAR-10 image and calculated a small perturbation based on the model's input gradient. The resulting image remained visually similar to the original input but caused an incorrect model prediction.



Two successful examples were demonstrated:



| Clean class | Adversarial class | Epsilon | Result     |

| ----------- | ----------------- | ------: | ---------- |

| Cat         | Frog              |    0.03 | Successful |

| Frog        | Deer              |    0.03 | Successful |



The attacks were also tested through the actual FastAPI `/predict` endpoint.



The API returned:



\* Cat → Frog with 65.78% confidence.

\* Frog → Deer with 95.26% confidence.



This demonstrates that the adversarial examples were not limited to an offline model test; they successfully passed through the serving pipeline and caused incorrect predictions.



\### 2.2 Large-Scale Evasion Evaluation



FGSM was evaluated across the CIFAR-10 test set at multiple perturbation strengths.



The attack-success rate increased as epsilon increased.



The mitigation comparison used the same evaluation methodology for both models:



| Model    | Initially correct | Successful FGSM attacks | FGSM ASR |

| -------- | ----------------: | ----------------------: | -------: |

| Original |             6,114 |                   4,158 |   68.01% |

| Defended |             6,953 |                   2,995 |   43.07% |



ASR was calculated only among images that were initially classified correctly.



The results demonstrate that adversarial training reduced the measured attack success rate but did not eliminate the vulnerability.



\### 2.3 Reconnaissance and Serving-Pipeline Testing



The red-team assessment also examined the exposed API surface.



The following endpoints were identified:



\* `/health`

\* `/predict`

\* `/docs`

\* `/openapi.json`



The OpenAPI specification revealed the available API paths and the expected upload interface.



The API also exposed a server fingerprint through the HTTP response headers.



These observations were recorded as reconnaissance and information-disclosure findings rather than being treated as direct model vulnerabilities.



\### 2.4 Malformed Input Testing



A non-image file was submitted to the `/predict` endpoint while using an image filename.



Before mitigation, the API attempted to decode the file and returned:



```text

HTTP 500 Internal Server Error

```



The server-side logs showed an image-decoding exception.



The vulnerability was mitigated by validating the uploaded content and returning a controlled client error:



```text

HTTP 400 Bad Request

{"detail":"Invalid image file."}

```



The assessment therefore demonstrated both exploitation of the original behavior and validation of the mitigation.



\---



\## 3. NIST AI RMF Mapping



The assessment maps to the four functions of the NIST AI RMF: Govern, Map, Measure, and Manage.



\### 3.1 GOVERN



The project established documentation and accountability mechanisms for the assessment.



Evidence includes:



\* `AI\_USAGE\_LOG.md`

\* reconnaissance documentation

\* attack evidence

\* mitigation documentation

\* reproducible Python scripts

\* Git commit history

\* documented experiment limitations



These artifacts provide a record of how the AI system was assessed, what risks were identified, what mitigations were implemented, and how the results were produced.



\### 3.2 MAP



The target system and its operating context were documented.



The target consists of:



\* A CIFAR-10 image-classification model.

\* A PyTorch model implementation.

\* A FastAPI serving layer.

\* A `/predict` endpoint accepting uploaded images.

\* A `/health` endpoint.

\* OpenAPI documentation.



The assessment identified two primary risk areas:



1\. Adversarial manipulation of model inputs.

2\. Unsafe or insufficiently constrained API inputs.



The model's assumptions and limitations were also considered when interpreting the experimental results.



\### 3.3 MEASURE



The assessment performed quantitative security and robustness measurements.



Measurements included:



\* Clean model accuracy.

\* FGSM attack success rate.

\* Attack performance at multiple epsilon values.

\* Successful adversarial examples.

\* API response codes for malformed input.

\* API response behavior for oversized images.

\* Comparison of original and defended model performance.



The model-level mitigation experiment produced the following results:



| Metric         | Original | Defended |

| -------------- | -------: | -------: |

| Clean accuracy |   61.14% |   69.53% |

| FGSM ASR       |   68.01% |   43.07% |



The FGSM attack success rate decreased by 24.94 percentage points in this experiment.



The result should not be interpreted as proving that the model is robust against all adversarial attacks. The experiment used one defense configuration and FGSM at epsilon 0.03.



\### 3.4 MANAGE



The identified risks were followed by concrete mitigation experiments.



\#### Model-level mitigation



Adversarial training was applied to create:



```text

model/weights/defended\_model.pth

```



The defended model was evaluated using the same FGSM methodology as the original model.



The measured FGSM ASR decreased from 68.01% to 43.07%.



This indicates an improvement under the tested attack configuration while demonstrating that residual vulnerability remained.



\#### API-level mitigation



The serving pipeline was hardened with:



\* Maximum upload size of 5 MB.

\* Maximum image dimensions of 1024×1024.

\* Image-content validation.

\* Controlled error handling for invalid image files.



Observed behavior changed from:



```text

Invalid image:

500 Internal Server Error

```



to:



```text

400 Bad Request

Invalid image file.

```



and:



```text

Oversized image:

413 Request Entity Too Large

```



The valid adversarial image was retested after the API changes and continued to reach the model, confirming that the validation changes did not simply disable the prediction endpoint.



\---



\## 4. Risk-to-Mitigation Summary



| Finding                            | Evidence                                 | Mitigation                              | Validation                    |

| ---------------------------------- | ---------------------------------------- | --------------------------------------- | ----------------------------- |

| FGSM model evasion                 | Cat → Frog; Frog → Deer                  | Adversarial training                    | ASR decreased 68.01% → 43.07% |

| Malformed image handling           | Invalid file caused HTTP 500             | Image validation and exception handling | HTTP 400                      |

| Oversized image acceptance         | 2000×2000 image accepted                 | Dimension limit                         | HTTP 413                      |

| API information exposure           | `/docs`, `/openapi.json`, server header  | Documented as hardening consideration   | Recon evidence retained       |

| Residual adversarial vulnerability | Defended model still had 43.07% FGSM ASR | Further robustness testing required     | Limitation documented         |



\---



\## 5. Framework-Based Conclusion



The assessment followed an iterative risk-management process:



```text

MAP

&#x20; ↓

Identify target, context and attack surface

&#x20; ↓

MEASURE

&#x20; ↓

Perform reconnaissance, FGSM attacks and API tests

&#x20; ↓

MANAGE

&#x20; ↓

Implement adversarial training and API hardening

&#x20; ↓

MEASURE AGAIN

&#x20; ↓

Compare original and defended behavior

&#x20; ↓

DOCUMENT

&#x20; ↓

Record results, limitations and AI usage

```



The assessment therefore demonstrates practical application of AI security testing rather than only theoretical discussion of AI risk frameworks.



The principal remaining model-level limitation is that adversarial training reduced but did not eliminate FGSM vulnerability. Additional evaluation against different attack methods, perturbation strengths, and threat models would be required before making broader robustness claims.



