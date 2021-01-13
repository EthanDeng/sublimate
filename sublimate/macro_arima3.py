from pmdarima import auto_arima
import matplotlib.pyplot as plt
import pandas as pd
from math import sqrt
from sklearn.metrics import mean_squared_error

data = pd.DataFrame({'gdp': [1.21, 1.34, 1.47, 1.66, 1.96, 2.29, 2.75, 3.55, 4.59, 5.1, 6.09, 7.55, 8.53, 9.57, 10.44,
                             11.02, 11.14, 12.14, 13.61],
                     'year': [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014,
                              2015, 2016, 2017, 2018]})


data = data.set_index('year')
train = data[:int(0.9 * len(data))]

test = data[int(0.9 * len(data)):]

model = auto_arima(train, trace=True, error_action="ignore", suppress_warnings=True)
model.fit(train)
gdp_pre = model.predict(n_periods=len(test))
# gdp_pre = model.predict(n_periods=3)
gdp_pre = pd.DataFrame(gdp_pre, test.index, columns=["Prediction"])

print("forecast:", gdp_pre)
#
plt.plot(train, label="Train")
plt.plot(test, label="test")
plt.plot(gdp_pre, label="Prediction")
plt.legend()
plt.show()
#
# rms = sqrt(mean_squared_error(test, gdp_pre))
# print("均方根误差rms:", rms)
