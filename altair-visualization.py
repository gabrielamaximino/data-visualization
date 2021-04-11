# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:nomarker
#     text_representation:
#       extension: .py
#       format_name: nomarker
#       format_version: '1.0'
#       jupytext_version: 1.7.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Visualização de dados - Altair 
#
# **Base: Brazilian Houses to Rent**
#
# Disciplina de Visualização da Informação - Universidade Federal do Pará - 10/04/2021.
#
# Aluna: Gabriela Souza Maximino - 201804940016
#
# **Observação**: algumas interações nos gráficos podem ser muito lentas devido à quantidade de registros da base (+10k).

import altair as alt
import pandas as pd

df = pd.read_csv("./dataset/houses_to_rent_v2.csv")

# A base de dados escolhida possui informações acerca de imóveis para alugar no Brasil. De modo a ter uma visão geral da base e de suas especificações, os métodos head() e info() do pandas foi utilizado:

df.head()

df.info()

# Diante disso, nota-se que a base possui informações do imóvel, como área e número de quartos, e as taxas que compoem o valor total de aluguel. 

alt.data_transformers.disable_max_rows()

# Inicialmente, considera-se necessário ver a distribuição dos imóveis em relação às cidades. Para isso, um gráfico de barras simples foi elaborado.

alt.Chart(df, title="Imóveis por cidade").mark_bar().encode(
    alt.Y("city", title="Cidade", sort=alt.EncodingSortField(op="count", order="ascending")),
    alt.X("count()", title="Número de imóveis", axis=alt.Axis(tickCount=5)),
    alt.Color("city:N", legend=alt.Legend(title="Cidade")),
    tooltip=[alt.Tooltip("count()", title="Número de imóveis")],
).properties(
    width=750,
    height=200,
)

# A partir do gráfico, nota-se que há imóveis registrados apenas em 5 cidades: Campinas, Porto Alegre, Belo Horizonte, Rio de Janeiro e São Paulo. Essa última, por sua vez, possui o maior número de imóveis registrados na base, com 5887 ocorrências.

# ## Questionamentos levantados

# Diante da visão geral da base de dados, levantam-se dois questionamentos. O primeiro deles é: **é possível notar uma diferença entre o preço do aluguel de imóveis com características semelhantes entre as cidades?**

# Para responder a essa pergunta, inicialmente vamos analisar a distribuição do preço nas diferentes cidades.

alt.Chart(df, title="Distribuição do valor de aluguel dos imóveis por cidade (com outliers)").mark_point(size=100).encode(
    alt.Y("city", title="Cidade", sort=alt.EncodingSortField(op="count", order="ascending")),
    alt.X("total (R$)", title="Aluguel total (R$) em escala logaritmica", scale=alt.Scale(type="log"), axis=alt.Axis(tickCount=5)),
    alt.Color("city:N", legend=alt.Legend(title="Cidade")),
    tooltip=[alt.Tooltip("total (R$)", title="Aluguel total (R$)")]
).properties(
    width=750,
    height=300,    
).interactive()

# A partir do gráfico acima, verifica-se a existência de alguns _outliers_. Para evitar problemas nas análises, é necessário realizar a retirada deles. Para tal, foi definido um valor de corte igual a 32000 para o preço do aluguel total. O corte foi feito utilizando o próprio pandas.

df.drop(df[df["total (R$)"] > 32000].index, inplace=True)

# Feito isso, vamos verificar se a nova distribuição está de acordo:

alt.Chart(df, title="Distribuição do valor de aluguel dos imóveis por cidade (sem outliers)").mark_point(size=100).encode(
    alt.Y("city", title="Cidade", sort=alt.EncodingSortField(op="count", order="ascending")),
    alt.X("total (R$)", title="Aluguel total (R$) em escala logaritmica", scale=alt.Scale(type="log"), axis=alt.Axis(tickCount=3)),
    alt.Color("city:N", legend=alt.Legend(title="Cidade")),
    tooltip=[alt.Tooltip("total (R$)", title="Aluguel total (R$)")]
).properties(
    width=750,
    height=300,    
).interactive()

# Removidos os _outliers_, vamos agora analisar o valor médio de aluguel dos imóveis nas cidades, sem considerar ainda as características do imóvel.

alt.Chart(df, title="Valor médio do aluguel de imóveis por cidade").mark_bar().encode(
    alt.Y("city", title="Cidade", sort=alt.EncodingSortField(field="total (R$)", op="average", order="ascending")),
    alt.X("average(total (R$)):Q", title="Preço médio de aluguel (R$)", axis=alt.Axis(tickCount=5)),
    alt.Color("city:N", legend=alt.Legend(title="Cidade")),
    tooltip=[alt.Tooltip("average(total (R$))", title="Preço médio do aluguel (R$)")],
).properties(
    width=750,
    height=200,
)

# Nota-se que, em média, os imóveis para alugar em SP são mais caros que nas demais cidades, enquanto que Porto Alegre possui os imóveis mais baratos. Além disso, nota-se que Belo Horizonte e Rio de Janeiro possuem valores bastante similares.

# Agora, para realizar a análise mais específica do preço do aluguel envolvendo imóveis com características similares, vamos aplicar filtros.

# Menus dropdown para selecionar os atributos Mobilia (furniture) e Animal (animal)

dropdown_mobilia = alt.binding_select(options=[None, 'furnished', 'not furnished'], 
                                      labels=['Todos', 'Mobiliado', 'Não mobiliado'])
selecao_mobilia = alt.selection_single(fields=['furniture'],
                                       bind=dropdown_mobilia, 
                                        name="Sobre a")

dropdown_animal = alt.binding_select(options=[None, 'acept', 'not acept'], 
                                     labels=['Todos', 'Aceita', 'Não aceita'])
selecao_animal = alt.selection_single(fields=['animal'], 
                                      bind=dropdown_animal, 
                                      name='Sobre')

# Chart para selecionar a Área desejada (area)

brush_area = alt.selection_interval(encodings=['x'])

seletor_area = alt.Chart(df).mark_point(size=200).encode(
    alt.X('area:Q', scale=alt.Scale(zero=False), title="Área", axis=alt.Axis(tickCount=10)), 
    color=alt.condition(brush_area, 'count()', alt.value('lightgray'), 
                        legend=alt.Legend(title="Número de imóveis", 
                                          direction="horizontal", 
                                          offset=90)),
    tooltip="area"
).add_selection(
    brush_area
).properties(
    width=600,
) 

seletor_area

# Nota-se que existem apenas 3 imóveis com área maior do que 5000. Nesse caso, vamos excluir esse imóveis para evitar que a barra de seleção de área fique desse modo. Para isso, passando o mouse sobre o último ponto antes de 5000, nota-se que o valor é 2000. Sendo assim, vamos adotar esse valor como corte.

df = df[df["area"] <= 2000]

# Atualizando o chart para selecionar a Área desejada (area)

brush_area = alt.selection_interval(encodings=['x'])

seletor_area = alt.Chart(df).mark_point(size=200).encode(
    alt.X('area:Q', scale=alt.Scale(zero=False), title="Área", axis=alt.Axis(tickCount=10)), 
    color=alt.condition(brush_area, 'count()', alt.value('lightgray'), 
                        legend=alt.Legend(title="Número de imóveis", 
                                          direction="horizontal", 
                                          offset=90)),
    tooltip="area"
).add_selection(
    brush_area
).properties(
    width=600,
) 

seletor_area

# Contudo, nota-se que o corte ainda não foi suficiente para evitar problemas. Sendo assim, vamos fazer um novo corte para eliminar as áreas que não possuem muitos imóveis. O valor de corte agora foi definido como 1100.

df = df[df["area"] <= 1100]

# Atualizando o chart para selecionar a Área desejada (area)

brush_area = alt.selection_interval(encodings=['x'])

seletor_area = alt.Chart(df).mark_point(size=200).encode(
    alt.X('area:Q', scale=alt.Scale(zero=False), title="Área", axis=alt.Axis(tickCount=10)), 
    color=alt.condition(brush_area, 'count()', alt.value('lightgray'), 
                        legend=alt.Legend(title="Número de imóveis", 
                                          direction="horizontal", 
                                          offset=90)),
    tooltip="area"
).add_selection(
    brush_area
).properties(
    width=600,
) 

seletor_area

# Com a barra de seleção de área ok, vamos apenas modificar a variável visual de ponto para barra para melhor visualização.

# Modificando a variável visual do chart melhor visualização (area)

brush_area = alt.selection_interval(encodings=['x'], empty='all')

seletor_area = alt.Chart(df).mark_bar(
    stroke='black', strokeWidth=.2).encode(
    alt.X('area:Q', scale=alt.Scale(zero=False), title="Área", bin=alt.Bin(maxbins=25)),
    alt.Color("count()", legend=alt.Legend(title="Número de imóveis",
                                          direction="horizontal",
                                          offset=140)),
    tooltip=[alt.Tooltip("count()", title="Número de imóveis")],
).add_selection(
    brush_area
).properties(
    width=600,
) 


seletor_area

# Chart para selecionar o número de quartos (rooms)

selecao_quarto = alt.selection_multi(fields=['rooms'])

seletor_quarto = alt.Chart(df).mark_rect(
    stroke='black', strokeWidth=.2
).encode(
    alt.X('rooms:N', scale=alt.Scale(zero=False), title="Número de quartos"), 
    color=alt.condition(selecao_quarto, 'count()', alt.value('lightgray')),
    tooltip=[alt.Tooltip("count()", title="Número de imóveis")]
).add_selection(selecao_quarto)

# Chart para selecionar o número de banheiros (bathroom)

selecao_banheiro = alt.selection_multi(fields=['bathroom'])

seletor_banheiro = alt.Chart(df).mark_rect(
    stroke='black', strokeWidth=.2
).encode(
    alt.X('bathroom:N', scale=alt.Scale(zero=False), title="Número de banheiros"), 
    color=alt.condition(selecao_banheiro, 'count()', alt.value('lightgray'), legend=alt.Legend(title="Número de imóveis", direction="horizontal", offset=90)),
    tooltip=[alt.Tooltip("count()", title="Número de imóveis")]
).add_selection(selecao_banheiro)

# Chart para selecionar o número de vagas (parking spaces)

selecao_vagas = alt.selection_multi(fields=['parking spaces'])

seletor_vagas = alt.Chart(df).mark_rect(
    stroke='black', strokeWidth=.2
).encode(
    alt.X('parking spaces:N', scale=alt.Scale(zero=False), title="Número de vagas de garagem"), 
    color=alt.condition(selecao_vagas, 'count()', alt.value('lightgray')),
    tooltip=[alt.Tooltip("count()", title="Número de imóveis")]
).add_selection(selecao_vagas)

# Lista com os preços e as cidades para fixar o domínio do scatterplot

precos = list(df["total (R$)"].unique())
cidades = list(df["city"].unique())

cidades.sort()

# Scatterplot que será atualizado de acordo com os filtros

scatterplot = alt.Chart(df, title="Distribuição do valor do aluguel por cidade com base nas características").mark_point(size=150).encode(
    alt.X('total (R$)', scale=alt.Scale(zero=False, domain=(min(precos), max(precos))), title="Valor do aluguel"),
    alt.Y('city', title="Cidade", scale=alt.Scale(domain=cidades)), 
    alt.Color("city:N", legend=alt.Legend(title="Cidade")),
    tooltip=[alt.Tooltip("city", title="Cidade"),
             alt.Tooltip("area", title="Área"), 
             alt.Tooltip("rooms", title="Quartos"),
             alt.Tooltip("bathroom", title="Banheiros"), 
             alt.Tooltip("parking spaces", title="Vagas de garagem"), 
             alt.Tooltip("animal", title="Animais"), 
             alt.Tooltip("furniture", title="Mobília"), 
             alt.Tooltip("total (R$)", title="Aluguel (R$)")],
).add_selection(
    selecao_mobilia, 
    selecao_animal
).transform_filter(
    selecao_mobilia
).transform_filter(
    selecao_animal
).transform_filter(
    selecao_quarto
).transform_filter(
     selecao_banheiro
).transform_filter(
     selecao_vagas
).transform_filter(
     brush_area
).properties(
    width=800,
    height=350
).interactive()

scatter_media = alt.Chart(df).mark_rule(color='firebrick').encode(
     alt.X('mean(total (R$)):Q'),
     size=alt.SizeValue(2),
).transform_filter(
     selecao_mobilia
).transform_filter(
    selecao_animal
).transform_filter(
    selecao_quarto
).transform_filter(
    selecao_banheiro
).transform_filter(
    selecao_vagas
).transform_filter(
    brush_area
).properties(
    width=800,
    height=350
)

(scatterplot + scatter_media) & seletor_area & (seletor_quarto | seletor_banheiro | seletor_vagas)


# A partir da visualização criada, é possível escolher as características desejadas para verificar o preço entre as cidades. O seletor da área é baseado em intervalo, enquanto que o seletor do número de quartos, banheiros e garagens é um seletor de múltipla escolha. Sendo assim, é possivel apertar _shift_ e selecionar mais de um elemento neles.

# Como resposta para a primeira pergunta, é possível observar no gráfico que, mesmo possuindo características semelhantes, os preços costumam variar entre as cidades. Selecionando, por exemplo, um imóvel com área entre 0 a 100, com 3 quartos, 2 banheiros e 1 vaga de garagem, que aceita animais e que não é mobiliado, nota-se que Rio de Janeiro e São Paulo possuem imóveis com valores acima da média (indicada pela linha vermelha), enquanto Campinas, Belo Horizonte e Porto Alegre possuem imóveis com aluguéis mais baratos. Contudo, BH apresenta 2 imóveis que são bem mais caros que o resto dos imóveis das cidades.

# Respondida a primeira pergunta, o segundo questionamento é feito: **é possível identificar uma relação entre as variáveis e o preço total do aluguel? O que mais "influencia" nesse valor?**
#
# Para responder a essa pergunta, vamos elaborar gráficos de dispersão com _brushing_ global de modo a analisar se existe uma correlação entre as variáveis e o preço.

# Removendo as variáveis categóricas e a variável que deseja ser analisada (total)

colunas = list(df.columns)
colunas.remove('total (R$)')
colunas.remove('animal')
colunas.remove('furniture')
colunas.remove('city')

brush = alt.selection_interval(
    resolve='global' 
)

# Primeira linha de gráficos

graficos1 = alt.Chart(df).mark_circle().add_selection(
    brush
).encode(
    alt.X(alt.repeat("column"), type='quantitative'),
    alt.Y("total (R$)", type='quantitative', scale=alt.Scale(zero=False)),
    color=alt.condition(brush, alt.value("steelblue"),alt.value("darkgrey")),
    opacity=alt.condition(brush, alt.value(.8),alt.value(.1))
).properties(
    width=200,
    height=200
).repeat(
    column=colunas[:3],
)

# Segunda linha de gráficos

graficos2 = alt.Chart(df).mark_circle().add_selection(
    brush
).encode(
    alt.X(alt.repeat("column"), type='quantitative'),
    alt.Y("total (R$)", type='quantitative', scale=alt.Scale(zero=False)),
    color=alt.condition(brush, alt.value("steelblue"),alt.value("darkgrey")),
    opacity=alt.condition(brush, alt.value(.8),alt.value(.1))
).properties(
    width=200,
    height=200
).repeat(
    column=colunas[3:6],
)

# Terceira linha de gráficos

graficos3 = alt.Chart(df).mark_circle().add_selection(
    brush
).encode(
    alt.X(alt.repeat("column"), type='quantitative'),
    alt.Y("total (R$)", type='quantitative', scale=alt.Scale(zero=False)),
    color=alt.condition(brush, alt.value("steelblue"),alt.value("darkgrey")),
    opacity=alt.condition(brush, alt.value(.8),alt.value(.1))
).properties(
    width=200,
    height=200
).repeat(
    column=colunas[6:],
)

graficos1 & graficos2 & graficos3

# A partir dos gráficos de dispersão, é possível visualizar uma leve correlação do preço total com duas variáveis: a taxa de aluguel (_rent amount_) e o seguro de incêndio (_fire insurance_). Contudo, acredita-se que isso ainda não é o bastante para responder a pergunta. Portanto, vamos calcular a correção entre as variáveis do banco de dados.

# A correlação é calculada usando o próprio método para _dataframe_ do pandas, o .corr(). O resultado é então organizado para ser armazenado em outro _dataframe_, de modo a plotar as descobertas.

dados_correlacionados = df.corr().stack().reset_index().rename(columns={0: 'correlacao', 'level_0': 'variavel1', 'level_1': 'variavel2'})
dados_correlacionados['label_correlacao'] = dados_correlacionados['correlacao'].map('{:.2f}'.format)  # Arredondando
dados_correlacionados.head()

# Agora, é necessário criar um _heatmap_ para visualizar melhor as correlações:

# Chart base
base = alt.Chart(dados_correlacionados).encode(
    alt.X('variavel1:O', title="Variável A"),
    alt.Y('variavel2:O', title="Variável B")    
)

# Inserir camada de texto no chart base
text = base.mark_text().encode(
    text='label_correlacao',
    color=alt.condition(
        alt.datum.correlacao > 0.5, 
        alt.value('white'),
        alt.value('black'))
)

# Heatmap
heatmap = base.mark_rect().encode(
    alt.Color("correlacao:Q", legend=alt.Legend(title="Correlação"))
).properties(
    width=500,
    height=500,
)

heatmap + text 

# A partir do _heatmap_ criado, é possível notar algumas correlações interessantes:
# - Há 93% de correlação entre a taxa de seguro de incêndio (_fire insurance_) e o preço total do aluguel;
# - Há 96% de correlação entre o preço do aluguel sozinho (_rent amount_) e o preço total do aluguel;
# - Há 99% de correlação entre a taxa de seguro de incêndio (_fire insurance_) e a taxa de aluguel (sem ser total) (_rent amount_).
#
# Diante disso, é possível afirmar que há uma correlação significativa das variáveis *taxa de seguro de incêndio* e *preço do aluguel sozinho* com o preço total do aluguel dos imóveis. Portanto, essas são as variáveis que mais "influenciam" no preço total do aluguel dos imóveis.
