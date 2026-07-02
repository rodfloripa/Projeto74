# 🚀 Relatório de Performance

### 📍 Linha 9 | Geral: list.insert(0)
- **Problema:** Move todos os elementos.
- **Solução:** Use collections.deque.
- **Patch:** `from collections import deque`

### 📍 Linha 14 | Geral: Concatenação += em loop
- **Problema:** O(n²) por realocação.
- **Solução:** Use "".join() ou list.append().
- **Patch:** `list.append(item)`

### 📍 Linha 24 | Pandas: .sort_values()
- **Problema:** Ordenação repetida.
- **Solução:** Ordene antes do loop.
- **Patch:** `df.sort_values(by="col")`

### 📍 Linha 25 | Pandas: .append()
- **Problema:** Cópia cara do DF.
- **Solução:** Use lista + pd.concat().
- **Patch:** `pd.concat([df1, df2])`

### 📍 Linha 29 | Polars: .vstack()
- **Problema:** Realoção cara.
- **Solução:** Use Expression API.
- **Patch:** `pl.concat([df1, df2])`

### 📍 Linha 30 | Polars: .filter()
- **Problema:** Perda de Lazy Eval.
- **Solução:** Use Joins/GroupBy.
- **Patch:** `df.filter(...)`

### 📍 Linha 34 | Spark: .count()
- **Problema:** Action cara.
- **Solução:** Calcule 1x.
- **Patch:** `df.agg(count("*"))`

### 📍 Linha 35 | Spark: .withColumn()
- **Problema:** DAG ineficiente.
- **Solução:** Use .select().
- **Patch:** `df.select(col("a"), col("b"))`

