"""MODELO HÍBRIDO DE DECISÃO MULTICRITÉRIO: WSM + AG.

Experimentos reprodutíveis com WSM, AG, WSM+AG, EDD, SPT e WSPT.

Exemplos:
  python executar.py --modo piloto --repeticoes 2 --geracoes 25
  python executar.py --modo completo --repeticoes 10 --geracoes 100 --populacao 50

OBS: para o artigo, os dados são da OR-Library, NÃO de uma empresa.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import platform
import statistics
import sys
import time
from datetime import datetime,timezone
from pathlib import Path
from modelo import ConfigAG,PERFIS,NOME_MODELO,METODO_MULTICRITERIO,CRITERIOS_WSM,avaliar,genetico,kendall_tau,malha_pesos,ranking_wsm,regras,matriz_decisao_wsm
from baixar_dados import preparar_dados

ROOT=Path(__file__).resolve().parent

def escrever(path:Path, rows:list[dict]):
    if not rows:return
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8-sig') as file:
        wr=csv.DictWriter(file, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)

def media(rows,field):return statistics.mean(r[field] for r in rows)
def dpadrao(rows,field):return statistics.stdev(r[field] for r in rows) if len(rows)>1 else 0.0

def p_bilateral_sinais(ganhos:int,perdas:int) -> float:
    # Teste exato dos sinais, excluindo empates; H0 P(ganho)=P(perda)=0,5.
    n=ganhos+perdas
    if n==0:return 1.0
    menor=min(ganhos,perdas)
    return min(1.0,2*sum(math.comb(n,k) for k in range(menor+1))/(2**n))

def principal(args):
    inicio=time.perf_counter()
    destino=ROOT/'resultados'/args.modo
    destino.mkdir(parents=True,exist_ok=True)
    dados, hashes=preparar_dados(ROOT/'dados',args.modo)
    config=ConfigAG(populacao=args.populacao,geracoes=args.geracoes,
                    prob_cruzamento=args.cruzamento, prob_mutacao=args.mutacao)
    registro=[];sensibilidade=[];convergencia=[];sequencias=[];memorias_mcdm=[]
    print(NOME_MODELO, flush=True)
    print('Modelo multicritério: WSM; otimização: Algoritmo Genético.', flush=True)
    print(f'Início: {len(dados)} instância(s); {args.repeticoes} repetição(ões); '
          f'{config.geracoes} gerações; {config.populacao} indivíduos.',flush=True)
    for ix,inst in enumerate(dados,1):
        tam=inst.n
        # Regras determinísticas e WSM: não se repetem por seed.
        candidatos=regras(inst)
        for perfil,pesos in PERFIS.items():
            ranking, scores=ranking_wsm(inst,pesos)
            candidatos['WSM_'+perfil]=ranking
        for metodo,seq in candidatos.items():
            indicadores=avaliar(inst,seq)
            registro.append(dict(instancia=inst.nome,n=tam,metodo=metodo,repeticao=0,
                                 seed='',tempo_s=0.0,**indicadores))
        wsm_base=candidatos['WSM_Equilibrado']
        if inst.nome.endswith('_001'):
            # Evidência rastreável do modelo multicritério, por tamanho de problema.
            memorias_mcdm.extend(matriz_decisao_wsm(inst, PERFIS['Equilibrado']))
        # Análise completa de sensibilidade dos pesos em cada instância.
        if args.sensibilidade:
            for a,b,c in malha_pesos():
                rank,_=ranking_wsm(inst,(a,b,c))
                m=avaliar(inst,rank)
                sensibilidade.append(dict(instancia=inst.nome,n=tam,
                    peso_importancia=a,peso_tempo=b,peso_prazo=c,
                    kendall_tau=kendall_tau(wsm_base,rank),
                    top1_igual=int(wsm_base[0]==rank[0]),
                    top5_intersecao=len(set(wsm_base[:5]) & set(rank[:5])),
                    atraso_ponderado=m['atraso_ponderado']))
        # Mesmas seeds e orçamento para AG e Híbrido; variar somente inicialização.
        for r in range(args.repeticoes):
            seed=args.seed+ix*1000+r
            for metodo,seed_wsm in [('AG',None),('WSM_AG',wsm_base)]:
                t0=time.perf_counter()
                resposta=genetico(inst,config,seed,seed_wsm)
                segundos=time.perf_counter()-t0
                m=avaliar(inst,resposta['sequencia'])
                registro.append(dict(instancia=inst.nome,n=tam,metodo=metodo,
                    repeticao=r+1,seed=seed,tempo_s=round(segundos,6),**m))
                # Curva de convergência em uma instância piloto de cada tamanho.
                if inst.nome.endswith('_001') and r==0:
                    for gen,valor in enumerate(resposta['historico']):
                        convergencia.append(dict(instancia=inst.nome,n=tam,metodo=metodo,
                          geracao=gen,atraso_ponderado=valor))
                if inst.nome.endswith('_001') and r==0:
                    sequencias.append(dict(instancia=inst.nome,metodo=metodo,
                                           sequencia_1_based=' '.join(str(j+1) for j in resposta['sequencia']),
                                           atraso_ponderado=m['atraso_ponderado']))
        if ix%25==0 or ix==len(dados):
            print(f'  {ix}/{len(dados)} instâncias concluídas.',flush=True)
        # Checkpoint: dados parciais são preservados se a execução for interrompida.
        if ix%25==0:
            escrever(destino/'execucoes_PARCIAIS.csv',registro)
    escrever(destino/'execucoes.csv',registro)
    escrever(destino/'sensibilidade_pesos.csv',sensibilidade)
    escrever(destino/'convergencia.csv',convergencia)
    escrever(destino/'sequencias_exemplo.csv',sequencias)
    escrever(destino/'MATRIZ_DECISAO_MULTICRITERIO_WSM.csv',memorias_mcdm)

    # Médias da mesma instância para compensar estocasticidade do AG.
    grupos={}
    for linha in registro:
        chave=(linha['instancia'],linha['n'],linha['metodo'])
        grupos.setdefault(chave,[]).append(linha)
    resumo=[]
    for (id_inst,n,metodo),linhas in sorted(grupos.items()):
        resumo.append(dict(instancia=id_inst,n=n,metodo=metodo,
            repeticoes=len(linhas),media_atraso=round(media(linhas,'atraso_ponderado'),3),
            dp_atraso=round(dpadrao(linhas,'atraso_ponderado'),3),
            melhor_atraso=min(row['atraso_ponderado'] for row in linhas),
            media_tempo_s=round(media(linhas,'tempo_s'),6),
            media_ordens_atrasadas=round(media(linhas,'ordens_atrasadas'),3)))
    escrever(destino/'resumo_por_instancia.csv',resumo)
    # Agregação por tamanho: cada instância tem o mesmo peso (não cada execução).
    agrupado={}
    for r in resumo:agrupado.setdefault((r['n'],r['metodo']),[]).append(r)
    tabela1=[]
    for (n,metodo),rows in sorted(agrupado.items()):
        tabela1.append(dict(n=n,metodo=metodo,instancias=len(rows),
            media_atraso_ponderado=round(statistics.mean(x['media_atraso'] for x in rows),3),
            mediana_atraso_ponderado=round(statistics.median(x['media_atraso'] for x in rows),3),
            dp_entre_instancias=round(statistics.stdev(x['media_atraso'] for x in rows),3) if len(rows)>1 else 0,
            media_tempo_s=round(statistics.mean(x['media_tempo_s'] for x in rows),6)))
    escrever(destino/'TABELA_1_COMPARACAO_METODOS.csv',tabela1)
    # Estatística pareada por instância (AG e híbrido avaliados nas MESMAS seeds).
    per_inst={(r['instancia'],r['metodo']):r for r in resumo}
    pares=[]
    for inst in dados:
        ga=per_inst[(inst.nome,'AG')]['media_atraso']
        hy=per_inst[(inst.nome,'WSM_AG')]['media_atraso']
        wsm=per_inst[(inst.nome,'WSM_Equilibrado')]['media_atraso']
        pares.append(dict(instancia=inst.nome,n=inst.n,atraso_ag=ga,atraso_wsm_ag=hy,
          atraso_wsm=wsm,delta_ag_menos_hibrido=round(ga-hy,3),
          reducao_vs_ag_pct=round(100*(ga-hy)/ga,4) if ga>0 else '',
          hibrido_melhor=int(hy<ga),empate=int(hy==ga)))
    escrever(destino/'comparacao_pareada.csv',pares)
    tabela2=[]
    for n in sorted({inst.n for inst in dados}):
        sub=[r for r in pares if r['n']==n]
        tabela2.append(dict(n=n,instancias=len(sub),
          media_delta_ag_menos_hibrido=round(statistics.mean(x['delta_ag_menos_hibrido'] for x in sub),3),
          mediana_delta=round(statistics.median(x['delta_ag_menos_hibrido'] for x in sub),3),
          melhorou=sum(x['hibrido_melhor'] for x in sub),
          igual=sum(x['empate'] for x in sub),
          piorou=sum(x['delta_ag_menos_hibrido']<0 for x in sub)))
    escrever(destino/'TABELA_2_GANHO_HIBRIDO.csv',tabela2)
    tabela4=[]
    for linha in tabela2:
        ganhos,perdas=linha['melhorou'],linha['piorou']
        tabela4.append(dict(n=linha['n'],instancias=linha['instancias'],
              ganhos=ganhos,empates=linha['igual'],perdas=perdas,
              p_sinais_bilateral=p_bilateral_sinais(ganhos,perdas)))
    # Holm: controla erro familiar em três testes por tamanho.
    ordenada=sorted(range(len(tabela4)),key=lambda i:tabela4[i]['p_sinais_bilateral'])
    acumulado=0
    for j,i in enumerate(ordenada):
        acum=max(acumulado,min(1.0,(len(tabela4)-j)*tabela4[i]['p_sinais_bilateral']))
        tabela4[i]['p_holm']=acum;acumulado=acum
    escrever(destino/'TABELA_4_TESTE_SINAIS.csv',tabela4)
    tabela3=[]
    if sensibilidade:
        for n in sorted({inst.n for inst in dados}):
            rs=[x for x in sensibilidade if x['n']==n]
            tabela3.append(dict(n=n,cenarios_peso_por_instancia=66,
                tau_medio=round(statistics.mean(x['kendall_tau'] for x in rs),4),
                proporcao_primeiro_igual=round(statistics.mean(x['top1_igual'] for x in rs),4),
                top5_intersecao_medio=round(statistics.mean(x['top5_intersecao'] for x in rs),4),
                atraso_medio=round(statistics.mean(x['atraso_ponderado'] for x in rs),3)))
    escrever(destino/'TABELA_3_SENSIBILIDADE.csv',tabela3)
    parametros=dict(data_utc=datetime.now(timezone.utc).isoformat(),modo=args.modo,
       modelo=NOME_MODELO,metodo_mcdm=METODO_MULTICRITERIO,
       criterios_mcdm=[{'criterio':x,'tipo':y,'variavel_origem':z} for x,y,z in CRITERIOS_WSM],
       funcao_objetivo_ag='Minimizar soma_j q_j * max(0, C_j - d_j)',
       total_instancias=len(dados),instancias_por_tamanho={str(n):sum(x.n==n for x in dados) for n in sorted({x.n for x in dados})},
       repeticoes=args.repeticoes,seed_base=args.seed,
       configuracao_ga=vars(config),perfis_wsm=PERFIS,
       sensibilidade_66_cenarios=bool(args.sensibilidade),
       python=sys.version,plataforma=platform.platform(),hashes_sha256=hashes,
       duracao_total_s=round(time.perf_counter()-inicio,3))
    (destino/'manifesto_execucao.json').write_text(json.dumps(parametros,indent=2,ensure_ascii=False),encoding='utf-8')
    try:
        from graficos import criar_figuras
        criar_figuras(destino)
    except ImportError:
        print('Aviso: matplotlib não instalado; CSV e tabelas foram gerados. Instale requirements.txt para os gráficos.')
    with (destino/'LEIA_PARA_PREENCHER_ARTIGO.txt').open('w',encoding='utf-8') as f:
        f.write('SAÍDAS VALIDADAS APÓS EXECUÇÃO\n\n')
        f.write('MODELO MULTICRITÉRIO: Weighted Sum Model (WSM). O AG realiza otimização evolutiva.\n')
        f.write('Matriz e memória de cálculo WSM -> MATRIZ_DECISAO_MULTICRITERIO_WSM.csv\n')
        f.write('Tabela 1 do artigo -> TABELA_1_COMPARACAO_METODOS.csv\n')
        f.write('Tabela 2 do artigo -> TABELA_2_GANHO_HIBRIDO.csv\n')
        f.write('Tabela 3 do artigo -> TABELA_3_SENSIBILIDADE.csv\n')
        f.write('Tabela 4 do artigo -> TABELA_4_TESTE_SINAIS.csv\n')
        f.write('Figura 1 -> FIGURA_1_COMPARACAO.png\n')
        f.write('Figura 2 -> FIGURA_2_GANHO_HIBRIDO.png\n')
        f.write('Figura 3 -> FIGURA_3_CONVERGENCIA.png\n')
        f.write('Figura 4 -> FIGURA_4_SENSIBILIDADE.png\n\n')
        f.write('Hardware, configuração e data -> manifesto_execucao.json\n')
        f.write('ATENÇÃO: se o modo foi piloto, a amostra NÃO equivale às 375 instâncias.\n')
    try:
        from atualizar_artigo import popular
        if args.sensibilidade:
            popular(args.modo)
        else:
            print('Artigo não preenchido: parâmetro --sem-sensibilidade desativou a Figura 4.')
    except ImportError:
        print('Aviso: python-docx indisponível, tabelas e figuras permanecem em arquivos separados.')
    print(f'CONCLUÍDO. Resultados em: {destino}',flush=True)

def comandos():
    parser=argparse.ArgumentParser(description='Modelo híbrido de decisão multicritério WSM + AG com dados públicos OR-Library.')
    parser.add_argument('--modo',choices=['piloto','completo'],default='piloto')
    parser.add_argument('--repeticoes',type=int,default=3)
    parser.add_argument('--geracoes',type=int,default=100)
    parser.add_argument('--populacao',type=int,default=50)
    parser.add_argument('--seed',type=int,default=20261103)
    parser.add_argument('--cruzamento',type=float,default=0.9)
    parser.add_argument('--mutacao',type=float,default=0.2)
    parser.add_argument('--sem-sensibilidade',dest='sensibilidade',action='store_false')
    args=parser.parse_args()
    if args.repeticoes<1:parser.error('--repeticoes deve ser >= 1')
    return args

if __name__=='__main__':
    try:principal(comandos())
    except Exception as erro:
        print(f'ERRO: {erro}',file=sys.stderr)
        raise
