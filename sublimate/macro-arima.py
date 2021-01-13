from pmdarima.arima import auto_arima
from pmdarima.arima import ADFTest
import pandas as pd
adf_test = ADFTest(alpha=0.05)

data = pd.read_excel('data.xlsx')
req_columns = ['土地出让金', '规划建筑面积', '地方一般公共预算收入', '地方一般公共预算支出', 'GDP',
               '人均GDP', '成交楼面均价', '房地产开发投资完成额', '基建投资完成额']
XY = data.filter(['时间', 'city'] + req_columns)

city = '保定'
sub_data = XY.query('city == @city')

pred_df = pd.DataFrame(columns=['时间', 'city'] + req_columns)
pred_df['时间'] = [2020, 2021, 2022]
pred_df['city'] = city

for item in req_columns:
    train_data = sub_data.loc[:, item]
    arima_model = auto_arima(train_data, error_action='ignore', trace=True,
                             suppress_warnings=True, maxiter=10,
                             seasonal=False)
    prediction = arima_model.predict(n_periods=3)
    pred_df.loc[:, item] = prediction

pred_df.to_excel('三年预测.xlsx')

data.interpolate(method='pad', limit=2)
