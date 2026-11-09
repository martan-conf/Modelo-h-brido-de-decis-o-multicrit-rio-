"""Gera o artigo acadêmico ABNT com marcadores de tabelas e figuras.
Apenas dados da literatura e metodologia são afirmados nesta versão;
resultados futuros são tratados como campos a preencher.
"""
from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'artigo'/'Artigo_Modelo_MCDM_WSM_AG_ABNT_MODELO.docx'
D=Document();s=D.sections[0]
s.page_width=Cm(21);s.page_height=Cm(29.7)
s.top_margin=Cm(3);s.left_margin=Cm(3);s.right_margin=Cm(2);s.bottom_margin=Cm(2)
normal=D.styles['Normal'];normal.font.name='Times New Roman';normal.font.size=Pt(12)
normal.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
normal.paragraph_format.first_line_indent=Cm(1.25)
normal.paragraph_format.line_spacing=1.5;normal.paragraph_format.space_after=Pt(0)
for nm in ['Heading 1','Heading 2']:
    st=D.styles[nm];st.font.name='Times New Roman';st.font.size=Pt(12);st.font.bold=True
    st.font.color.rgb=RGBColor(0,0,0)
    st.paragraph_format.first_line_indent=Cm(0)
    st.paragraph_format.space_before=Pt(12);st.paragraph_format.space_after=Pt(6)
    st.paragraph_format.keep_with_next=True
for name,size in [('Legenda',10),('Fonte',10),('Alerta',10),('Referencia',11),('Formula',11)]:
    if name not in D.styles:
        st=D.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
        st.font.name='Times New Roman';st.font.size=Pt(size)
        st.paragraph_format.first_line_indent=Cm(0);st.paragraph_format.line_spacing=1
        st.paragraph_format.space_after=Pt(5)
D.styles['Alerta'].font.color.rgb=RGBColor(117,68,11)
D.styles['Alerta'].font.bold=True
D.styles['Formula'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER
D.styles['Referencia'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
D.styles['Referencia'].paragraph_format.space_after=Pt(9)
foot=s.footer.paragraphs[0];foot.alignment=WD_ALIGN_PARAGRAPH.RIGHT
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');foot._p.append(fld)

def p(txt='',style=None):
    par=D.add_paragraph(style=style)
    if txt:par.add_run(txt)
    return par

def sec(txt,lvl=1):D.add_heading(txt,lvl)
def frm(text):p(text,'Formula')
def mark(txt):
    par=p(txt,'Alerta')
    for r in par.runs:
        shd=OxmlElement('w:shd');shd.set(qn('w:fill'),'FFF1BF');r._r.get_or_add_rPr().append(shd)
def caption(txt):p(txt,'Legenda')
def source(txt):p(txt,'Fonte')
def tabela(cod,legenda,origem):
    caption(legenda)
    mark(f'[[{cod}]] — INSERÇÃO AUTOMÁTICA APÓS EXECUTAR O EXPERIMENTO COMPLETO.')
    source(origem)
def figura(cod,legenda,origem):
    caption(legenda)
    mark(f'[[{cod}]] — INSERÇÃO AUTOMÁTICA A PARTIR DO GRÁFICO DO CÓDIGO.')
    source(origem)
def quadro(titulo,cab,linhas,origem):
    caption(titulo)
    t=D.add_table(rows=1,cols=len(cab));t.style='Table Grid';t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for j,x in enumerate(cab):t.rows[0].cells[j].text=str(x)
    for linha in linhas:
        c=t.add_row().cells
        for j,x in enumerate(linha):c[j].text=str(x)
    for i,row in enumerate(t.rows):
        for cell in row.cells:
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for par in cell.paragraphs:
                par.paragraph_format.first_line_indent=Cm(0)
                par.paragraph_format.line_spacing=1
                par.paragraph_format.space_after=Pt(2)
                for run in par.runs:
                    run.font.name='Times New Roman';run.font.size=Pt(9)
                    if i==0:run.bold=True
    source(origem)

par=D.add_paragraph();par.alignment=WD_ALIGN_PARAGRAPH.CENTER;par.paragraph_format.first_line_indent=Cm(0)
r=par.add_run('MODELO HÍBRIDO DE DECISÃO MULTICRITÉRIO BASEADO NO MÉTODO DA SOMA PONDERADA E EM ALGORITMOS GENÉTICOS PARA PRIORIZAÇÃO E SEQUENCIAMENTO DA PRODUÇÃO: UMA AVALIAÇÃO COMPUTACIONAL COM DADOS PÚBLICOS')
r.font.name='Times New Roman';r.font.size=Pt(13);r.bold=True
x=p('[INSERIR AUTOR(ES), VÍNCULO INSTITUCIONAL E E-MAIL]');x.alignment=WD_ALIGN_PARAGRAPH.CENTER
mark('MODELO DE ARTIGO ACADÊMICO. Não há resultados finais ou revisão sistemática concluída até a execução dos procedimentos descritos.')
sec('RESUMO')
p('A programação da produção envolve decisões em que atributos como duração, importância e prazo de conclusão podem apontar para prioridades diferentes. O presente trabalho propõe desenvolver e avaliar um modelo híbrido de decisão multicritério baseado no Método da Soma Ponderada (Weighted Sum Model — WSM) e em um Algoritmo Genético (AG) para priorização e sequenciamento de tarefas em máquina única. A pesquisa combina uma revisão narrativa estruturada da literatura com experimentos computacionais reproduzíveis em instâncias públicas da coleção Weighted Tardiness, disponibilizada na OR-Library. No procedimento proposto, o WSM agrega três critérios normalizados e produz um ranking de referência, utilizado como um dos indivíduos da população inicial do AG. A função objetivo do AG minimiza o atraso total ponderado, sendo as soluções confrontadas com o AG sem inicialização WSM e com regras clássicas de sequenciamento. O protocolo inclui diferentes tamanhos de instância, repetições independentes por semente e análise de sensibilidade dos pesos. [INSERIR AQUI, APÓS A EXECUÇÃO, OS PRINCIPAIS RESULTADOS NUMÉRICOS E A CONCLUSÃO RESUMIDA EM DUAS OU TRÊS FRASES.]')
p('Palavras-chave: modelo de decisão multicritério; Método da Soma Ponderada; Algoritmo Genético; sequenciamento da produção; OR-Library.')
sec('ABSTRACT')
p('Production scheduling requires decisions involving potentially conflicting criteria such as processing time, task importance, and due dates. This paper proposes a hybrid multicriteria decision-making model based on the Weighted Sum Model (WSM) and a Genetic Algorithm (GA) for prioritizing and sequencing jobs on a single machine. The study combines a structured narrative literature review and reproducible computational experiments using the public Weighted Tardiness instances from the OR-Library. The WSM ranks jobs according to normalized criteria, and the resulting permutation is injected into the initial population of a GA that minimizes total weighted tardiness. The methodology includes comparisons against a non-seeded GA and conventional dispatching rules, as well as sensitivity analyses and independent random repetitions. [ADD THE VERIFIED NUMERICAL FINDINGS AND FINAL CONCLUSION AFTER RUNNING THE EXPERIMENT.]')
p('Keywords: multicriteria decision-making model; weighted sum model; genetic algorithm; production scheduling; benchmark.')

sec('1 INTRODUÇÃO')
p('Estabelecer a sequência de execução de tarefas é uma decisão recorrente em sistemas produtivos. Em situações com recursos limitados, uma ordem de curta duração pode ser atraente porque libera rapidamente a máquina, enquanto outra, de maior importância, pode justificar atendimento antecipado mesmo quando necessita de mais tempo. O prazo de entrega acrescenta outra dimensão ao problema, pois nem sempre a ordem economicamente mais importante é também a mais urgente. Essa combinação de fatores torna relevante investigar métodos transparentes de apoio à priorização.')
p('O Método da Soma Ponderada (WSM) permite reunir critérios em uma pontuação de preferência, desde que suas escalas sejam previamente tratadas. Sua estrutura facilita a implementação e a interpretação do ranking produzido. Entretanto, a escolha dos pesos e do procedimento de normalização pode afetar a classificação, como discutem Mohammadi e Rezaei (2023). Nesse sentido, utilizar o WSM sem verificar sua estabilidade pode levar a conclusões apressadas sobre a prioridade das tarefas.')
p('Além da priorização, a programação da produção exige determinar uma sequência operacional que atenda a uma função objetivo. Para tarefas processadas em uma máquina, o atraso total ponderado representa uma forma de penalizar a conclusão após o prazo, levando em consideração a importância de cada tarefa. O uso de Algoritmos Genéticos para problemas combinatórios de programação da produção tem sido investigado em diferentes condições operacionais, incluindo pesquisas em periódicos da IEEE (Momenikorbekandi; Abbod, 2023; Li et al., 2025).')
p('Uma possibilidade de integração consiste em utilizar o ranking gerado pelo WSM como uma solução inicial de um Algoritmo Genético. O WSM não garante o menor atraso ponderado, mas pode fornecer uma sequência estruturada para o início da busca evolutiva. A hipótese precisa ser testada, porque incluir uma solução inicial aparentemente promissora também pode reduzir a diversidade ou produzir ganhos pequenos em determinadas instâncias.')
p('A pesquisa foi definida para não utilizar informações sigilosas nem dados operacionais de empresas. Como alternativa, emprega a coleção pública Weighted Tardiness da OR-Library (Beasley, 1990), formada por instâncias sintéticas voltadas a comparações computacionais. Embora essa escolha favoreça a reprodutibilidade, seus resultados não devem ser tratados como uma validação direta em uma indústria específica.')
p('A questão norteadora é: em instâncias públicas de sequenciamento de máquina única, a utilização de um modelo de decisão multicritério baseado no WSM para inicializar um Algoritmo Genético melhora a qualidade das soluções em relação ao mesmo algoritmo sem inicialização multicritério? O objetivo geral consiste em desenvolver e avaliar um modelo híbrido de decisão multicritério e otimização evolutiva, investigando a influência da matriz de decisão, da normalização e dos pesos do WSM sobre a classificação das ordens e sobre o atraso total ponderado alcançado após a busca genética.')

sec('2 REFERENCIAL TEÓRICO')
sec('2.1 Modelos de decisão multicritério e preferências',2)
p('Decisões com múltiplos critérios exigem distinguir o desempenho observado de cada alternativa e a importância atribuída a cada dimensão. A atribuição de pesos torna explícitas as preferências consideradas na avaliação, mas não elimina os conflitos existentes entre os critérios. Larbani e Aouni (2025) discutem a ligação entre diferentes paradigmas de apoio multicritério e de otimização, evidenciando que classificar alternativas e buscar soluções em um espaço de decisões são atividades conceitualmente distintas.')
p('No contexto da programação da produção, a literatura também discute sistemas que procuram tornar visíveis as escolhas entre objetivos conflitantes. Zeiträg, Figueira e Pereira (2024) apresentam um sistema de apoio à decisão associado a problemas de dimensionamento de lotes e programação produtiva. Embora o problema e os métodos desse trabalho não sejam iguais aos utilizados aqui, o estudo contribui para compreender a importância de documentar o processo decisório e seus compromissos entre objetivos.')
sec('2.2 Modelo de decisão multicritério pelo Método da Soma Ponderada (WSM)',2)
p('O WSM combina os critérios normalizados de uma alternativa por meio de uma soma de produtos. Considerando m alternativas e três critérios, a pontuação global Sᵢ é obtida por:')
frm('Sᵢ = α · rᵢ,importância + β · rᵢ,tempo + γ · rᵢ,prazo')
frm('α ≥ 0; β ≥ 0; γ ≥ 0; α + β + γ = 1')
p('Os coeficientes α, β e γ expressam, respectivamente, os pesos experimentais dos critérios de importância, duração e prazo. A alternativa mais bem classificada é aquela com maior Sᵢ. O resultado representa uma preferência relativa do modelo, não a probabilidade de cumprir um prazo ou uma solução ótima do sequenciamento.')
p('O comportamento do WSM depende dos dados e da transformação aplicada a cada critério. Mohammadi e Rezaei (2023) discutem problemas de consistência associados a modelos de agregação multicritério e mostram que a normalização merece atenção na interpretação dos rankings. Neste estudo, a normalização será mantida fixa para que mudanças de classificação possam ser atribuídas aos pesos e às características dos problemas analisados.')
sec('2.3 Algoritmos Genéticos para sequenciamento',2)
p('Algoritmos Genéticos são procedimentos de busca que trabalham com uma população de soluções candidatas. O processo alterna seleção, recombinação e mutação para explorar novas configurações, preservando soluções consideradas mais adequadas segundo uma função de aptidão. O trabalho clássico de Holland (1975) oferece a base conceitual desse tipo de algoritmo; aplicações recentes mostram adaptações voltadas ao sequenciamento produtivo.')
p('Momenikorbekandi e Abbod (2023), na IEEE Access, investigaram estratégias evolutivas para problemas de job shop. Li et al. (2025), na IEEE Transactions on Automation Science and Engineering, estudaram um problema flexível de programação da produção com recursos auxiliares, utilizando procedimentos evolutivos e busca de vizinhança. Esses trabalhos não demonstram a eficácia da combinação específica WSM+AG proposta aqui, mas sustentam o uso de metaheurísticas como estratégia de pesquisa em problemas combinatórios produtivos.')
p('Também no contexto de atrasos, Li et al. (2024) aplicaram um Algoritmo Genético a um problema de máquinas paralelas com tempos e prazos incertos. Huang, Tsai e Chou (2023) investigaram um problema de máquina única com restrições adicionais e uma estratégia genética. Esses exemplos reforçam a necessidade de declarar a configuração operacional analisada, uma vez que resultados obtidos em máquinas paralelas, com manutenção ou com tempos incertos não podem ser transferidos automaticamente para uma máquina única convencional.')
sec('2.4 Integração entre priorização e busca evolutiva',2)
p('O modelo híbrido examinado neste artigo utiliza o WSM apenas para produzir uma sequência inicial, sem modificar diretamente a função objetivo do AG. O mérito potencial da integração está na qualidade da população inicial; o ganho não é presumido, mas avaliado por comparação pareada. Um AG isolado e um AG com inicialização WSM empregam a mesma codificação, os mesmos operadores, os mesmos parâmetros e as mesmas sementes pseudoaleatórias. A única diferença deliberada é a substituição de um indivíduo aleatório pela sequência do WSM na população híbrida.')
p('A escolha permite uma avaliação mais específica do que simplesmente comparar o WSM com um algoritmo evolutivo. Se o híbrido apresentar melhoria sobre o AG isolado nas mesmas condições de execução, haverá indício de contribuição da inicialização multicritério. Caso os resultados sejam semelhantes ou piores, o estudo continuará relevante por delimitar situações nas quais a integração não trouxe benefícios observáveis.')

sec('3 METODOLOGIA')
sec('3.1 Delineamento da pesquisa e revisão bibliográfica',2)
p('A pesquisa tem caráter quantitativo e experimental na etapa computacional, complementado por uma revisão narrativa estruturada da literatura. Nesta versão, a revisão não é apresentada como revisão sistemática concluída. Para sua ampliação, propõe-se registrar buscas em IEEE Xplore, Scopus, Web of Science e ScienceDirect, com termos relacionados a “weighted sum model”, “simple additive weighting”, “genetic algorithm”, “single machine scheduling”, “weighted tardiness” e “hybrid optimization”. O recorte recomendado é 2019–2026, mantendo apenas referências anteriores de caráter fundador ou relacionadas à origem do benchmark.')
p('A seleção deverá considerar publicações revisadas por pares que descrevam critérios de priorização, algoritmos evolutivos de programação, estratégias de inicialização ou experimentos comparativos. Para cada estudo, pretende-se registrar ano, problema, fonte de dados, função objetivo, procedimento de validação e limitações. Se for adotada uma revisão sistemática formal, seus registros de identificação, triagem, elegibilidade e inclusão precisarão seguir recomendações de transparência como as do PRISMA 2020 (Page et al., 2021). Não serão atribuídos números de publicações encontradas antes da execução das buscas.')
mark('SE A REVISTA EXIGIR REVISÃO SISTEMÁTICA: INSERIR AQUI O PROTOCOLO EXECUTADO, TABELA DE ARTIGOS INCLUÍDOS E FLUXOGRAMA PRISMA COM CONTAGENS REAIS. Caso contrário, manter a classificação de revisão narrativa estruturada.')
sec('3.2 Base pública e problema de sequenciamento',2)
p('Os experimentos empregam a coleção Weighted Tardiness da OR-Library. A documentação oficial estabelece 125 instâncias de 40 ordens, 125 de 50 e 125 de 100, totalizando 375 instâncias. Cada ordem j dispõe de tempo de processamento pⱼ, importância qⱼ e prazo numérico dⱼ. Os dados foram gerados artificialmente, não representando registros de empresas. A comparação é realizada no problema de máquina única, com todas as tarefas disponíveis no instante zero e processamento sem interrupções (Beasley, 1990; OR-Library, s.d.).')
quadro('Quadro 1 — Composição do conjunto de dados', ['Arquivo','Ordens por instância','Instâncias','Variáveis'],[
 ('wt40.txt','40','125','pⱼ, qⱼ, dⱼ'),('wt50.txt','50','125','pⱼ, qⱼ, dⱼ'),('wt100.txt','100','125','pⱼ, qⱼ, dⱼ')],
 'Fonte: OR-Library — Weighted Tardiness (s.d.).')
p('Para uma sequência π, o tempo de conclusão Cⱼ de cada tarefa corresponde à soma dos tempos das tarefas processadas até sua posição. O atraso Tⱼ é definido como a diferença positiva entre conclusão e prazo; o objetivo operacional é minimizar a soma dos atrasos multiplicados pela importância de cada tarefa:')
frm('Tⱼ = max(0, Cⱼ − dⱼ)')
frm('Minimizar Z(π) = Σⱼ qⱼ · Tⱼ')
p('A importância qⱼ, fornecida pelo benchmark, não corresponde ao peso α do critério “importância” no WSM. Essa distinção é fundamental para não confundir a pontuação multicritério com a função objetivo do sequenciamento.')
p('No modelo multicritério, as alternativas são as ordens do benchmark e as colunas da matriz de decisão correspondem a três critérios: importância (benefício), tempo de processamento (custo) e prazo numérico (custo interpretado como urgência). Para cada instância, a matriz normalizada é multiplicada pelo vetor de pesos e resulta em uma pontuação para cada ordem. A memória de cálculo individual é exportada pelo código para demonstrar a contribuição de cada critério, sem acrescentar outros métodos multicritério.')
sec('3.3 Construção do modelo de decisão multicritério WSM',2)
p('O critério importância é tratado como benefício, sendo preferíveis valores mais altos. Tempo de processamento e prazo são tratados como critérios de custo, em que valores menores resultam em pontuação maior. Na interpretação do prazo, menor dⱼ indica prioridade temporal mais elevada. Adota-se a normalização linear min–máx:')
frm('rⱼ,benefício = (xⱼ − min(x))/(max(x) − min(x))')
frm('rⱼ,custo = (max(x) − xⱼ)/(max(x) − min(x))')
p('Se um critério apresentar o mesmo valor para todas as tarefas, a implementação atribui 1 a todas elas nesse critério. Por ser uma contribuição constante, esse tratamento evita divisão por zero sem alterar a posição relativa das ordens. Após o cálculo de Sⱼ, as tarefas são classificadas em ordem decrescente. Em caso de pontuações iguais, o desempate é feito pelo identificador original do benchmark.')
quadro('Quadro 2 — Estrutura do modelo de decisão multicritério', ['Componente','Definição operacional'], [
 ('Alternativas','Ordens de produção do benchmark público'),
 ('Critério 1','Importância da ordem (benefício; maior valor preferido)'),
 ('Critério 2','Tempo de processamento (custo; menor valor preferido)'),
 ('Critério 3','Prazo numérico (custo; menor valor = maior urgência)'),
 ('Normalização','Min–máx por critério e por instância'),
 ('Agregação','Soma ponderada dos três critérios, pesos não negativos com soma 1'),
 ('Saída multicritério','Pontuação S_j e ranking de prioridades (antes do AG)'),
 ('Integração','Ranking WSM equilibrado insere um indivíduo na população inicial do AG')
], 'Fonte: elaboração própria com base no código do experimento (2026).')
quadro('Quadro 3 — Perfis de ponderação WSM previstos no código', ['Perfil','Importância (α)','Tempo (β)','Prazo (γ)'],[
 ('Equilibrado','1/3','1/3','1/3'),('Ênfase em importância','0,50','0,25','0,25'),('Ênfase em tempo','0,25','0,50','0,25'),('Ênfase em prazo','0,25','0,25','0,50')],
 'Fonte: elaboração própria (2026). Os pesos são cenários de simulação; não foram validados por especialistas.')
sec('3.4 Implementação do Algoritmo Genético',2)
p('O cromossomo representa uma permutação de todas as tarefas, evitando repetições e omissões. A população inicial do AG isolado é formada por sequências aleatórias. No modelo híbrido, um desses indivíduos é substituído pela sequência obtida no WSM equilibrado. Os demais indivíduos são gerados pelo mesmo procedimento pseudoaleatório utilizado no AG isolado.')
p('A aptidão minimizada é exclusivamente Z(π), o atraso total ponderado, e não uma soma de diferentes objetivos. A seleção é por torneio, o cruzamento utiliza o operador Order Crossover (OX), a mutação aplica troca de posições ou inversão de um trecho, e o elitismo mantém os melhores indivíduos na geração seguinte. A utilização de operadores específicos de permutação evita sequências inválidas.')
quadro('Quadro 4 — Configuração planejada para o experimento integral', ['Parâmetro','Valor'],[
 ('Tamanho da população','50 indivíduos'),('Gerações','100'),('Probabilidade de cruzamento','0,90'),
 ('Probabilidade de mutação','0,20'),('Seleção','Torneio com 3 candidatos'),
 ('Elitismo','2 indivíduos'),('Repetições por instância','10 por AG e 10 por WSM+AG'),
 ('Semente base','20261103'),('Modelo de máquina','Uma máquina; tarefas não preemptivas')],
 'Fonte: parâmetros implementados em executar.py (2026). Valores configuráveis; não otimizados previamente.')
p('As duas variantes evolutivas são executadas para cada instância e cada semente, utilizando configuração idêntica de população e gerações. Embora o orçamento máximo por geração seja o mesmo, o código também registra tempos de execução, que podem diferir entre as variantes. Não se utiliza neste estudo uma otimização matemática exata como comparador, e não se reivindica garantia de otimalidade.')
sec('3.5 Métodos de comparação',2)
p('Serão calculados rankings diretos pelo WSM equilibrado e pelos três perfis de ênfase. Como referências operacionais, serão utilizadas EDD (Earliest Due Date), SPT (Shortest Processing Time) e WSPT (Weighted Shortest Processing Time), baseadas respectivamente em prazo crescente, tempo crescente e razão pⱼ/qⱼ crescente. A avaliação principal confrontará o AG isolado e o híbrido WSM+AG. As seis abordagens essenciais — EDD, SPT, WSPT, WSM equilibrado, AG e WSM+AG — serão apresentadas nos gráficos comparativos, sem impedir que os demais perfis WSM apareçam nas tabelas.')
p('O atraso total ponderado será o indicador primário. Também serão calculados o número de tarefas atrasadas, o atraso total simples e o tempo de processamento computacional. Para cada instância, os resultados das repetições do AG serão sintetizados por média, desvio-padrão e melhor valor observado; na comparação por tamanho de problema, cada instância terá o mesmo peso estatístico.')
sec('3.6 Análise de sensibilidade e reprodutibilidade',2)
p('A sensibilidade dos rankings WSM será examinada com 66 combinações de pesos não negativos em passos de 0,1, com soma unitária. Para cada configuração, serão calculados o coeficiente tau de Kendall em relação ao ranking equilibrado, a manutenção da primeira posição, a interseção entre os cinco primeiros colocados e o atraso ponderado da sequência correspondente. Essa etapa se refere à estabilidade da classificação WSM e não equivale à calibração do Algoritmo Genético.')
p('O programa registra os parâmetros, as versões do Python, a plataforma utilizada, a data de execução e os códigos SHA-256 dos arquivos públicos recebidos. Os resultados são exportados para CSV, com arquivos específicos para as tabelas e figuras do artigo. As comparações AG e WSM+AG são pareadas por instância e semente, permitindo examinar em quantos problemas o híbrido apresentou ganho, empate ou perda. Na etapa de discussão, as diferenças deverão ser interpretadas de forma descritiva; análises inferenciais adicionais só devem ser relatadas se forem efetivamente executadas e seus pressupostos forem avaliados.')

sec('4 RESULTADOS E DISCUSSÃO — CAMPOS PARA PREENCHIMENTO')
mark('ATENÇÃO: os campos a seguir serão preenchidos automaticamente pelo script atualizar_artigo.py após rodar EXECUTAR_ARTIGO_COMPLETO.bat. NÃO inserir valores do piloto como resultados das 375 instâncias.')
sec('4.1 Comparação das estratégias de sequenciamento',2)
p('A Tabela 1 apresenta a comparação das abordagens em cada tamanho de instância. Os resultados deverão ser interpretados considerando o atraso médio ponderado e a dispersão entre instâncias. Valores menores indicam melhor resultado para o indicador primário. A discussão deve distinguir desempenho médio de custo computacional, pois um procedimento pode produzir atraso menor às custas de mais tempo de execução.')
tabela('TABELA_1','Tabela 1 — Comparação dos métodos por tamanho do benchmark','Fonte: elaboração própria, a partir de TABELA_1_COMPARACAO_METODOS.csv (após execução).')
figura('FIGURA_1','Figura 1 — Atraso total ponderado médio dos métodos por tamanho de instância','Fonte: elaboração própria, gerada por FIGURA_1_COMPARACAO.png.')
mark('REDAÇÃO A COMPLETAR: informar quais métodos obtiveram menor atraso em n=40, 50 e 100; indicar a magnitude dos resultados e suas limitações.')
sec('4.2 Contribuição da inicialização WSM ao Algoritmo Genético',2)
p('O efeito da integração será avaliado pela diferença entre o atraso médio do AG isolado e o atraso médio do modelo híbrido na mesma instância. Uma diferença positiva indica que WSM+AG produziu menor atraso. Para cada tamanho, também será registrada a quantidade de instâncias em que o híbrido melhorou, empatou ou piorou em relação ao AG, de acordo com a média das repetições.')
frm('Δᵢ = Z̄AG,ᵢ − Z̄WSM+AG,ᵢ')
tabela('TABELA_2','Tabela 2 — Comparação pareada entre AG e WSM+AG','Fonte: elaboração própria, a partir de TABELA_2_GANHO_HIBRIDO.csv (após execução).')
figura('FIGURA_2','Figura 2 — Número de instâncias com ganho, empate ou perda do modelo híbrido','Fonte: elaboração própria, gerada por FIGURA_2_GANHO_HIBRIDO.png.')
p('As trajetórias de convergência permitem observar a evolução do melhor indivíduo ao longo das gerações. Elas devem ser utilizadas apenas como evidência descritiva de um exemplo de execução e não como prova isolada da superioridade de uma estratégia sobre todo o benchmark.')
figura('FIGURA_3','Figura 3 — Evolução do melhor atraso ponderado no AG e no WSM+AG','Fonte: elaboração própria, gerada por FIGURA_3_CONVERGENCIA.png; primeira instância de um tamanho.')
mark('REDAÇÃO A COMPLETAR: interpretar ganhos médios, dispersão, tempo computacional, empates e o comportamento das curvas. Não declarar significância estatística sem o teste apropriado.')
sec('4.3 Estabilidade dos pesos do WSM',2)
p('A Tabela 3 sintetizará a estabilidade das classificações nos 66 cenários experimentais. O tau de Kendall permite examinar mudanças na ordenação completa, enquanto a preservação da primeira posição e a interseção do conjunto dos cinco primeiros verificam diferenças em partes específicas do ranking.')
tabela('TABELA_3','Tabela 3 — Sensibilidade dos rankings WSM às variações dos pesos','Fonte: elaboração própria, a partir de TABELA_3_SENSIBILIDADE.csv (após execução).')
figura('FIGURA_4','Figura 4 — Sensibilidade do ranking ao peso atribuído ao prazo','Fonte: elaboração própria, gerada por FIGURA_4_SENSIBILIDADE.png.')
mark('REDAÇÃO A COMPLETAR: discutir se o ranking foi robusto ou sensível a mudanças de pesos e em quais faixas ocorreu maior alteração. Não atribuir os pesos experimentais a especialistas.')
sec('4.4 Discussão à luz da literatura',2)
p('Para complementar a comparação descritiva, será aplicado o teste exato dos sinais às diferenças entre as médias do AG e WSM+AG em cada instância, excluindo empates. O procedimento avalia se a quantidade de instâncias favoráveis a uma variante difere da quantidade favorável à outra, sob a hipótese nula de probabilidades iguais. Os três valores-p por tamanho serão ajustados pelo procedimento de Holm. A significância, caso seja observada, não demonstrará efeito em aplicações empresariais reais nem substituirá a análise das magnitudes das diferenças.')
tabela('TABELA_4','Tabela 4 — Teste exato dos sinais para a comparação pareada','Fonte: elaboração própria, a partir de TABELA_4_TESTE_SINAIS.csv (após execução).')
p('A interpretação dos resultados deverá retomar a distinção entre pontuação multicritério e otimização de sequenciamento. Mesmo quando a classificação do WSM favorecer tarefas de importância elevada e curto prazo, isso não garante menor atraso total ponderado. A eventual melhoria obtida pelo AG dependerá das interações entre a ordem inicial, as combinações de tarefas e as operações evolutivas realizadas.')
p('Se o híbrido superar o AG isolado de modo recorrente, os resultados sugerirão que a solução WSM pode representar uma inicialização útil nas instâncias examinadas. Se houver empates ou perdas, esses casos deverão ser apresentados e relacionados à diversidade da população, à variação de prazos e às particularidades das instâncias. Em ambos os casos, os achados dialogarão com a necessidade de avaliação empírica da qualidade de soluções heurísticas e com as ressalvas sobre métodos de agregação indicadas por Mohammadi e Rezaei (2023).')
mark('REDAÇÃO A COMPLETAR: confrontar os resultados efetivamente obtidos com 3 a 5 estudos da revisão, respeitando diferenças de base, função objetivo e restrições. Evitar afirmar que a literatura “comprova” o seu modelo específico.')

sec('5 LIMITAÇÕES DO ESTUDO')
p('A primeira limitação decorre da natureza sintética do benchmark utilizado. Embora permita comparação reproduzível, a OR-Library não reúne condições reais de uma fábrica específica, como mudança de turno, setups, absenteísmo, disponibilidades diferentes de máquinas ou variações de produtividade individual. A segunda limitação é a adoção de uma máquina única com tarefas independentes, que não equivale a um ambiente job shop ou a uma linha industrial com múltiplos recursos.')
p('Outra limitação relaciona-se ao fato de os pesos do WSM terem sido definidos como cenários hipotéticos, sem elicitação com especialistas. Os parâmetros do AG também são fixados para permitir comparação controlada, sem um procedimento abrangente de calibração. Assim, uma eventual superioridade do híbrido deve ser restrita à configuração e aos dados testados. A influência das sementes pseudoaleatórias é parcialmente tratada por meio de repetições, mas não exclui a necessidade de estudos posteriores com parâmetros e operadores alternativos.')

sec('6 CONSIDERAÇÕES FINAIS')
p('Este trabalho propõe um modelo híbrido de decisão multicritério e otimização combinatória, estruturado com o WSM como único método multicritério e um Algoritmo Genético para sequenciamento de tarefas. A principal contribuição metodológica prevista consiste em examinar, sobre dados públicos e repetíveis, se a incorporação do ranking WSM na população inicial modifica o desempenho de uma busca evolutiva quando a função objetivo é o atraso total ponderado.')
mark('APÓS EXECUTAR O EXPERIMENTO COMPLETO: substituir este destaque por um parágrafo conclusivo com números verificáveis, limitações e resposta explícita à questão de pesquisa. Se o híbrido não superar o AG, declarar esse resultado com a mesma clareza.')
p('Como continuidade, poderão ser avaliadas outras configurações do Algoritmo Genético, alternativas de normalização, estratégias de inicialização mais diversificadas e benchmarks com múltiplas máquinas. A aplicação prática a organizações dependerá de estudos adicionais autorizados e não integra o escopo desta versão.')

sec('REFERÊNCIAS')
refs=[
'BEASLEY, J. E. OR-Library: distributing test problems by electronic mail. Journal of the Operational Research Society, v. 41, n. 11, p. 1069–1072, 1990. DOI: https://doi.org/10.1057/jors.1990.166.',
'HOLLAND, J. H. Adaptation in natural and artificial systems. Ann Arbor: University of Michigan Press, 1975.',
'HUANG, S.; TSAI, Y.-C.; CHOU, F.-D. A trajectory-based immigration strategy genetic algorithm to solve a single-machine scheduling problem with job release times and flexible preventive maintenance. Algorithms, v. 16, n. 4, art. 207, 2023. DOI: https://doi.org/10.3390/a16040207.',
'LARBANI, M.; AOUNI, B. A generalized approach for multi-criteria decision aid methods. Annals of Operations Research, v. 346, p. 1187–1215, 2025. DOI: https://doi.org/10.1007/s10479-024-06327-4.',
'LI, J.; LI, X.; GAO, L.; LIU, Q. A flexible job shop scheduling problem considering on-site machining fixtures: a case study from customized manufacturing enterprise. IEEE Transactions on Automation Science and Engineering, v. 22, p. 8415–8426, 2025. DOI: https://doi.org/10.1109/TASE.2024.3485810.',
'LI, K.; XU, L.; ZHANG, H.; CHEN, J. A genetic algorithm for fuzzy identical parallel machine scheduling of minimising total weighted tardiness under resource constraint. International Journal of Production Research, v. 62, n. 21, p. 7619–7643, 2024. DOI: https://doi.org/10.1080/00207543.2024.2323065.',
'MOHAMMADI, M.; REZAEI, J. Ratio product model: a rank-preserving normalization-agnostic multi-criteria decision-making method. Journal of Multi-Criteria Decision Analysis, v. 30, n. 5–6, p. 163–172, 2023. DOI: https://doi.org/10.1002/mcda.1806.',
'MOMENIKORBEKANDI, A.; ABBOD, M. F. A novel metaheuristic hybrid parthenogenetic algorithm for job shop scheduling problems: applying an optimization model. IEEE Access, v. 11, p. 56027–56045, 2023. DOI: https://doi.org/10.1109/ACCESS.2023.3278372.',
'OR-LIBRARY. Weighted tardiness: benchmark instances and documentation. Brunel University London, [s.d.]. Disponível em: https://people.brunel.ac.uk/~mastjjb/jeb/orlib/wtinfo.html. Acesso em: 3 nov. 2026.',
'PAGE, M. J. et al. The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. BMJ, v. 372, art. n71, 2021. DOI: https://doi.org/10.1136/bmj.n71.',
'ZEITRÄG, Y.; FIGUEIRA, J. R.; PEREIRA, M. A. A web-based interactive decision support system for a multi-objective lot-sizing and production scheduling model. International Journal of Production Economics, v. 271, art. 109209, 2024. DOI: https://doi.org/10.1016/j.ijpe.2024.109209.'
]
for ref in refs:p(ref,'Referencia')
sec('APÊNDICE A — GUIA DE INSERÇÃO DOS RESULTADOS')
quadro('Quadro A1 — Relação entre saídas do código e campos do artigo',['Elemento','Arquivo de origem','Local'],[
 ('Tabela 1','TABELA_1_COMPARACAO_METODOS.csv','Seção 4.1'),
 ('Figura 1','FIGURA_1_COMPARACAO.png','Seção 4.1'),
 ('Tabela 2','TABELA_2_GANHO_HIBRIDO.csv','Seção 4.2'),
 ('Figura 2','FIGURA_2_GANHO_HIBRIDO.png','Seção 4.2'),
 ('Figura 3','FIGURA_3_CONVERGENCIA.png','Seção 4.2'),
 ('Tabela 3','TABELA_3_SENSIBILIDADE.csv','Seção 4.3'),
 ('Tabela 4','TABELA_4_TESTE_SINAIS.csv','Seção 4.4'),
 ('Figura 4','FIGURA_4_SENSIBILIDADE.png','Seção 4.3'),
 ('Parâmetros','manifesto_execucao.json','Seção 3.4 e descrição dos testes'),
 ('Matriz de decisão WSM','MATRIZ_DECISAO_MULTICRITERIO_WSM.csv','Evidência suplementar das contribuições dos critérios'),
 ('Estatística detalhada','comparacao_pareada.csv','Interpretação da Seção 4.2')],
 'Fonte: elaboração própria (2026). O script atualizar_artigo.py insere tabelas e figuras automaticamente.')
p('As figuras devem ser produzidas pelo próprio experimento, a partir dos dados públicos da OR-Library. Não são necessárias fotografias de fábrica nem imagens coletadas de terceiros. Se desejar inserir imagens adicionais, utilize apenas capturas autorais do ambiente de execução e identifique no texto o equipamento, o arquivo e a origem das informações. A representação visual do algoritmo também pode ser feita como diagrama autoral, sem reproduzir figuras protegidas de outros estudos.')
sec('APÊNDICE B — REPRODUTIBILIDADE')
p('O pacote suplementar inclui código-fonte Python, arquivos de execução para Windows, uma primeira instância oficial de demonstração, testes automatizados e orientações para obtenção dos conjuntos completos da OR-Library. Os arquivos originais dos três tamanhos são baixados automaticamente na primeira execução integral, e seus hashes ficam registrados em manifesto de execução. O modo piloto serve apenas para verificar se o projeto funciona; o artigo deve ser preenchido com resultados do modo completo.')
# Conferências editoriais adicionais constam também no README.
OUT.parent.mkdir(parents=True,exist_ok=True)
D.save(OUT)
print('Criado',OUT)
