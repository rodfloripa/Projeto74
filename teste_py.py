import pandas as pd
import polars as pl
from pyspark.sql import SparkSession

def processamento_ineficiente(lista_dados, df_pandas, df_polars, spark_df):
    # 1. Vilão: list.insert(0) em loop
    lista = []
    for i in range(100):
        lista.insert(0, i)

    # 2. Vilão: string += string em loop
    s = ""
    for i in range(100):
        s += str(i)

    # 3. Vilão: "in lista" em loop (lookup ineficiente)
    lista_busca = [1, 2, 3, 4, 5]
    for i in range(100):
        if i in lista_busca:
            print("Encontrado")

    # 4. Vilão: Pandas append/sort em loop
    for i in range(10):
        df_pandas.sort_values('col')
        df_pandas.append({'a': 1}, ignore_index=True)

    # 5. Vilão: Polars vstack/filter em loop
    for i in range(10):
        df_polars.vstack(df_polars)
        df_polars.filter(pl.col("a") == i)

    # 6. Vilão: Spark actions em loop
    for i in range(10):
        spark_df.count()
        spark_df.withColumn("nova", pl.lit(1))

# Apenas para evitar erros de execução se rodado diretamente
if __name__ == "__main__":
    print("Script de teste de carga para o O2Detector.")