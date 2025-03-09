import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import importlib.util

import itertools

# Data
file_path = r"Installation Sequences Optimization\Structure Simulations\SimulationDataset.py"

spec = importlib.util.spec_from_file_location("SimulationDataset", file_path)
SimulationDataset = importlib.util.module_from_spec(spec)
spec.loader.exec_module(SimulationDataset)

sequences = SimulationDataset.tags_data
displacements = SimulationDataset.data

built_values = {'#0':1,'#1':0.8387,'#2':0.7903,'#3':0.7419,'#4':0.6935,'#5':0.5645,'#6':0.5161,
                '#7':0.3225,'#8':0.3870,'#9':0.4838,'#10':0.1612,'#11':0.2258,'#12':0.0645,
                '#13':0.5483,'#14':0.8064,'#15':0.4193}

# Feature Engineering
def extract_features(seq_name, sequence, displacement):
    features = {}
    built_score = np.mean([built_values[rod] for rod in sequence])
    stability = np.std(displacement)
    convergence_rate = displacement[0] - np.mean(displacement[-5:])
    
    features['built_score'] = built_score
    features['stability'] = stability
    features['convergence_rate'] = convergence_rate
    return features

# Prepare dataset
feature_list = []
labels = []
for seq_name in sequences.keys():
    features = extract_features(seq_name, sequences[seq_name], displacements[seq_name])
    feature_list.append(features)
    labels.append(np.mean(displacements[seq_name]))  # Target: mean displacement

df = pd.DataFrame(feature_list)
X = df
y = labels

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model Training
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f'Mean Absolute Error: {mae}')

# =================================================================================================
# 特征工程：将杆件序列转换为数值
def sequence_to_features(sequence):
    return [built_values[rod] for rod in sequence]

X = np.array([sequence_to_features(sequences[key]) for key in sequences])
y = np.array([min(displacements[key]) for key in displacements])  # 目标值：最小位移

# 训练模型
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
print("Mean Absolute Error:", mean_absolute_error(y_test, y_pred))

# 生成所有可能的杆件顺序
rods = list(built_values.keys())
candidate_sequences = list(itertools.permutations(rods, 16))[:10]  # 限制 100 个排列组合

# 预测所有候选序列的稳定性
best_sequence = None
best_score = float('inf')
for seq in candidate_sequences:
    features = np.array(sequence_to_features(seq)).reshape(1, -1)
    score = rf.predict(features)[0]
    if score < best_score:
        best_score = score
        best_sequence = seq

print("Predicted Best Sequence:", best_sequence)
print("Predicted Best Stability Score:", best_score)