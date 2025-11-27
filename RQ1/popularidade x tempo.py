import pandas as pd
import matplotlib.pyplot as plt
import os

#CONFIGURAÇÃO DOS ARQUIVOS
PASTA = "csv_issues"

arquivos = {
    "Baixa": os.path.join(PASTA, "issues_baixa_popularidade.csv"),
    "Média": os.path.join(PASTA, "issues_media_popularidade.csv"),
    "Alta": os.path.join(PASTA, "issues_alta_popularidade.csv"),
}

#CARREGAR E PREPARAR DADOS
dfs = {}

for grupo, caminho in arquivos.items():
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    df = pd.read_csv(caminho)

    # Converte datas para datetime
    df["createdAt"] = pd.to_datetime(df["createdAt"], errors="coerce")
    df["closedAt"] = pd.to_datetime(df["closedAt"], errors="coerce")

    # Calcula tempo de fechamento em dias
    df["tempo_dias"] = (df["closedAt"] - df["createdAt"]).dt.days

    # Remove linhas sem tempo válido
    df = df.dropna(subset=["tempo_dias"])

    dfs[grupo] = df

df_baixa = dfs["Baixa"]
df_media = dfs["Média"]
df_alta  = dfs["Alta"]

#GRÁFICO 1: TEMPO MÉDIO POR GRUPO
medias = {
    "Baixa": df_baixa["tempo_dias"].mean(),
    "Média": df_media["tempo_dias"].mean(),
    "Alta":  df_alta["tempo_dias"].mean(),
}

plt.figure(figsize=(6, 4))
plt.bar(medias.keys(), medias.values(), color=["#f1c40f", "#e74c3c", "#3498db"])
plt.title("Tempo médio de fechamento por grupo de popularidade")
plt.xlabel("Grupo")
plt.ylabel("Dias (média)")
plt.tight_layout()
plt.savefig("RQ1_tempo_medio_fechamento_grupo.pdf", dpi=300)
plt.show()

#GRÁFICO 2: HISTOGRAMA DA DISTRIBUIÇÃO DOS TEMPOS

plt.figure(figsize=(10, 6))

bins = range(0, 601, 20)

plt.hist(
    df_baixa["tempo_dias"],
    bins=bins,
    alpha=0.6,
    label="Baixa",
    color="#f1c40f",
)
plt.hist(
    df_media["tempo_dias"],
    bins=bins,
    alpha=0.6,
    label="Média",
    color="#e74c3c",
)
plt.hist(
    df_alta["tempo_dias"],
    bins=bins,
    alpha=0.6,
    label="Alta",
    color="#3498db",
)

plt.title("Distribuição dos tempos de fechamento por grupo")
plt.xlabel("Dias até fechamento")
plt.ylabel("Número de issues")
plt.xlim(0, 600)
plt.legend(title="Grupo")

plt.tight_layout()
plt.savefig("RQ1_tempo_histograma.pdf", dpi=300)
plt.show()

print("Gráficos gerados: RQ1_tempo_medio_fechamento_grupo.pdf e RQ1_tempo_histograma.pdf")
