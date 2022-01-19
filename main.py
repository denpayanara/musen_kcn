import urllib.parse

import requests
import pandas as pd

def musen_api(d):

    parm = urllib.parse.urlencode(d, encoding="shift-jis")
    r = requests.get("https://www.tele.soumu.go.jp/musen/list", parm)

    return r.json()

d = {
    # 1:免許情報検索  2: 登録情報検索
    "ST": 1,
    # 詳細情報付加 0:なし 1:あり
    "DA": 0,
    # スタートカウント
    "SC": 1,
    # 取得件数
    "DC": 3,
    # 出力形式 1:CSV 2:JSON 3:XML
    "OF": 2,
    # 無線局の種別
    "OW": "FB",
    # 所轄総合通信局
    "IT": "E",
    # 都道府県/市区町村
    "HCV": 29000,
    # 免許人名称/登録人名称
    "NA": "近鉄ケーブルネットワーク株式会社",
}

data = musen_api(d)

df = pd.json_normalize(data, "musen").rename(columns={"listInfo.tdfkCd": "name"})

se = df.value_counts("name")

df0 = (
    pd.concat([se], axis=1)
    .rename_axis("場所")
    .reset_index()
)

df0 = df0.rename(columns={0: '開設局数'})

df_code = pd.read_csv(
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vSkzhvYe66Y9el8my6n9Hk7qHKCFf_j3utHEjaU2rExCRLV3vUtHq9EE0dy0RI2AXgjBdyxSuBxTsUe/pub?gid=928286156&single=true&output=csv",
    dtype={"団体コード": int, "都道府県名": str, "郡名": str, "市区町村名": str},
).set_index('団体コード')

# 目的の都道府県名を指定
df_code = df_code[df_code['都道府県名'] == '奈良県']

df_code["市区町村名"] = df_code["郡名"].fillna("") + df_code["市区町村名"]
df_code.drop("郡名", axis=1, inplace=True)

# 団体コード290009の空の行を削除
df_code.drop(290009, axis=0, inplace=True)

df_code = df_code.reset_index()

df_code["場所"] = df_code["都道府県名"] + df_code["市区町村名"]

df1 = pd.merge(df_code, df0, on=["場所"], how="left")
df1["団体コード"] = df1["団体コード"].astype("Int64")

df1.sort_index(inplace=True)

df1["市区町村名"] = df1["市区町村名"].str.replace("^(添上郡|山辺郡|生駒郡|磯城郡|宇陀郡|高市郡|北葛城郡|吉野郡)", "", regex=True)

df1["開設局数"] = df1["開設局数"].fillna(0).astype(int)

df2 = df1[['市区町村名', '開設局数']]

df2.to_csv('musen_kcn.csv', encoding="utf_8_sig", index=False)
