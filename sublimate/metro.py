import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
sns.set()


data = pd.read_excel('./data/地铁客运量.xlsx', index_col=0)
data['date'] = data.index
data['weekday'] = data['date'].apply(lambda x: 'm' + str(x.weekday() + 1))
data['yeek_week'] = data['date'].dt.strftime('%Y-%W')


city = '上海'
sub_data = data.filter([city, 'date', 'weekday', 'yeek_week'])
city_data = sub_data.pivot(index='yeek_week', columns='weekday', values=city)
city_data = city_data.interpolate(method='linear', limit_direction='forward', axis=0)

city_data['week_mean'] = city_data.eval('(m1 + m2 + m3 + m4 + m5 + m6 + m7)/7')
city_data['workday_mean'] = city_data.eval('(m1 + m2 + m3 + m4 + m5)/5')
city_data['weekend_mean'] = city_data.eval('(m6 + m7)/2')
plot_data = city_data.filter(['weekday', 'week_mean', 'workday_mean', 'weekend_mean'])
# plot_data.columns = ['weekday', 'week_mean', 'workday_mean', 'weekend_mean']
print(plot_data)
fig = plt.figure()
ax = plt.axes()

plt.plot(plot_data.index, plot_data['workday_mean'])
plt.plot(plot_data.index, plot_data['weekend_mean'])

plt.show()

city_data.to_excel('./data/%s.xlsx' % city)
