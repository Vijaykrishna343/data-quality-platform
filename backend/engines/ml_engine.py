import pandas as pd
import numpy as np
import lightgbm as lgb
import shap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, mean_squared_error

class MLEngine:
    @staticmethod
    def train_model(df: pd.DataFrame, target_col: str, task_type: str = "classification", **kwargs):
        """
        Trains a LightGBM model. Returns the trained model and basic performance metrics.
        """
        if target_col not in df.columns:
            raise ValueError(f"Target column {target_col} not found in DataFrame.")

        df_ml = df.copy()
        
        # Determine features and target
        X = df_ml.drop(columns=[target_col])
        y = df_ml[target_col]

        # Drop rows where target is NaN
        valid_indices = y.dropna().index
        X = X.loc[valid_indices]
        y = y.loc[valid_indices]

        import re
        X.columns = [re.sub(r'[^\w]', '_', col) for col in X.columns]

        # 1. train_test_split first
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 2. fit scaler / preprocessing only on training data (No Leakage)
        from backend.engines.preprocessing_engine import PreprocessingEngine
        preprocessor = PreprocessingEngine()
        X_train = preprocessor.fit_transform(X_train)
        
        # 3. transform test separately
        X_test = preprocessor.transform(X_test)

        # Handle object/categorical types for LGBM
        cat_cols = X_train.select_dtypes(include=['object', 'category']).columns.tolist()
        for col in cat_cols:
            X_train[col] = X_train[col].astype('category')
            X_test[col] = X_test[col].astype('category')

        # Recommended Hyperparameters
        lgb_params = {
            "n_estimators": 200,
            "learning_rate": 0.05,
            "max_depth": 6,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42
        }
        for k, v in lgb_params.items():
            if k not in kwargs:
                kwargs[k] = v

        metrics = {}
        if task_type == "classification":
            n_classes = y.nunique()
            if n_classes == 2:
                model = lgb.LGBMClassifier(**kwargs)
            else:
                model = lgb.LGBMClassifier(num_class=n_classes, **kwargs)
                
            model.fit(X_train, y_train, categorical_feature=cat_cols)
            preds = model.predict(X_test)
            
            # Evaluate using standard classification metrics
            eval_metrics = MLEngine.evaluate_model(y_test, preds)
            metrics.update(eval_metrics)
            
            # Measure train vs test accuracy for overfitting detection
            train_preds = model.predict(X_train)
            train_accuracy = accuracy_score(y_train, train_preds)
            metrics["train_accuracy"] = float(train_accuracy)
            metrics["test_accuracy"] = float(metrics["accuracy"])
            
            # Generate SHAP explainability feature importance
            try:
                explanations = MLEngine.generate_explanations(model, X_test)
                metrics["explainability"] = explanations
            except Exception as e:
                metrics["explainability"] = {"error": f"SHAP generation failed: {str(e)}"}
        
        elif task_type == "regression":
            from sklearn.metrics import mean_absolute_error, r2_score
            if not pd.api.types.is_numeric_dtype(y):
                raise ValueError("Regression target must be numeric")
            model = lgb.LGBMRegressor(**kwargs)
            model.fit(X_train, y_train, categorical_feature=cat_cols)
            preds = model.predict(X_test)
            metrics["rmse"] = float(np.sqrt(mean_squared_error(y_test, preds)))
            metrics["mae"] = float(mean_absolute_error(y_test, preds))
            metrics["r2_score"] = float(r2_score(y_test, preds))
        else:
            raise ValueError(f"Unsupported task_type: {task_type}")
            
        # Monkey-patch the preprocessor into the model to avoid breaking method signature
        model.preprocessor = preprocessor

        import joblib
        import os
        os.makedirs("saved_models", exist_ok=True)
        joblib.dump(model, "saved_models/final_model.pkl")

        return model, metrics

    @staticmethod
    def predict(model, df: pd.DataFrame):
        '''
        Predict on new data.
        '''
        df_pred = df.copy()
        
        import re
        df_pred.columns = [re.sub(r'[^\w]', '_', col) for col in df_pred.columns]

        # Use stateful preprocessor from training
        if hasattr(model, 'preprocessor'):
            df_pred = model.preprocessor.transform(df_pred)
        else:
            # Fallback for older models without monkey-patched preprocessor
            from backend.engines.preprocessing_engine import PreprocessingEngine
            df_pred = PreprocessingEngine.process(df_pred)
            
        # Handle object/categorical types for LGBM
        cat_cols = df_pred.select_dtypes(include=['object', 'category']).columns.tolist()
        for col in cat_cols:
            df_pred[col] = df_pred[col].astype('category')
        
        return model.predict(df_pred)

    @staticmethod
    def evaluate_model(y_test, y_pred) -> dict:
        """
        Computes and returns standard classification metrics.
        """
        return {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
            "f1_score": float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
            "classification_report": classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        }

    @staticmethod
    def generate_explanations(model, X_test: pd.DataFrame) -> dict:
        """
        Generates SHAP explainability and feature importance values for the model.
        Also exports visual summary plots.
        """
        # Optimization: SHAP is O(N_rows * N_features), sample for large datasets
        X_test_sample = X_test.sample(min(200, len(X_test))) if len(X_test) > 0 else X_test
        
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test_sample)
        
        # Normalize shap_values to list of 2D arrays if it's 3D (N, F, C)
        if hasattr(shap_values, "shape") and len(shap_values.shape) == 3:
            shap_values = [shap_values[:, :, i] for i in range(shap_values.shape[2])]

        # Calculate mean absolute contribution for each feature
        if isinstance(shap_values, list):
            # Multiclass: list of arrays (one per class)
            mean_abs_shap = np.mean([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)
        else:
            # Binary classification or regression: 2D array
            mean_abs_shap = np.abs(shap_values).mean(axis=0)
            
        contributions = {str(col): float(val) for col, val in zip(X_test_sample.columns, mean_abs_shap)}
        
        # Sort features by importance
        feature_importance = dict(sorted(contributions.items(), key=lambda x: x[1], reverse=True))
        
        plot_base64 = None
        bar_plot_base64 = None
        
        try:
            import io
            import base64
            # Handle multiclass classification shap values (list of arrays)
            shap_values_to_plot = shap_values[1] if isinstance(shap_values, list) and len(shap_values) > 1 else shap_values

            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 1) Generate SHAP Visual Summary Plot Export
            plt.figure(figsize=(10, 6))
            shap.summary_plot(shap_values_to_plot, X_test_sample, show=False)
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
            plt.savefig(f"shap_summary_{timestamp}.png", format="png", dpi=300, bbox_inches="tight")
            plt.close()
            buf.seek(0)
            plot_base64 = base64.b64encode(buf.read()).decode("utf-8")
            
            # 2) Generate Optional Additional Plot (bar chart style)
            plt.figure(figsize=(10, 6))
            shap.summary_plot(shap_values, X_test_sample, plot_type="bar", show=False)
            plt.tight_layout()
            buf2 = io.BytesIO()
            plt.savefig(buf2, format="png", dpi=300, bbox_inches="tight")
            plt.savefig(f"shap_bar_{timestamp}.png", format="png", dpi=300, bbox_inches="tight")
            plt.close()
            buf2.seek(0)
            bar_plot_base64 = base64.b64encode(buf2.read()).decode("utf-8")
        except Exception as e:
            print(f"Plot generation failed: {str(e)}")
            plot_base64 = None
            bar_plot_base64 = None
        
        return {
            "feature_importance": feature_importance,
            "explainer_type": "TreeExplainer",
            "plot_base64": plot_base64,
            "bar_plot_base64": bar_plot_base64
        }
