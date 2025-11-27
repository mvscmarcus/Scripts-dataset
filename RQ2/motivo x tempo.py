import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
import numpy as np

#CONFIGURAÇÃO
PASTA = "csv_issues"
arquivos = {
    "Baixa": os.path.join(PASTA, "issues_baixa_popularidade.csv"),
    "Média": os.path.join(PASTA, "issues_media_popularidade.csv"),
    "Alta": os.path.join(PASTA, "issues_alta_popularidade.csv"),
}
sns.set(style="whitegrid", palette="coolwarm")

#Função de classificação
def classificar_motivo(titulo):
    if not isinstance(titulo, str):
        return "Outro"
    titulo = titulo.lower()
    if re.search("fix|bug|error|fail|crash", titulo):
        return "Correção de bug"
    elif re.search("feature|add|implement|request|suggestion|enhance", titulo):
        return "Nova funcionalidade"
    elif re.search("doc|readme|typo|document", titulo):
        return "Documentação"
    elif re.search("duplicate|invalid", titulo):
        return "Outros / duplicada"
    else:
        return "Outro"

#Carregar dados
dfs = []
for grupo, caminho in arquivos.items():
    if os.path.exists(caminho):
        df = pd.read_csv(caminho)
        df["grupo"] = grupo
        dfs.append(df)
if not dfs:
    raise FileNotFoundError("Nenhum arquivo de issues encontrado na pasta.")

df_all = pd.concat(dfs, ignore_index=True)
df_all["createdAt"] = pd.to_datetime(df_all["createdAt"], errors="coerce")
df_all["closedAt"] = pd.to_datetime(df_all["closedAt"], errors="coerce")
df_all["tempo_dias"] = (df_all["closedAt"] - df_all["createdAt"]).dt.days
df_all["motivo"] = df_all["title"].astype(str).apply(classificar_motivo)
df_all = df_all.dropna(subset=['tempo_dias'])

#Filtrar motivos principais
motivos_principais = ['Correção de bug', 'Documentação', 'Nova funcionalidade']
df_plot = df_all[df_all['motivo'].isin(motivos_principais)].copy()

ordem_motivos = motivos_principais

#GRÁFICO 1: BOXPLOT 
plt.figure(figsize=(10, 6))
sns.boxplot(
    data=df_plot,
    x='motivo',
    y='tempo_dias',
    palette="coolwarm",
    order=ordem_motivos,
    showfliers=False
)
plt.title("Distribuição do tempo de fechamento por motivo da issue", fontsize=16)
plt.ylabel("Tempo de fechamento (dias)", fontsize=12)
plt.xlabel("Motivo de fechamento", fontsize=12)
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("boxplot_motivo_tempo_filtrado.png", dpi=300)
plt.show()

#GRÁFICO 2: BARPLOT 
plt.figure(figsize=(10, 6))
sns.barplot(
    data=df_plot,
    x='motivo',
    y='tempo_dias',
    palette="coolwarm",
    order=ordem_motivos,
    estimator=np.mean,
    ci=None
)
plt.title("Tempo médio de fechamento por motivo da issue", fontsize=16)
plt.ylabel("tempo médio de fechamento (dias)", fontsize=12)
plt.xlabel("Motivo de fechamento", fontsize=12)
plt.xticks(rotation=0)
# Defina os limites e os intervalos do eixo y
limite_superior = 60  # ajuste conforme o valor necessário
plt.ylim(0, limite_superior)
plt.yticks(np.arange(0, limite_superior+1, 5))

plt.tight_layout()
plt.savefig("barplot_motivo_tempo_filtrado.png", dpi=300)
plt.show()

print("Análise concluída e gráficos gerados.")
