import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import ast

#Mapear grupos e arquivos
grupos = {
    'Baixa': 'issues_baixa_popularidade.csv',
    'Média': 'issues_media_popularidade.csv',
    'Alta': 'issues_alta_popularidade.csv',
}

#Carregar dados, extrair comentário e montar dataframe único
dfs = []
for grupo, arquivo in grupos.items():
    df = pd.read_csv(arquivo)
    def extrai_total_count(x):
        try:
            if isinstance(x, str):
                data = ast.literal_eval(x)
                return data.get('totalCount')
            elif isinstance(x, dict):
                return x.get('totalCount')
            return np.nan
        except Exception:
            return np.nan
    df['comment_count'] = df['comments'].apply(extrai_total_count)
    df['Grupo'] = grupo
    dfs.append(df[['comment_count', 'Grupo']])

full_df = pd.concat(dfs, ignore_index=True)
full_df = full_df.dropna(subset=['comment_count'])
full_df['comment_count'] = full_df['comment_count'].astype(int)


full_df = full_df[full_df['comment_count'] < 50]

plt.figure(figsize=(10, 6))
sns.boxplot(
    data=full_df,
    x='Grupo',
    y='comment_count',
    showfliers=False,      
    palette='Blues'
)
plt.title("Distribuição de comentários por grupo de popularidade", fontsize=16)
plt.ylabel("Número de comentários", fontsize=12)
plt.xlabel("Grupo de popularidade", fontsize=12)
plt.tight_layout()
plt.savefig("boxplot_comentarios_popularidade.png", dpi=300)
plt.show()

