"""Modelo híbrido de decisão multicritério (MCDM/WSM) e otimização evolutiva.

O WSM é o ÚNICO método multicritério: normaliza três critérios de produção,
aplica pesos de preferência e produz um ranking. O Algoritmo Genético recebe
esse ranking como solução inicial e busca uma sequência com menor atraso
total ponderado. Não é uma otimização matemática multiobjetivo: o GA tem
uma função objetivo operacional única.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import random
from typing import Sequence

NOME_MODELO = "Modelo Híbrido de Decisão Multicritério WSM + Algoritmo Genético"
METODO_MULTICRITERIO = "Weighted Sum Model (WSM) / Método da Soma Ponderada"
CRITERIOS_WSM = (
    ("Importância", "Benefício", "q_j"),
    ("Tempo de processamento", "Custo", "p_j"),
    ("Prazo de conclusão", "Custo (urgência)", "d_j"),
)

@dataclass(frozen=True)
class Instancia:
    nome: str
    processamento: tuple[int,...]
    importancia: tuple[int,...]
    prazo: tuple[int,...]

    def __post_init__(self):
        n=len(self.processamento)
        if n < 2 or len(self.importancia)!=n or len(self.prazo)!=n:
            raise ValueError('A instância requer n>=2 e vetores de mesmo tamanho.')
        if any(v <= 0 for v in self.processamento+self.importancia):
            raise ValueError('Processamento e importância devem ser positivos.')
        if any(not isinstance(v,int) for v in self.processamento+self.importancia+self.prazo):
            raise ValueError('Os valores do benchmark devem ser inteiros.')

    @property
    def n(self):return len(self.processamento)


def ler_instancias(caminho, n: int) -> list[Instancia]:
    """Formato OFICIAL: blocos de n durações, n importâncias, n prazos."""
    from pathlib import Path
    arq=Path(caminho)
    try:
        valores=[int(v) for v in arq.read_text(encoding='ascii').split()]
    except ValueError as exc:
        raise ValueError(f'Inteiros inválidos em {arq}') from exc
    tam=3*n
    if not valores or len(valores)%tam!=0:
        raise ValueError(f'{arq.name}: esperado múltiplo de {tam} inteiros, obtido {len(valores)}.')
    return [Instancia(f'{arq.stem}_{i+1:03d}',
                      tuple(valores[k:k+n]), tuple(valores[k+n:k+2*n]),
                      tuple(valores[k+2*n:k+3*n]))
            for i,k in enumerate(range(0,len(valores),tam))]


def normalizar(valores: Sequence[int], beneficio: bool) -> list[float]:
    """Min-max em [0,1]. Critério constante = 1 para todas as ordens."""
    menor,maior=min(valores),max(valores)
    if menor==maior:return [1.0]*len(valores)
    amplitude=maior-menor
    return [(v-menor)/amplitude if beneficio else (maior-v)/amplitude for v in valores]


def ranking_wsm(inst: Instancia, pesos: tuple[float,float,float]):
    """(importância, duração, prazo); maior nota primeiro; desempate por ID."""
    if len(pesos)!=3 or any(not math.isfinite(x) or x<0 for x in pesos) or not math.isclose(sum(pesos),1.0,abs_tol=1e-9):
        raise ValueError('Os três pesos WSM devem ser não negativos e somar 1.')
    a=normalizar(inst.importancia,True)
    b=normalizar(inst.processamento,False)
    c=normalizar(inst.prazo,False)
    pont=[pesos[0]*a[i]+pesos[1]*b[i]+pesos[2]*c[i] for i in range(inst.n)]
    return tuple(sorted(range(inst.n), key=lambda i:(-pont[i],i))), tuple(pont)


def matriz_decisao_wsm(inst: Instancia, pesos: tuple[float, float, float]) -> list[dict]:
    """Memória de cálculo auditável do modelo de decisão multicritério.

    Cada linha registra os três critérios originais, as notas normalizadas,
    as contribuições ponderadas, a pontuação WSM e sua posição no ranking.
    A importância q_j do dataset NÃO deve ser confundida com o peso w_j do WSM.
    """
    ordem, pontos = ranking_wsm(inst, pesos)
    nw = normalizar(inst.importancia, True)
    nt = normalizar(inst.processamento, False)
    nd = normalizar(inst.prazo, False)
    posicoes = {id_: pos for pos, id_ in enumerate(ordem, 1)}
    linhas = []
    for j in range(inst.n):
        cw, ct, cd = pesos[0]*nw[j], pesos[1]*nt[j], pesos[2]*nd[j]
        assert math.isclose(cw+ct+cd, pontos[j], rel_tol=0, abs_tol=1e-9)
        linhas.append({
            "instancia": inst.nome,
            "ordem_id": j+1,
            "importancia_original_q": inst.importancia[j],
            "tempo_original_p": inst.processamento[j],
            "prazo_original_d": inst.prazo[j],
            "peso_importancia_w": pesos[0],
            "peso_tempo_w": pesos[1],
            "peso_prazo_w": pesos[2],
            "normalizado_importancia": round(nw[j], 10),
            "normalizado_tempo": round(nt[j], 10),
            "normalizado_prazo": round(nd[j], 10),
            "contribuicao_importancia": round(cw, 10),
            "contribuicao_tempo": round(ct, 10),
            "contribuicao_prazo": round(cd, 10),
            "pontuacao_wsm": round(pontos[j], 10),
            "posicao_no_ranking": posicoes[j],
        })
    return linhas


def regras(inst:Instancia) -> dict[str,tuple[int,...]]:
    n=range(inst.n)
    return {
        'EDD': tuple(sorted(n,key=lambda i:(inst.prazo[i],i))),
        'SPT': tuple(sorted(n,key=lambda i:(inst.processamento[i],i))),
        'WSPT':tuple(sorted(n,key=lambda i:(inst.processamento[i]/inst.importancia[i],i))),
    }


def avaliar(inst:Instancia, ordem:Sequence[int]) -> dict[str,int]:
    """Problema 1||sum(q_j T_j): 1 máquina, não-preemptivo, todos disponíveis t=0."""
    if len(ordem)!=inst.n or set(ordem)!=set(range(inst.n)):
        raise ValueError('Sequência não é uma permutação válida das ordens.')
    t=z=numero_atrasadas=atraso_simples=0
    for j in ordem:
        t+=inst.processamento[j]
        atraso=max(0,t-inst.prazo[j])
        z+=inst.importancia[j]*atraso
        atraso_simples+=atraso
        numero_atrasadas+=(atraso>0)
    return {'atraso_ponderado':z,'atraso_total':atraso_simples,'ordens_atrasadas':numero_atrasadas,'makespan':t}


def custo(inst:Instancia,ordem:Sequence[int]) -> int:
    t=z=0
    for j in ordem:
        t+=inst.processamento[j]
        if t>inst.prazo[j]:z+=(t-inst.prazo[j])*inst.importancia[j]
    return z


def cruzamento_ox(p1:tuple[int,...],p2:tuple[int,...],rng:random.Random) -> tuple[int,...]:
    """Order crossover (OX) preserva uma permutação válida."""
    n=len(p1)
    a,b=sorted(rng.sample(range(n),2))
    filho=[-1]*n
    filho[a:b+1]=p1[a:b+1]
    fixos=set(p1[a:b+1])
    faltantes=[v for v in p2[b+1:]+p2[:b+1] if v not in fixos]
    pos=list(range(b+1,n))+list(range(0,a))
    for ix,v in zip(pos,faltantes):filho[ix]=v
    assert -1 not in filho and len(set(filho))==n
    return tuple(filho)


def mutar(seq:tuple[int,...],rng:random.Random) -> tuple[int,...]:
    arr=list(seq);a,b=sorted(rng.sample(range(len(arr)),2))
    if rng.random()<0.5:arr[a],arr[b]=arr[b],arr[a]
    else:arr[a:b+1]=reversed(arr[a:b+1])
    return tuple(arr)

@dataclass(frozen=True)
class ConfigAG:
    populacao:int=50
    geracoes:int=100
    prob_cruzamento:float=0.9
    prob_mutacao:float=0.2
    torneio:int=3
    elite:int=2

    def __post_init__(self):
        if self.populacao<4 or self.geracoes<1 or not (1<=self.elite<self.populacao) or not (2<=self.torneio<=self.populacao):
            raise ValueError('Parâmetros inválidos da população, gerações, torneio ou elite.')
        if not(0<=self.prob_cruzamento<=1 and 0<=self.prob_mutacao<=1):
            raise ValueError('Probabilidades do GA devem estar em [0,1].')


def genetico(inst:Instancia,config:ConfigAG,seed:int,sequencia_wsm:tuple[int,...]|None=None):
    """GA isolado vs híbrido usam as MESMAS sequências aleatórias e mesma semente.

    Híbrido: substitui um indivíduo aleatório por 1 sequência WSM, sendo
    o orçamento de avaliações e a função de aptidão iguais ao AG isolado.
    """
    rng=random.Random(seed)
    base=list(range(inst.n))
    populacao=[]
    for _ in range(config.populacao):
        arr=base.copy();rng.shuffle(arr);populacao.append(tuple(arr))
    if sequencia_wsm is not None:
        if set(sequencia_wsm)!=set(base):raise ValueError('Seed WSM inválida.')
        populacao[0]=tuple(sequencia_wsm)
    avaliacoes={}
    def f(sol):
        if sol not in avaliacoes:avaliacoes[sol]=custo(inst,sol)
        return avaliacoes[sol]
    melhor=min(populacao,key=f); melhor_f=f(melhor)
    historico=[melhor_f]
    for _ in range(config.geracoes):
        ordenada=sorted(populacao,key=f)
        nova=list(ordenada[:config.elite])
        def selecionar():
            candidatos=rng.sample(populacao,config.torneio)
            return min(candidatos,key=f)
        while len(nova)<config.populacao:
            pai,mae=selecionar(),selecionar()
            filho=cruzamento_ox(pai,mae,rng) if rng.random()<config.prob_cruzamento else pai
            if rng.random()<config.prob_mutacao:filho=mutar(filho,rng)
            nova.append(filho)
        populacao=nova
        candidato=min(populacao,key=f)
        if f(candidato)<melhor_f:melhor,melhor_f=candidato,f(candidato)
        historico.append(melhor_f)
    return {'sequencia':melhor,'atraso_ponderado':melhor_f,'historico':historico,
            'avaliacoes_distintas':len(avaliacoes),'seed':seed}


def kendall_tau(ordem1:Sequence[int],ordem2:Sequence[int])->float:
    if len(ordem1)!=len(ordem2) or set(ordem1)!=set(ordem2):raise ValueError('Rankings incompatíveis.')
    n=len(ordem1);p={v:i for i,v in enumerate(ordem2)}
    discordantes=sum(p[ordem1[i]]>p[ordem1[j]] for i in range(n) for j in range(i+1,n))
    return 1-4*discordantes/(n*(n-1))

PERFIS={
    'Equilibrado':(1/3,1/3,1/3),
    'Importancia':(0.50,0.25,0.25),
    'Tempo':(0.25,0.50,0.25),
    'Prazo':(0.25,0.25,0.50),
}

def malha_pesos(passo_decimos=10):
    """Para passo 0,1 há 66 combinações de três pesos não negativos."""
    for a in range(passo_decimos+1):
        for b in range(passo_decimos+1-a):
            yield (a/passo_decimos,b/passo_decimos,(passo_decimos-a-b)/passo_decimos)
