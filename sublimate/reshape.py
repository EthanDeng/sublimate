import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

engine = create_engine('mysql://root:dds123456@localhost/macro_data')
data = pd.read_excel('./gjdata.xlsx', index_col=0)
data = data.unstack().reset_index()
data.columns = ['code', 'date', 'value']
# data['date'] = data['date'].apply(lambda x: datetime.strptime(str(x), '%Y'))
data['date'] = pd.to_datetime(data['date'], format='%Y')
data['update_date'] = datetime.today().strftime('%Y-%m-%d')
data.to_sql('macro_data', con=engine, index=False, if_exists='append')
