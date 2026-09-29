## PGD Defense Evaluation

To evaluate the effectiveness of adversarial training, the original pretrained model, the FGSM-defended model, and the PGD-defended model were tested against the same PGD attack configuration.

### Attack Configuration

* **Epsilon (ε):** 0.03
* **Step size (α):** 0.005
* **PGD steps:** 10
* **Dataset:** CIFAR-10 test set
* **Batch size:** 64
* **Evaluation:** Only images that were correctly classified before the attack were included in the attack-success calculation.

### Results

| Model               | Correctly Classified & Attacked | PGD Attack Success Rate | Accuracy After PGD |
| ------------------- | ------------------------------: | ----------------------: | -----------------: |
| Original Model      |                           6,114 |                  79.56% |             20.44% |
| FGSM-Defended Model |                           6,953 |                  53.49% |             46.51% |
| PGD-Defended Model  |                           7,149 |                  43.07% |             56.93% |

### Analysis

The original model was highly vulnerable to the evaluated PGD attack, with an attack success rate of **79.56%**.

After FGSM adversarial training, the PGD attack success rate decreased to **53.49%**, indicating improved robustness against the iterative PGD attack.

After additional PGD adversarial training, the attack success rate decreased further to **43.07%**, while the accuracy remaining after the attack increased to **56.93%**.

Compared with the original model, the PGD-defended model reduced the PGD attack success rate by **36.49 percentage points**.

Compared with the FGSM-defended model, PGD adversarial training produced an additional **10.42 percentage-point reduction** in PGD attack success rate.

### Conclusion

The experiment demonstrates that adversarial training improved the model's robustness against the evaluated PGD attack. PGD-based adversarial training provided additional robustness compared with FGSM-based training under the same PGD evaluation configuration.

However, the attack success rate remained **43.07%**, so the defense did not completely eliminate the vulnerability. The result therefore demonstrates **improved robustness rather than complete protection**.
