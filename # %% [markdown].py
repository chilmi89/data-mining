# %% [markdown]
# ### import library

# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno
import numpy as np
import pandas as pd

# %% [markdown]
# ###  import dataset

# %%
dataset = pd.read_csv('loan_train.csv')
print("shape =" , dataset.shape)
dataset.head()


# %% [markdown]
# ### 3. Informasi Dataset

# %%
dataset.info()


# %% [markdown]
# ### deteksi Missing Values

# %%
# jumlah parsentasamissing value per kolom
missing_count = dataset.isnull().sum()
missing_pct   = (dataset.isnull().sum() / len(dataset)) * 100
missing_df    = pd.DataFrame({'Jumlah Missing': missing_count, 'Persentase (%)': missing_pct})
missing_df[missing_df['Jumlah Missing'] > 0]


# %%
# tampilkan baris yang mengandung missing value
dataset[dataset.isnull().any(axis=1)]


# %% [markdown]
# ### 5. Visualisasi Missing Values

# %%
plt.figure(figsize=(12, 5))
msno.matrix(dataset)
plt.title('visualisasi matriks missin values')
plt.tight_layout()
plt.show()


# %%
plt.figure(figsize=(10, 4))
missing_cols = missing_pct[missing_pct > 0]
missing_cols.plot(kind='bar', color='salmon')
plt.title('persentase missing value per kolom')
plt.ylabel('persentase (%)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# %% [markdown]
# ### 6. Penanganan Missing Values

# %%
# copy dataset
df = dataset.copy()

# Kolom kategorik: isi dengan modus (nilai paling sering muncul)
cat_cols_with_missing = ['Gender', 'Married', 'Dependents', 'Self_Employed', 'Credit_History']
for col in cat_cols_with_missing:
    if df[col].isnull().sum() > 0:
        mode_val = df[col].mode()[0]
        df[col].fillna(mode_val, inplace=True)
        print(f'[{col}] diisi dengan modus: {mode_val}')

# Kolom numerik: isi dengan median
num_cols_with_missing = ['LoanAmount', 'Loan_Amount_Term']
for col in num_cols_with_missing:
    if df[col].isnull().sum() > 0:
        median_val = df[col].median()
        df[col].fillna(median_val, inplace=True)
        print(f'[{col}] diisi dengan median: {median_val}')

print('\nMissing values setelah penanganan:')
print(df.isnull().sum())


# %% [markdown]
# ### 7. Deteksi Outliers dengan Boxplot

# %%
num_cols = ['ApplicantIncome', 'CoapplicantIncome', 'LoanAmount', 'Loan_Amount_Term']

fig, axes = plt.subplots(1, len(num_cols), figsize=(16, 5))
for ax, col in zip(axes, num_cols):
    df.boxplot(column=col, ax=ax)
    ax.set_title(col)
plt.suptitle('Boxplot Deteksi Outliers')
plt.tight_layout()
plt.show()


# %%
# Hitung jumlah outliers dengan metode IQR
def count_outliers(data, col):
    Q1  = data[col].quantile(0.25)
    Q3  = data[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    n     = ((data[col] < lower) | (data[col] > upper)).sum()
    return n, lower, upper

print(f'{'Kolom':<25} {'Jumlah Outlier':<20} {'Batas Bawah':<15} {'Batas Atas'}')
print('-' * 70)
for col in num_cols:
    n, lo, hi = count_outliers(df, col)
    print(f'{col:<25} {n:<20} {lo:<15.2f} {hi:.2f}')


# %% [markdown]
# ### 8. Penanganan Outliers (IQR Capping)

# %%
# Metode IQR Capping (Winsorizing) — outlier diganti dengan batas IQR
df_clean = df.copy()

def iqr_cap(data, col):
    Q1  = data[col].quantile(0.25)
    Q3  = data[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    data[col] = data[col].clip(lower=lower, upper=upper)
    return data

for col in num_cols:
    df_clean = iqr_cap(df_clean, col)

print('Statistik setelah IQR Capping:')
df_clean[num_cols].describe().round(2)


# %%
# Boxplot setelah penanganan outliers
fig, axes = plt.subplots(1, len(num_cols), figsize=(16, 5))
for ax, col in zip(axes, num_cols):
    df_clean.boxplot(column=col, ax=ax)
    ax.set_title(col)
plt.suptitle('Boxplot Setelah Penanganan Outliers')
plt.tight_layout()
plt.show()


# %% [markdown]
# ### 9. Pemodelan (Klasifikasi Loan_Status)

# %%
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Encode kolom kategorik
le = LabelEncoder()
cat_cols = ['Gender', 'Married', 'Dependents', 'Education', 'Self_Employed', 'Property_Area', 'Loan_Status']

def prepare(data):
    d = data.copy()
    d.drop(columns=['Loan_ID'], inplace=True)
    for col in cat_cols:
        d[col] = le.fit_transform(d[col].astype(str))
    return d

df_model = prepare(df_clean)
X = df_model.drop(columns=['Loan_Status'])
y = df_model['Loan_Status']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print('Train size:', X_train.shape[0], '| Test size:', X_test.shape[0])


# %%
def evaluate(model, X_tr, X_te, y_tr, y_te):
    model.fit(X_tr, y_tr)
    pred = model.predict(X_te)
    return {
        'Accuracy' : round(accuracy_score(y_te, pred) * 100, 2),
        'Precision': round(precision_score(y_te, pred, zero_division=0) * 100, 2),
        'Recall'   : round(recall_score(y_te, pred, zero_division=0) * 100, 2),
        'F-Score'  : round(f1_score(y_te, pred, zero_division=0) * 100, 2),
    }

dt  = DecisionTreeClassifier(random_state=42)
gnb = GaussianNB()

res_dt  = evaluate(dt,  X_train, X_test, y_train, y_test)
res_gnb = evaluate(gnb, X_train, X_test, y_train, y_test)

results = pd.DataFrame({
    'Metrik'        : ['Accuracy (%)', 'Precision (%)', 'Recall (%)', 'F-Score (%)'],
    'Decision Tree' : list(res_dt.values()),
    'Naive Bayes'   : list(res_gnb.values()),
})
print(results.to_string(index=False))



