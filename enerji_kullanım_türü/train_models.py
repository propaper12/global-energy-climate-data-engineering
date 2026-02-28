import os
import sys  # Komut satırı argümanları için eklendi
import joblib
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from config import logger
from utils import load_all_datasets

def train_and_save_models(target_country=None):
    logger.info("ML Pipeline Başlatıldı (Gold Schema Sync)...")
    os.makedirs("models", exist_ok=True)
    
    # Gold Katmanından veriyi çekiyoruz
    df_co2, df_fossil, df_share, df_master = load_all_datasets()
    
    if df_master is None or df_master.empty:
        logger.error("HATA: Veritabanı boş.")
        return

    # 1. POLİTİKA SİMÜLATÖRÜ MODELİ
    df_sim = df_master.copy()
    df_sim['Share_Fossil'] = (df_sim['Fossil fuels'] / df_sim['Total_Gen']) * 100
    df_sim['Share_Nuclear'] = (df_sim['Nuclear'] / df_sim['Total_Gen']) * 100
    df_sim = df_sim.rename(columns={'Renewables_Percentage': 'Share_Renewables'})
    df_sim = df_sim.dropna(subset=['Per capita emissions', 'Share_Renewables', 'Share_Nuclear', 'Share_Fossil'])
    
    if not df_sim.empty:
        rf_sim_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_sim_model.fit(df_sim[['Share_Renewables', 'Share_Nuclear', 'Share_Fossil']], df_sim['Per capita emissions'])
        joblib.dump(rf_sim_model, "models/policy_simulator_rf.pkl")
        logger.info(" Global Simülatör Modeli güncellendi.")

    # 2. ÜLKE BAZLI MODELLER (PARAMETREYE GÖRE FİLTRELEME)
    df_ai = df_master.dropna(subset=['Renewables', 'Year', 'Fossil fuels', 'Nuclear', 'Per capita emissions'])
    
    # Eğer bir ülke seçildiyse sadece onu eğit, yoksa hepsini (target_country kontrolü)
    if target_country:
        entities = [target_country]
        logger.info(f"Hedef odaklı eğitim: {target_country}")
    else:
        entities = df_ai['Entity'].unique()
        logger.info(" Toplu eğitim başlatılıyor (Tüm Ülkeler).")

    success_count = 0
    for country in entities:
        df_target = df_ai[df_ai['Entity'] == country]
        if len(df_target) > 10: 
            X = df_target[["Year", "Fossil fuels", "Nuclear", "Per capita emissions"]]
            y = df_target["Renewables"]
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Şampiyon Model: XGBoost
            best_model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
            best_model.fit(X_train, y_train)
            
            preds = best_model.predict(X_test)
            metrics = {
                "name": "XGBoost Regressor",
                "r2": r2_score(y_test, preds),
                "mse": mean_squared_error(y_test, preds),
                "rmse": np.sqrt(mean_squared_error(y_test, preds)),
                "mae": mean_absolute_error(y_test, preds),
                "importance": best_model.feature_importances_.tolist()
            }
            
            # 2040 Projeksiyon Modeli
            poly = PolynomialFeatures(degree=2)
            X_poly = poly.fit_transform(df_target[['Year']])
            poly_model = Ridge().fit(X_poly, df_target['Renewables'])
            
            model_package = {
                "champion_model": best_model,
                "metrics": metrics,
                "poly_model": poly_model,
                "poly_transformer": poly
            }
            joblib.dump(model_package, f"models/ai_vision_{country}.pkl")
            success_count += 1
            logger.info(f"{country} modeli hazır.")
            
    logger.info(f" İşlem Tamam: {success_count} model dosyası güncellendi.")

if __name__ == "__main__":
    # Dışarıdan argüman gelip gelmediğini kontrol et (sys.argv)
    argument_country = sys.argv[1] if len(sys.argv) > 1 else None

    train_and_save_models(argument_country)
