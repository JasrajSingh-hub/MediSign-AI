# Training Report — Emergency Gesture Recognition

- **Train samples:** 8080
- **Test samples:** 32305
- **Classes:** accident, call, doctor, help, hot, pain
- **Model file:** `C:\Users\kamle\OneDrive\Desktop\MediSign-AI\emergency\models\emergency_model_v2.pkl`

## Hyperparameters

```json
{
  "n_estimators": 200,
  "max_depth": 20,
  "min_samples_leaf": 2,
  "random_state": 42
}
```

## Cross-validation (f1_macro)

- **Mean:** 0.9612  **Std:** 0.0036
- **Folds:** [0.9630822201760739, 0.9661727452406521, 0.9562722663158292, 0.962450678058055, 0.9582137880458265]

## Evaluation (test set)

- **Accuracy:** 0.9649
- **Macro-F1:** 0.9654

| Class | Precision | Recall | F1 | Support |
|-------|----------:|-------:|---:|--------:|
| accident | 0.973 | 0.982 | 0.978 | 5712 |
| call | 0.951 | 0.951 | 0.951 | 5398 |
| doctor | 0.955 | 0.990 | 0.972 | 5114 |
| help | 0.982 | 0.972 | 0.977 | 4141 |
| hot | 0.964 | 0.930 | 0.946 | 5800 |
| pain | 0.968 | 0.969 | 0.968 | 6140 |
