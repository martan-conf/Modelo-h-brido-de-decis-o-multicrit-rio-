# Modelo híbrido de decisão multicritério — WSM + Algoritmo Genético

## Título oficial do artigo

**MODELO HÍBRIDO DE DECISÃO MULTICRITÉRIO BASEADO NO MÉTODO DA SOMA PONDERADA E EM ALGORITMOS GENÉTICOS PARA PRIORIZAÇÃO E SEQUENCIAMENTO DA PRODUÇÃO: UMA AVALIAÇÃO COMPUTACIONAL COM DADOS PÚBLICOS**

O método **WSM** é o modelo de decisão multicritério: formaliza alternativas, critérios, normalização e pesos. O Algoritmo Genético é uma etapa de **otimização combinatória**, não um segundo método multicritério.

## 1. Objetivo

Comparar o Método da Soma Ponderada (WSM) isolado, um Algoritmo Genético (AG) isolado e um híbrido que utiliza a sequência WSM como **um** indivíduo da população inicial do AG, além de três regras de sequenciamento (EDD, SPT e WSPT). A função-objetivo é minimizar o atraso total ponderado de tarefas de uma máquina.

Os dados **não são de uma fábrica**. O conjunto completo é um benchmark gerado artificialmente e publicado pela OR-Library (Beasley, 1990). O programa mantém o WSM como **único método de decisão multicritério**. O AG é uma técnica de otimização combinatória, não outro método multicritério.

## 2. O que fazer no Windows

É necessário ter **Python 3.10 ou superior** instalado. O modo completo precisa de internet **na primeira execução**, para baixar os arquivos oficiais.

1. Extraia todo o ZIP, sem mover arquivos isolados.
2. Abra a pasta `codigo`.
3. Dê dois cliques em `TESTAR_PRIMEIRO.bat`. Ele instala as dependências, executa os testes e processa a primeira instância de 40 ordens que já acompanha o projeto.
4. Dê dois cliques em `EXECUTAR_ARTIGO_COMPLETO.bat` para processar **375 instâncias** com **10 repetições independentes** por instância, usando 100 gerações e 50 indivíduos. Uma execução completa pode demandar tempo de processamento significativo, dependendo do computador.
5. Localize os resultados em `codigo/resultados/completo/`. A cópia do artigo com tabelas e figuras inseridas será gravada em `artigo/Artigo_Modelo_MCDM_WSM_AG_RESULTADOS_COMPLETO.docx`.
6. Abra o Word preenchido, revise as seções destacadas (RESUMO, discussão e CONSIDERAÇÕES FINAIS), confira a revisão da literatura, a autoria e a formatação exigida pelo periódico.

Se a máquina bloquear a abertura de `.bat`, abra o terminal do VS Code na pasta `codigo` e execute:

```bat
py -3 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m unittest discover -s testes -v
python executar.py --modo piloto --repeticoes 3 --geracoes 30 --populacao 30
python executar.py --modo completo --repeticoes 10 --geracoes 100 --populacao 50 --seed 20261103
```

## 3. Como obter os dados caso o download automático falhe

Documentação: <https://people.brunel.ac.uk/~mastjjb/jeb/orlib/wtinfo.html>

Copie os seguintes arquivos **sem modificar o conteúdo** para a pasta `codigo/dados/`, usando exatamente estes nomes:

- <https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/wt40.txt>
- <https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/wt50.txt>
- <https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/wt100.txt>

O programa valida a existência de **125 instâncias por arquivo**. Se houver um problema de acesso ao site, ele exibirá uma mensagem e **não** inventará um resultado ou substituirá silenciosamente os dados oficiais por dados sintéticos.

## 4. Metodologia implementada

- **Entrada por ordem:** `p_j` = duração, `q_j` = peso de importância original do benchmark, `d_j` = prazo.
- **WSM:** importância é benefício; duração e prazo são custos. Os três critérios usam normalização min–máx. A pontuação segue `S_j = alpha*n(q_j)+beta*n_custo(p_j)+gamma*n_custo(d_j)`.
- **Cenários WSM:** pesos iguais (1/3,1/3,1/3), importância (0,5;0,25;0,25), tempo (0,25;0,5;0,25), prazo (0,25;0,25;0,5).
- **Regras:** EDD = menor prazo; SPT = menor duração; WSPT = menor razão duração/importância.
- **AG:** permutações de tarefas, torneio, OX, mutação de troca/inversão, elitismo. Fitness = `Z = soma(q_j*max(0,C_j-d_j))`.
- **AG híbrido:** igual ao AG, mas uma das permutações iniciais aleatórias é substituída pela ordem WSM equilibrada.
- **Pareamento:** AG e WSM+AG são executados com a mesma semente por instância e repetição e com os mesmos parâmetros. A comparação usa as médias das repetições por instância.
- **Sensibilidade:** 66 vetores de pesos (passo 0,1); tau de Kendall, posição 1 e Top 5.
- **Teste estatístico:** teste exato bilateral dos sinais (ganhos versus perdas; empates excluídos), com ajuste de Holm para os três tamanhos. Interprete valores-p juntamente com os tamanhos de efeito e limitações.

**Importante:** a OR-Library representa uma máquina, com todas as tarefas disponíveis no instante zero e sem interrupções. A pesquisa não modela linhas reais com turnos, colaboradores ou máquinas paralelas. A inicialização WSM não é garantida como ótima.

## 5. Arquivos gerados

| Arquivo | Finalidade no artigo |
|---|---|
| `TABELA_1_COMPARACAO_METODOS.csv` | Tabela 1: médias de atraso e tempos |
| `TABELA_2_GANHO_HIBRIDO.csv` | Tabela 2: ganhos, perdas e empates |
| `TABELA_3_SENSIBILIDADE.csv` | Tabela 3: robustez dos pesos WSM |
| `TABELA_4_TESTE_SINAIS.csv` | Tabela 4: teste estatístico |
| `FIGURA_1_COMPARACAO.png` | Figura 1: comparação por tamanho |
| `FIGURA_2_GANHO_HIBRIDO.png` | Figura 2: melhora/empate/perda |
| `FIGURA_3_CONVERGENCIA.png` | Figura 3: convergência de uma instância |
| `FIGURA_4_SENSIBILIDADE.png` | Figura 4: sensibilidade de uma instância |
| `execucoes.csv` | Todas as execuções brutas e indicadores |
| `resumo_por_instancia.csv` | Média, desvio-padrão e melhor valor por instância |
| `comparacao_pareada.csv` | Comparação entre AG e híbrido em todas as instâncias |
| `sensibilidade_pesos.csv` | 66 configurações por instância |
| `manifesto_execucao.json` | Modelo multicritério, critérios, pesos, função objetivo, data, sistema e hashes SHA-256 |
| `MATRIZ_DECISAO_MULTICRITERIO_WSM.csv` | Memória de cálculo do WSM por ordem para a primeira instância de cada tamanho |
| `Artigo_Modelo_MCDM_WSM_AG_RESULTADOS_COMPLETO.docx` | Artigo com tabelas/figuras preenchidas automaticamente |

Ao executar apenas o `piloto`, as saídas terão apenas **uma instância** e ficarão em `resultados/piloto/` para não serem confundidas com a avaliação integral.

## 6. Organização do projeto

- `modelo.py`: validações, ranking WSM, regras EDD/SPT/WSPT, função objetivo, GA, sensibilidade;
- `baixar_dados.py`: obtenção e validação dos datasets públicos;
- `executar.py`: protocolo experimental, relatórios, estatísticas e criação de figuras/documentos;
- `graficos.py`: gráficos originais a partir dos CSV;
- `atualizar_artigo.py`: preenche os marcadores de tabelas e figuras no documento;
- `criar_artigo_modelo.py`: código-fonte que gera o modelo do artigo;
- `testes/test_modelo.py`: testes automatizados.

## 7. Cuidados científicos antes de submeter

Os valores de pesos são **experimentais**, não validados com especialistas. O artigo contém um referencial teórico e uma revisão narrativa estruturada, **não uma revisão sistemática já concluída**. Complete e documente buscas bibliográficas se o periódico pedir revisão sistemática. Avalie a estabilidade de conclusões, não omita resultados desfavoráveis ao híbrido, indique explicitamente que o benchmark é sintético e guarde o manifesto para reprodutibilidade.

Referências metodológicas com DOI estão no documento Word. A origem dos dados é a OR-Library: <https://people.brunel.ac.uk/~mastjjb/jeb/orlib/wtinfo.html>.
