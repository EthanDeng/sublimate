import pandas as pd
import numpy as np

time_index = pd.date_range('01/01/2008', periods=12, freq='Y')
df = pd.DataFrame(index=time_index)

# Create feature with a gap of missing values
# df['bg'] = [47.10, 55.28, 72.91, 95.06, 120.24, 150.02, 171.26, 182.78, 183.51, 187.47, 202.52, 206.27]
df['bg'] = [47.10, 55.28, 72.91, 95.06, 120.24, 150.02, np.nan, 182.78, 183.51, 187.47, 202.52, np.nan]
new_df = df.interpolate(method='pchip', limit_direction='forward').round(2)
print(new_df)
