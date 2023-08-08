import pandas as pd


def categorical_index_fc():
    """
    identify which columns are the categorical variables
    :return:
    a list of where categorical variables locate
    """
    the_infile = 'dataset/Dragon_2000cpds.csv'
    df = pd.read_csv(the_infile)
    df = df.iloc[:, 8:]
    print("df", df.shape)

    df_head = df.iloc[:0, :]

    categorical_col = df.select_dtypes(include=['category', 'int'])
    categorical_col_name = categorical_col.columns.tolist()

    n = 0
    index = -1
    categorical_col_index = []
    for i in df_head:
        index += 1
        if i in categorical_col_name:
            n += 1
            categorical_col_index.append(index)
    print("n=", n)

    return categorical_col_index
