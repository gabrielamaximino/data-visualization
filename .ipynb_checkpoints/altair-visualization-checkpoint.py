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

import altair as alt
import pandas as pd

df = pd.read_csv("./dataset/houses_to_rent_v2.csv")

# A base de dados escolhida possui informações acerca de imóveis para alugar no Brasil. De modo a ter uma visão geral da base e de suas especificações, os métodos head() e info() do pandas foi utilizado:

df.head()

df.info()

# Diante disso, nota-se que a base possui informações do imóvel, como área e número de quartos, e as taxas que compoem o valor total de aluguel. 

alt.data_transformers.disable_max_rows()

# Inicialmente, considera-se necessário ver a distribuição dos imóveis em relação às cidades. Para isso, um gráfico de barras simples foi elaborado.

alt.Chart(df).mark_bar().encode(
    alt.Y("city", scale=alt.Scale(zero=False), title="Cidade"),
    alt.X("count()", title="Imóveis"),
    tooltip="count()",
).properties(
    width=500,
    height=150,
)

# A partir do gráfico, nota-se que há imóveis registrados apenas em 5 cidades: Belo Horizonte, Campinas, Porto Alegre, Rio de Janeiro e São Paulo. Essa última, por sua vez, possui o maior número de imóveis registrados na base, com 5887 ocorrências.

# ## Hipóteses levantadas

# Diante da visão geral da base de dados, levantam-se alguns questionamentos. O primeiro deles é: **é possível notar uma diferença entre o preço do aluguel de apartamentos com características semelhantes entre as cidades?**

# Para responder a essa pergunta, vamos analisar a distribuição do preço nas diferentes cidades.

alt.Chart(df).mark_point().encode(
    alt.Y("city", title="Cidade"),
    alt.X("total (R$)", scale=alt.Scale(zero=False, type="log"), title="Aluguel total (R$)"),
    color="city",
    tooltip=[alt.Tooltip("total (R$)")]
).properties(
    width=700,
    height=300,    
).interactive()

# A partir do gráfico acima, verifica-se a existência de 5 _outliers_: 1 no Rio de Janeiro; 3 em São Paulo; e 1 em Belo Horizonte. Esses valores estão todos acima do último valor considerando coerente, que é de São Paulo (R$ 54.430). Para evitar problemas em análises futuras, faz-se necessário a retirada desses _outliers_. Isso é feito utilizando o próprio pandas:

df.drop(df[df["total (R$)"] > 55000].index, inplace=True)

# Feito isso, vamos verificar se a nova distribuição está de acordo:

alt.Chart(df).mark_point().encode(
    alt.Y("city", title="Cidade"),
    alt.X("total (R$)", scale=alt.Scale(zero=False, type="log"), title="Aluguel total (R$)"),
    color="city",
    tooltip=[alt.Tooltip("total (R$)")]
).properties(
    width=700,
    height=300,    
).interactive()

# Removido os _outliers_, vamos inicialmente analisar o preço médio dos apartamentos nas cidades, sem considerar ainda as características do imóvel.

alt.Chart(df, title="Preço médio de apartamentos nas cidades").mark_bar(opacity=.85).encode(
    alt.Y("city",title="Cidade"),
    alt.X("average(total (R$)):Q",scale=alt.Scale(zero=False), title="Preço médio"),
    alt.Color("city:N"),
).properties(
    width=300,
    height=150,
)

# Nota-se que, em média, os imóveis para alugar em SP são mais caros que nas demais cidades, e que Belo Horizonte e Rio de Janeiro possuem valores similares.

# Agora, para realizar a análise mais específica envolvendo características similares, vamos aplicar filtros.

dropdown_mobilia = alt.binding_select(options=[None, 'furnished', 'not furnished'], 
                                      labels=['Todos', 'Mobiliado', 'Não mobiliado'])
selecao_mobilia = alt.selection_single(fields=['furniture'],
                                       bind=dropdown_mobilia, 
                                        name="Selecao de")

dropdown_animal = alt.binding_select(options=[None, 'acept', 'not acept'], 
                                     labels=['Todos', 'Aceita', 'Não aceita'])
selecao_animal = alt.selection_single(fields=['animal'], 
                                      bind=dropdown_animal, 
                                      name='Selecao')

brush_area = alt.selection_interval(encodings=['x'], empty='all')

selecao_quarto, selecao_banheiro, selecao_vagas = alt.selection_multi(fields=['rooms']), alt.selection_multi(fields=['bathroom']), alt.selection_multi(fields=['parking spaces'])


seletor_area = alt.Chart(df).mark_bar(color='salmon', opacity=.5).encode(
    alt.X('area:Q', scale=alt.Scale(zero=False), title="Área"), 
).add_selection(
    brush_area
).properties(
    width=600
) # Arrumar isso para ficar até 5000

seletor_quarto = alt.Chart(df).mark_rect(
    stroke='black', strokeWidth=.2, color='salmon', opacity=.5
).encode(
    alt.X('rooms:N', scale=alt.Scale(zero=False), title="Número de quartos"), 
    color=alt.condition(selecao_quarto, alt.value('salmon'), alt.value('lightgray'))
).add_selection(selecao_quarto)

seletor_banheiro = alt.Chart(df).mark_rect(
    stroke='black', strokeWidth=.2, color='salmon', opacity=.5
).encode(
    alt.X('bathroom:N', scale=alt.Scale(zero=False), title="Número de banheiros"), 
    color=alt.condition(selecao_banheiro, alt.value('salmon'), alt.value('lightgray'))
).add_selection(selecao_banheiro)

seletor_vagas = alt.Chart(df).mark_rect(
    stroke='black', strokeWidth=.2, color='salmon', opacity=.5
).encode(
    alt.X('parking spaces:N', scale=alt.Scale(zero=False)), 
    color=alt.condition(selecao_vagas, alt.value('salmon'), alt.value('lightgray'))
).add_selection(selecao_vagas)

precos = list(df["total (R$)"].unique())

cidades = list(df["city"].unique())

scatterplot = alt.Chart(df).mark_point(size=150).encode(
    alt.X('total (R$)', scale=alt.Scale(zero=False, domain=(min(precos), max(precos))), title="Valor do aluguel"),
    alt.Y('city', title="Cidade"), 
    color='city:N',
    tooltip=[alt.Tooltip("city"),
             alt.Tooltip("area"), 
             alt.Tooltip("rooms"),
             alt.Tooltip("bathroom"), 
             alt.Tooltip("parking spaces"), 
             alt.Tooltip("animal"), 
             alt.Tooltip("furniture"), 
             alt.Tooltip("total (R$)")],
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
    width=750,
    height=300
).interactive()

scatter_media = alt.Chart(df).mark_rule(color='firebrick').encode(
     x='mean(total (R$)):Q',
     size=alt.SizeValue(3),
     tooltip='mean(total (R$))'
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
    width=750,
    height=300
)

(scatterplot + scatter_media) & seletor_area & (seletor_quarto | seletor_banheiro | seletor_vagas) 


# A partir da visualização criada, é possível escolher as características desejadas para verificar o preço entre as cidades. 

# Feito a primeira análise, a segunda análise deseja responder os seguintes questionamentos: **é possível identificar uma relação entre as variáveis com os preços? O que mais "influencia" no preço?**
#
# Para responder a essa pergunta, vamos verificar o gráfico de dispersão de modo a analisar se existe uma correlação entre as variáveis e o preço.

# Removendo as variáveis categóricas e a variável que deseja ser analisada (total)

lista = list(df.columns)
lista.remove('total (R$)')
lista.remove('animal')
lista.remove('furniture')
lista.remove('city')

hm = alt.Chart(df).mark_circle().encode(
    alt.X(alt.repeat("column"), type='quantitative'),
    alt.Y("total (R$)", type='quantitative', scale=alt.Scale(zero=False))
).properties(
    width=200,
    height=200
).repeat(
    column=lista[:3],
)

hm2 = alt.Chart(df).mark_circle().encode(
    alt.X(alt.repeat("column"), type='quantitative'),
    alt.Y("total (R$)", type='quantitative', scale=alt.Scale(zero=False))
).properties(
    width=200,
    height=200
).repeat(
    column=lista[3:6],
)

hm3 = alt.Chart(df).mark_circle().encode(
    alt.X(alt.repeat("column"), type='quantitative'),
    alt.Y("total (R$)", type='quantitative', scale=alt.Scale(zero=False))
).properties(
    width=200,
    height=200
).repeat(
    column=lista[6:],
)

hm & hm2 & hm3

# A partir dos gráficos de dispersão, é possível visualizar uma leve correlação do preço total com duas variáveis: a taxa de aluguel (_rent amount_) e o seguro de incêndio (_fire insurance_). Contudo, acredita-se que isso não é o bastante para responder a pergunta. Portanto, vamos calcular a correção entre as variáveis do banco de dados.

# A correlação é calculada usando o próprio método para _dataframes_ do pandas. O resultado é então organizado para ser armazenado em outro _dataframe_, de modo a plotar as descobertas.

cor_data = df.corr().stack().reset_index().rename(columns={0: 'correlation', 'level_0': 'variable', 'level_1': 'variable2'})
cor_data['correlation_label'] = cor_data['correlation'].map('{:.2f}'.format)  # Round to 2 decimal
cor_data.head()

# Agora, é necessário criar o _heatmap_ para visualizar as correlações:

base = alt.Chart(cor_data).encode(
    alt.X('variable2:O', title="Variável"),
    alt.Y('variable:O', title="Variável")    
)

# Text layer with correlation labels
# Colors are for easier readability
text = base.mark_text().encode(
    text='correlation_label',
    color=alt.condition(
        alt.datum.correlation > 0.5, 
        alt.value('white'),
        alt.value('black')
    )
)

# The correlation heatmap itself
cor_plot = base.mark_rect().encode(
    color='correlation:Q',
).properties(
    width=500,
    height=500,
)

cor_plot + text # The '+' means overlaying the text and rect layer

# A partir do _heatmap_ criado, é possível notar algumas correlações interessantes:
# - Há 92% de correlação entre a taxa de seguro de incêndio e o preço total do aluguel;
# - Há 96% de correlação entre o preço do aluguel sozinho e o preço total do aluguel;
# - Há 99% de correlação entre a taxa de seguro de incêndio e a taxa de aluguel (sem ser total).
#
# Sendo assim, é possível afirmar que há uma correlação significativa das variáveis *taxa de seguro de incêndio* e *preço do aluguel sozinho* com o preço total do aluguel dos imóveis.
