# Model Robustness Mitigation Experiment



## 1. Objective



The objective of this experiment was to determine whether adversarial training could improve the CIFAR-10 model's robustness against FGSM (Fast Gradient Sign Method) adversarial attacks.



The original model was previously demonstrated to be vulnerable to FGSM attacks at epsilon (ε) = 0.03.



A copy of the pretrained model was fine-tuned using adversarial examples, producing a separate defended model.



The original model weights were not modified.



---



## 2. Defense Method



The defense used adversarial training.



During training, FGSM adversarial examples were generated from CIFAR-10 training images using:



```text

Epsilon: 0.03

Epochs: 1

Batch size: 64

Learning rate: 0.0001

Optimizer: Adam

Loss: Cross-Entropy Loss

```



The resulting model was saved separately as:



```text

model/weights/defended\_model.pth

```



The original pretrained model remains:



```text

model/weights/pytorch\_model.bin

```



---



## 3. Evaluation Method



The original and defended models were evaluated using the same CIFAR-10 test dataset and preprocessing.



Two measurements were collected:



1. Clean accuracy

2. FGSM attack success rate at ε = 0.03



For the FGSM evaluation, only images that were initially classified correctly were included in the attack-success calculation.



Attack Success Rate (ASR) was calculated as:



```text

ASR = successful adversarial attacks / initially correctly classified images × 100

```



This provides a controlled comparison between the original and defended models.



---



## 4. Clean Accuracy Results



| Model    | Correct Predictions | Test Images | Clean Accuracy |

| -------- | ------------------: | ----------: | -------------: |

| Original |                6114 |       10000 |         61.14% |

| Defended |                6953 |       10000 |         69.53% |



The defended model achieved 69.53% clean accuracy compared with 61.14% for the original model.



This represents an observed increase of 8.39 percentage points under this experiment.



---



## 5. FGSM Robustness Results



The models were attacked using FGSM with ε = 0.03.



| Model    | Initially Correct | Successful Attacks | FGSM ASR |

| -------- | ----------------: | -----------------: | -------: |

| Original |              6114 |               4158 |   68.01% |

| Defended |              6953 |               2995 |   43.07% |



The measured attack success rate decreased from 68.01% to 43.07%.



This is a reduction of 24.94 percentage points.



---



## 6. Interpretation



Under the tested configuration, adversarial training improved the model's measured robustness against FGSM.



The attack success rate decreased from:



```text

68.01% → 43.07%

```



At the same time, clean accuracy increased from:



```text

61.14% → 69.53%

```



Therefore, in this experiment, the defended model showed both improved clean accuracy and reduced FGSM attack success.



However, the defense did not eliminate the vulnerability.



An FGSM attack success rate of 43.07% means that a substantial number of initially correctly classified images were still changed to incorrect predictions.



The result should therefore be interpreted as evidence that adversarial training improved robustness under the tested conditions, rather than as proof that the model is fully robust against adversarial attacks.



---



## 7. Limitations



This experiment has several limitations:



* Only one adversarial training epoch was used.

* The defense was evaluated primarily against FGSM.

* The attack strength tested for the comparison was ε = 0.03.

* The experiment used the CIFAR-10 test dataset.

* Only initially correctly classified images were included in the ASR calculation.

* The experiment did not evaluate other attacks such as PGD, C\&W, or black-box attacks.

* The results may change with different training configurations, random seeds, preprocessing, or datasets.

* The increase in clean accuracy should not be assumed to occur for every adversarial-training configuration.



Further testing with multiple attack methods and different perturbation strengths would provide a stronger assessment of robustness.



---



## 8. Reproducibility



The experiment can be reproduced using:



```text

python model/adversarial\_training.py

python model/test\_defense.py

python model/clean\_accuracy\_comparison.py

```



The original model is preserved separately from the defended model so that the original red-team findings remain reproducible.



---



## 9. Security Conclusion



The red-team assessment demonstrated that the original model was susceptible to adversarial manipulation.



Adversarial training provided a measurable improvement against the tested FGSM attack:



```text

Original FGSM ASR:  68.01%

Defended FGSM ASR:  43.07%

Improvement:       24.94 percentage points

```



The defense reduced, but did not eliminate, the model's susceptibility to adversarial examples.



This demonstrates the importance of evaluating both model accuracy and adversarial robustness when deploying machine-learning systems.



