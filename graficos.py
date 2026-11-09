"""Figuras prontas para substituir os espaços marcados no artigo (matplotlib)."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def ler(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def criar_figuras(destino:Path):
    dados=ler(destino/'TABELA_1_COMPARACAO_METODOS.csv')
    tamanhos=sorted(set(int(x['n']) for x in dados))
    metodos=['EDD','SPT','WSPT','WSM_Equilibrado','AG','WSM_AG']
    fig,ax=plt.subplots(figsize=(10,5))
    for met in metodos:
        vals=[float(next(x for x in dados if int(x['n'])==n and x['metodo']==met)['media_atraso_ponderado']) for n in tamanhos]
        ax.plot([str(n) for n in tamanhos],vals,marker='o',label=met)
    ax.set(xlabel='Número de ordens por instância',ylabel='Média do atraso total ponderado',title='Comparação dos métodos por tamanho do problema')
    ax.legend(ncol=3,fontsize=9);ax.grid(alpha=.2);fig.tight_layout()
    fig.savefig(destino/'FIGURA_1_COMPARACAO.png',dpi=180);plt.close(fig)

    linhas=ler(destino/'TABELA_2_GANHO_HIBRIDO.csv')
    fig,ax=plt.subplots(figsize=(8,4.3));xs=[str(x['n']) for x in linhas]
    ax.bar(xs,[int(x['melhorou']) for x in linhas],label='Híbrido melhor')
    ax.bar(xs,[int(x['igual']) for x in linhas],bottom=[int(x['melhorou']) for x in linhas],label='Empate')
    ax.bar(xs,[int(x['piorou']) for x in linhas],bottom=[int(x['melhorou'])+int(x['igual']) for x in linhas],label='AG isolado melhor')
    ax.set(xlabel='Número de ordens',ylabel='Quantidade de instâncias',title='AG versus WSM+AG: média por instância')
    ax.legend();fig.tight_layout();fig.savefig(destino/'FIGURA_2_GANHO_HIBRIDO.png',dpi=180);plt.close(fig)

    hist=ler(destino/'convergencia.csv')
    fig,ax=plt.subplots(figsize=(9,4.4))
    ref=hist[0]['instancia']
    for met in ['AG','WSM_AG']:
        rows=[x for x in hist if x['instancia']==ref and x['metodo']==met]
        ax.plot([int(x['geracao']) for x in rows],[int(x['atraso_ponderado']) for x in rows],label=met)
    ax.set(xlabel='Geração',ylabel='Melhor atraso total ponderado',title=f'Convergência — {ref} (primeira repetição)')
    ax.legend();ax.grid(alpha=.2);fig.tight_layout()
    fig.savefig(destino/'FIGURA_3_CONVERGENCIA.png',dpi=180);plt.close(fig)

    sens_file=destino/'sensibilidade_pesos.csv'
    if sens_file.exists() and sens_file.stat().st_size>0:
        rows=ler(sens_file)
        ref=rows[0]['instancia'];rs=[x for x in rows if x['instancia']==ref]
        fig,ax=plt.subplots(figsize=(8.3,4.4))
        ax.scatter([float(x['peso_prazo']) for x in rs],[float(x['kendall_tau']) for x in rs],alpha=.7)
        ax.set(xlabel='Peso do prazo (WSM)',ylabel='τ de Kendall vs. pesos iguais',title=f'Análise de sensibilidade — {ref}')
        ax.grid(alpha=.2);fig.tight_layout()
        fig.savefig(destino/'FIGURA_4_SENSIBILIDADE.png',dpi=180);plt.close(fig)
