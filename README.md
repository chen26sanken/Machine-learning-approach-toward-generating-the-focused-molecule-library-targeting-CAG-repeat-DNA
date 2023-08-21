# RF_Generation-of-a-focused-molecule-library-by-machine-learning-targeting-CAG-repeat-DNA

This repository contains the code and resources for the manuscript titled "Generation of a Focused Molecule Library by Machine Learning Targeting CAG-repeat DNA."

## Figure
![Figure](https://github.com/chen26sanken/RF_Generation-of-a-focused-molecule-library-by-machine-learning-targeting-CAG-repeat-DNA/assets/141697122/ee26ee9e-7d5c-46fb-98ab-50d6f06d8a52)

(A) The training (left) data proportion with the down-sampling adjustment shown in Table S3, entry 4 in ESI; the testing (right) data proportion without adjustment.
(B) The confusion matrix on the testing dataset. The confusion matrix with the highest recall (upper) and the highest precision (bottom).
(C) Receiver operating characteristic (ROC) curve with 3-fold cross-validation of the RF model performance.


## Evaluation Scores in Applying Down-Sampling (Hit Class)

Table S3: The evaluation scores in applying down-sampling. (The scores in this table are for the hit class)

| entry | average recall<sup>a</sup> | highest recall<sup>b</sup> | average precision<sup>a</sup> | highest precision<sup>b</sup> | average F1<sup>a</sup> | highest F1<sup>b</sup> | hits:non-hits in training | dropped non-hits<sup>c</sup> |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 0.17 | 0.32 | 0.51 | 0.8 | 0.26 | 0.43 | 76:324 | 1200 |
| 2 | 0.31 | 0.5 | 0.41 | 0.75 | 0.36 | 0.48 | 76:224 | 1300 |
| 3 | 0.54 | 0.64 | 0.28 | 0.38 | 0.37 | 0.45 | 76:124 | 1400 |
| 4 | 0.75 | 0.86 | 0.16 | 0.21 | 0.26 | 0.33 | 76:74 | 1450 |
| 5 | 0.89 | 0.96 | 0.11 | 0.13 | 0.20 | 0.23 | 76:49 | 1475 |
| 6 | 0.94 | 1 | 0.09 | 0.12 | 0.18 | 0.21 | 76:39 | 1485 |

<sup>a</sup>Average scores obtained from 100 recorded prediction scores where the non-hits removed in each replicate experiment differed. The five top and bottom values were excluded from the calculation.
<sup>b</sup>Highest scores obtained from 100 recorded prediction scores where the non-hits removed in each replicate experiment differed.
<sup>c</sup>Non-hits dropped in the whole dataset.

## Dataset

The dataset used in the study consists of 2000 small molecule compounds. The original dataset can be found here: [Dragon_2000cpds.csv.zip](Dragon_2000cpds.csv.zip).

## Scripts

The following scripts are provided in this repository:

1. [1-RFcls_main_latest.py](1-RFcls_main_latest.py): Run this script for classification and to obtain evaluation results.
2. [categorical_index.py](categorical_index.py): Required module for over-sampling.
3. [2-plot_feature_importance_ver2.py](2-plot_feature_importance_ver2.py): Modified plotting script for feature importance.

## Requirements

The following Python packages are required to run the code in this repository. You can install them using `pip` or any other suitable package manager:

```plaintext
numpy~=1.21.6
scikit-learn~=1.1.1
shap~=0.41.0
matplotlib~=3.5.1
pandas~=1.4.3
seaborn~=0.11.2
tqdm~=4.64.1
```


## Acknowledgments

We acknowledge the contributions and support that have made this work possible.
