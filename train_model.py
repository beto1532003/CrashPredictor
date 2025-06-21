import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Input, Dense, LSTM, LayerNormalization, MultiHeadAttention, Dropout, GlobalAveragePooling1D
from tensorflow.keras.optimizers import Adam
from pattern_detector import detect_pattern_type
import os

def train_model(values):
    if len(values) < 11:
        raise ValueError("✖ البيانات غير كافية للتدريب. أدخل على الأقل 11 قيمة.")

    pattern = detect_pattern_type(values)
    values = np.array(values).reshape(-1, 1)
    scaler = MinMaxScaler()
    values_scaled = scaler.fit_transform(values)
    os.makedirs("models", exist_ok=True)
    joblib.dump(scaler, "models/scaler.pkl")

    sequence_length = 10
    X, y = [], []
    for i in range(len(values_scaled) - sequence_length):
        X.append(values_scaled[i:i + sequence_length])
        y.append(values_scaled[i + sequence_length])
    X, y = np.array(X), np.array(y)

    if pattern == "LCG":
        model = Sequential([
            Input(shape=(10, 1)),
            Dense(64, activation='relu'),
            Dense(32, activation='relu'),
            Dense(1)
        ])
        model_name = "models/model_lcg.keras"

    elif pattern == "PRNG":
        model = Sequential([
            LSTM(64, input_shape=(10, 1), return_sequences=False),
            Dense(32, activation='relu'),
            Dense(1)
        ])
        model_name = "models/model_prng.keras"

    else:  # HASH
        input_layer = Input(shape=(10, 1))
        x = MultiHeadAttention(num_heads=2, key_dim=2)(input_layer, input_layer)
        x = LayerNormalization()(x)
        x = Dropout(0.1)(x)
        x = Dense(64, activation='relu')(x)
        x = Dropout(0.2)(x)
        x = Dense(32, activation='relu')(x)
        x = GlobalAveragePooling1D()(x)
        output = Dense(1)(x)
        model = Model(inputs=input_layer, outputs=output)
        model_name = "models/model_transformer.keras"

    model.compile(optimizer=Adam(), loss="mse")
    model.fit(X, y, epochs=200, batch_size=16, verbose=0)
    model.save(model_name)

    return pattern
