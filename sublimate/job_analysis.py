import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft Yahei']
plt.rcParams['axes.unicode_minus'] = False


sh_salary = pd.read_excel('上海零售批发.xlsx')
test = sh_salary.filter(['pos_salary', 'pos_title']).dropna()
print(test)


def wage_split(df, col=None, out_col=None):
    if col is None:
        col = 'pos_salary'
    if out_col is None:
        out_col = ['min_wage', 'max_wage', 'wage']
    df[out_col[0:2]] = df[col].str.split("-", n=1, expand=True)
    df[out_col[0]] = pd.to_numeric(df[out_col[0]])
    df[out_col[1]] = pd.to_numeric(df[out_col[1]])
    df[out_col[2]] = (df[out_col[0]] + df[out_col[1]])/2
    return df


def wage_density(df, job_col=None, positions=None):
    if job_col is None:
        job_col = ['pos_title', 'wage']
    wage_df = df.filter(job_col).dropna()
    print("wage_df", wage_df)
    if positions is None:
        positions = wage_df[job_col[0]].unique().tolist()
    wage_df = wage_df[wage_df.iloc[0] == positions]

    # positions = ['店员/营业员', '销售代表', '送餐员']
    plot_data = wage_df.pivot(columns=wage_df.columns[0], values=wage_df.columns[1])
    plot_data.plot.density(figsize=(8, 6),
                           xlim=(0, 20000),
                           linewidth=2)
    plt.xlabel("岗位平均工资")
    plt.legend(frameon=False)
    plt.ylabel("")
    plt.title("上海零售批发行业岗位招聘平均工资")
    plt.show()
    plt.savefig("上海零售批发行业岗位招聘平均工资.png", dpi=200)


clean_df = wage_split(test)
wage_density(clean_df, job_index=[1, 4], positions=['店员/营业员', '销售代表', '送餐员'])
