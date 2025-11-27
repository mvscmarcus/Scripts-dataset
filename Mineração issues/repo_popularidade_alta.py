import requests 
import pandas as pd
import time
import os

TOKEN = "SEU-TOKEN-GITHUB-AQUI"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
MAX_ISSUES = 200
os.makedirs("csv_issues", exist_ok=True)

repositorios = [
    ("public-apis", "public-apis"),
    ("donnemartin", "system-design-primer"),
    ("jwasham", "coding-interview-university"),
    ("ecomfe", "echarts"),
    ("google-research", "bert"),
    ("tensorflow", "models"),
    ("pallets", "flask"),
    ("psf", "requests"),
    ("matplotlib", "matplotlib"),
    ("scikit-learn", "scikit-learn"),
]

def coletar_issues(owner, repo):
    url = "https://api.github.com/graphql"
    issues = []
    cursor = None

    while len(issues) < MAX_ISSUES:
        after_str = f'"{cursor}"' if cursor else "null"
        query = f"""
        {{
          repository(owner:"{owner}", name:"{repo}") {{
            issues(first:100, states:CLOSED, orderBy:{{field:CREATED_AT, direction:DESC}}, after:{after_str}) {{
              pageInfo {{ hasNextPage endCursor }}
              nodes {{
                title
                createdAt
                closedAt
                comments {{ totalCount }}
              }}
            }}
          }}
        }}
        """
        response = requests.post(url, json={'query': query}, headers=HEADERS)
        if response.status_code != 200:
            print(f"Erro em {owner}/{repo}: {response.text}")
            break

        data = response.json()
        if "errors" in data or "data" not in data or not data["data"]["repository"]:
            print(f"Erro GraphQL ou sem dados em {owner}/{repo}")
            break

        repo_data = data["data"]["repository"]["issues"]
        issues.extend(repo_data["nodes"])
        if repo_data["pageInfo"]["hasNextPage"]:
            cursor = repo_data["pageInfo"]["endCursor"]
            time.sleep(1)
        else:
            break

    df = pd.DataFrame(issues)
    df["repo"] = f"{owner}/{repo}"
    if not df.empty:
        df["createdAt"] = pd.to_datetime(df["createdAt"])
        df["closedAt"] = pd.to_datetime(df["closedAt"])
        df["tempo_para_fechamento_dias"] = (df["closedAt"] - df["createdAt"]).dt.days
    return df

dfs = []
for owner, repo in repositorios:
    print(f"Coletando {owner}/{repo}...")
    dfs.append(coletar_issues(owner, repo))

df_final = pd.concat(dfs, ignore_index=True)
df_final.to_csv("csv_issues/issues_alta_popularidade.csv", index=False, encoding="utf-8")
print("Coleta finalizada! Arquivo salvo como issues_alta_popularidade.csv")
