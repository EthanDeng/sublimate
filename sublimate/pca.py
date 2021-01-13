import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from pandas import ExcelWriter
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


def optimal_component(cov_mat, threshold=0.85):
    eig_val, eig_vec = np.linalg.eig(cov_mat)
    idx = eig_val.argsort()[::-1]
    eig_ratio = np.cumsum(np.round(eig_val[idx], decimals=2)) / sum(eig_val[idx])
    result = min(enumerate(eig_ratio), key=lambda item: item[1] if item[1] > threshold else float('inf'))

    return result[0] + 1


full_data = pd.read_excel('source_data.xlsx')
data = full_data.query('年份==2018').filter(['城市', '土地出让金', '财政自给率', '财政赤字率', 'GDP'])
data.set_index('城市', inplace=True)
scaler = StandardScaler()
data_train = scaler.fit_transform(data)
data_train = pd.DataFrame(data=data_train,
                          index=data.index,
                          columns=data.columns)


corr_matrix = data_train.corr()
optimal_comp = optimal_component(corr_matrix)
print("The optimal components (info > 85%) are", optimal_comp)

n_comp = data_train.shape[1]
n_comp_names = ['Component' + str(item) for item in range(1, n_comp + 1)]
pca = PCA(n_comp)
# fit on data
pca.fit(data_train)
# access values and vectors

loadings = pd.DataFrame(pca.components_,
                        columns=data_train.columns,
                        index=n_comp_names)
eigenvalues = pd.DataFrame(pca.explained_variance_,
                           columns=['Explain_Variance'],
                           index=n_comp_names)
eigenvalues['Explain_Ratio'] = eigenvalues['Explain_Variance'] / eigenvalues['Explain_Variance'].sum()
eigenvalues['Cum_Explain_Ratio'] = eigenvalues['Explain_Ratio'].cumsum()

# transform data
component_matrix = pd.DataFrame(pca.transform(data_train),
                                columns=n_comp_names,
                                index=data_train.index)


with ExcelWriter('PCA_result.xlsx') as writer:
    loadings.to_excel(writer, sheet_name='loadings')
    eigenvalues.to_excel(writer, sheet_name='eigenvalues')
    component_matrix.to_excel(writer, sheet_name='component_matrix')
