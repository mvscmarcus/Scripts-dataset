import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import ast

#CONFIGURAÇÃO
PASTA = "."
ARQUIVO_SAIDA_BOXPLOT = "comentarios_vs_tempo_boxplot.png"
ARQUIVO_SAIDA_REGPLOT = "comentarios_vs_tempo_scatterplot.png"

sns.set(style="whitegrid", palette="coolwarm")
print("Iniciando análise: Comentários vs. Tempo de Fechamento")

#CARREGAR E PREPARAR DADOS ---
arquivos = [
    "issues_baixa_popularidade.csv",
    "issues_media_popularidade.csv",
    "issues_alta_popularidade.csv",
]

dfs = []
arquivos_encontrados = 0
for f in arquivos:
    caminho = os.path.join(PASTA, f)
    if os.path.exists(caminho):
        try:
            dfs.append(pd.read_csv(caminho))
            arquivos_encontrados += 1
        except Exception as e:
            print(f"Erro ao ler {caminho}: {e}")
    else:
        print(f"Aviso: Arquivo não encontrado {caminho}")

if not dfs:
    print("Nenhum arquivo CSV de issues encontrado. A análise não pode continuar.")
else:
    print(f"Carregados {arquivos_encontrados} arquivos de issues.")
    df_all = pd.concat(dfs, ignore_index=True)

    #LIMPEZA E EXTRAÇÃO DE DADOS

    #Função robusta para extrair totalCount
    def get_comment_count(x):
        try:
            #Se for string, avalia como literal Python (ex: "{'totalCount': 5}")
            if isinstance(x, str):
                data = ast.literal_eval(x)
                return data.get('totalCount')
            #Se já for um dict (menos provável, mas por segurança)
            elif isinstance(x, dict):
                return x.get('totalCount')
            #Se for NaN, 0, ou outra coisa
            return np.nan
        except (ValueError, SyntaxError, TypeError):
            #Se falhar a avaliação (ex: string vazia ou mal formatada)
            return np.nan

    print("Extraindo contagem de comentários...")
    df_all["comment_count"] = df_all["comments"].apply(get_comment_count)


    print("Calculando tempo de fechamento...")
    df_all["createdAt"] = pd.to_datetime(df_all["createdAt"], errors="coerce")
    df_all["closedAt"] = pd.to_datetime(df_all["closedAt"], errors="coerce")
    df_all["tempo_dias"] = (df_all["closedAt"] - df_all["createdAt"]).dt.days


    df_all = df_all.dropna(subset=['tempo_dias', 'comment_count'])
    
    # Converter para int (após remover NaNs)
    df_all["comment_count"] = df_all["comment_count"].astype(int)
    df_all["tempo_dias"] = df_all["tempo_dias"].astype(int)

    # Remover tempos negativos (dados anômalos)
    df_all = df_all[df_all["tempo_dias"] >= 0]

    print(f"Total de {len(df_all)} issues válidas para análise.")

    #CÁLCULO DE CORRELAÇÃO ---
    print("\nCalculando correlação de Pearson...")

    df_filtered_corr = df_all[(df_all['tempo_dias'] < 365) & (df_all['comment_count'] < 50)]
    correlation = df_filtered_corr[['comment_count', 'tempo_dias']].corr()
    print("Valor de Correlação (Pearson):")
    print(correlation['tempo_dias'])

    #GRÁFICO 1: BOXPLOT
    print("\nGerando Boxplot (agrupado por faixas de comentários)...")
    
    # Criar faixas (bins) para contagem de comentários
    bins = [-1, 0, 1, 2, 5, 10, 20, np.inf]
    labels = ['0', '1', '2', '3-5', '6-10', '11-20', '21+']
    df_all['comment_bin'] = pd.cut(df_all['comment_count'], bins=bins, labels=labels)

    plt.figure(figsize=(10, 6))
    sns.boxplot(
        data=df_all,
        x='comment_bin',
        y='tempo_dias',
        palette="coolwarm",
        showfliers=False # Sem outliers para ver a caixa
    )
    plt.title("Tempo de fechamento por faixa de comentários", fontsize=16)
    plt.ylabel("Tempo de fechamento (dias)", fontsize=12)
    plt.xlabel("Contagem de comentários (Faixas)", fontsize=12)
    # Focando nos primeiros 100 dias para ver a mediana
    plt.ylim(0, 200)
    plt.tight_layout()
    plt.savefig(ARQUIVO_SAIDA_BOXPLOT, dpi=300)
    print(f"Boxplot salvo como: {ARQUIVO_SAIDA_BOXPLOT}")
    # plt.show() # Desabilitar plt.show()
    plt.clf() # Limpar a figura

    #GERAR GRÁFICO 2: REGPLOT (Scatter)
    print("\nGerando Gráfico de Regressão (Scatter Plot)...")
    

    df_filtered = df_all[(df_all['comment_count'] < 50) & (df_all['tempo_dias'] < 365)].copy()

    # Amostragem para evitar overplotting no scatter
    if len(df_filtered) > 5000:
        df_sample = df_filtered.sample(5000, random_state=1)
    else:
        df_sample = df_filtered

    plt.figure(figsize=(10, 6))
    sns.regplot(
        data=df_sample,
        x='comment_count',
        y='tempo_dias',
        scatter_kws={'alpha': 0.1, 's': 10}, 
        line_kws={'color': 'red', 'linewidth': 2} 
    )
    
    plt.title("Contagem de comentários vs Tempo de fechamento", fontsize=16)
    plt.ylabel("Tempo de Fechamento (dias)", fontsize=12)
    plt.xlabel("Contagem de Comentários", fontsize=12)
    plt.ylim(0, 200)
    plt.xlim(0, 50)
    plt.tight_layout()
    plt.savefig(ARQUIVO_SAIDA_REGPLOT, dpi=300)
    print(f"Gráfico de Regressão salvo como: {ARQUIVO_SAIDA_REGPLOT}")
    # plt.show() # Desabilitar plt.show()
    plt.clf() # Limpar a figura

    print("Análise concluída.")