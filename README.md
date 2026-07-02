
<div align="justify">

# Detector de Anti-patterns de Performance com AST

## 1. Visão Geral

Este projeto implementa um analisador estático de código Python utilizando o módulo `ast` da biblioteca padrão. O objetivo é identificar automaticamente padrões de código conhecidos por degradar o desempenho, principalmente quando executados dentro de loops.

Ao invés de executar o programa, o analisador percorre a Árvore Sintática Abstrata (Abstract Syntax Tree - AST), identificando chamadas de funções consideradas problemáticas e gerando um relatório em Markdown contendo os problemas encontrados, sua causa e sugestões de otimização.

A proposta é semelhante ao funcionamento de ferramentas como linters e analisadores estáticos, porém especializada em detectar gargalos de performance.

---

## 2. Objetivo

O projeto busca automatizar a identificação de operações frequentemente responsáveis por aumentar significativamente o tempo de execução de programas que manipulam grandes volumes de dados.

Entre os casos analisados estão operações envolvendo:

- Pandas
- Polars
- PySpark
- Estruturas nativas do Python

O foco principal está em detectar chamadas realizadas dentro de laços (`for` e `while`), situação em que diversos métodos passam a possuir impacto quadrático ou elevado.

---

## 3. Arquitetura

O projeto é composto por quatro partes principais:

```
script.py
│
├── O2Detector
│      Classe responsável pela análise da AST
│
├── gerar_relatorio()
│      Gera o relatório em Markdown
│
├── analisar_arquivo()
│      Faz o parsing do código
│
└── main
       Recebe o arquivo informado na linha de comando
```

Todo o fluxo acontece em memória, sem executar nenhuma linha do código analisado.

---

# 4. Funcionamento

O processo ocorre em cinco etapas.

## Etapa 1

O arquivo Python é aberto.

```python
with open(path, 'r', encoding='utf-8') as f:
```

---

## Etapa 2

O código é convertido em uma AST.

```python
tree = ast.parse(f.read())
```

A AST representa o programa como uma árvore de objetos Python.

Exemplo:

Código

```python
for i in lista:
    df.append(i)
```

Transforma-se aproximadamente em:

```
Module
 └── For
      └── Call
           └── Attribute
```

---

## Etapa 3

O Visitor percorre toda a árvore.

Sempre que encontra um nó do tipo:

- FunctionDef
- For
- While
- Call

executa uma lógica específica.

---

## Etapa 4

Caso uma chamada de função esteja dentro de um loop, ela é comparada com o banco de regras.

Exemplo:

```python
df.append(...)
```

gera

```
append
```

que é comparado contra o dicionário:

```python
self.regras
```

---

## Etapa 5

Se houver correspondência, é criado um registro contendo:

- linha
- função
- problema
- solução
- patch sugerido

Ao final, todos os registros são exportados para um arquivo Markdown.

---

# 5. Estrutura da Classe Principal

Toda a lógica está concentrada na classe

```python
class O2Detector(ast.NodeVisitor)
```

Ela herda de `ast.NodeVisitor`, permitindo visitar automaticamente cada nó da árvore sintática.

Os principais atributos são:

| Atributo | Finalidade |
|-----------|------------|
| loop_depth | Indica se o analisador está dentro de um loop |
| current_func | Nome da função atualmente visitada |
| regras | Base de conhecimento dos anti-patterns |
| viloes | Lista de problemas encontrados |

---

# 6. Controle da Profundidade dos Loops

O detector mantém um contador chamado:

```python
self.loop_depth
```

Sempre que encontra:

```python
for
```

ou

```python
while
```

incrementa esse contador.

Ao sair do bloco, decrementa.

Dessa forma é possível saber se qualquer chamada de função está sendo executada dentro de um loop.

Essa abordagem também funciona para loops aninhados.

---

# 7. Identificação das Chamadas

Sempre que um nó `Call` é encontrado, o método

```python
visit_Call()
```

é executado.

Primeiro verifica:

```python
if self.loop_depth > 0:
```

Somente chamadas dentro de loops são analisadas.

Depois obtém o nome da função.

Exemplo:

```python
df.sort_values(...)
```

retorna

```
sort_values
```

Esse nome é comparado com todas as regras cadastradas.

---

# 8. Base de Regras

O detector utiliza um grande dicionário organizado por biblioteca.

Cada regra possui quatro informações:

- Nome do anti-pattern
- Motivo
- Solução
- Patch sugerido

Exemplo:

```python
'append':
(
    'df.append em loop',
    'Cópia cara.',
    'Use lista + pd.concat().',
    'df_list.append(df); pd.concat(df_list)'
)
```

Essa estrutura facilita a expansão do projeto.

Adicionar novas regras normalmente exige apenas incluir novas entradas no dicionário.

---

# 9. Bibliotecas Suportadas

Atualmente o detector identifica problemas relacionados a:

## Pandas

Detecta operações como:

- append
- iterrows
- apply
- sort_values

---

## Polars

Detecta:

- concat
- filter
- iter_rows
- with_columns

---

## PySpark

Detecta:

- count
- collect
- join
- withColumn
- udf
- toPandas

---

## Python

Detecta atualmente:

- list.insert(0)

Novas estruturas podem ser adicionadas facilmente.

---

# 10. Geração do Relatório

Ao final da análise é criado automaticamente o arquivo:

```
relatorio_performance.md
```

Cada ocorrência encontrada possui:

- linha
- tipo do problema
- explicação
- solução
- exemplo de correção

Exemplo:

```markdown
### Linha 42 | Pandas: df.append em loop

- Problema:
  Cópia cara.

- Solução:
  Use lista + pd.concat().

- Patch sugerido:
  df_list.append(df)
```

O relatório pode ser versionado juntamente com o projeto ou utilizado em pipelines de integração contínua (CI).

---

# 11. Complexidade

A AST é percorrida apenas uma vez.

Assim, considerando:

- **N** = número de nós da árvore

temos:

| Operação | Complexidade |
|----------|--------------|
| Parsing | O(N) |
| Percorrer AST | O(N) |
| Busca nas regras | O(1) |
| Complexidade total | **O(N)** |

Mesmo projetos grandes podem ser analisados rapidamente.

---

# 12. Possíveis Melhorias

O projeto pode evoluir para detectar padrões mais sofisticados, como:

- loops aninhados (potencial O(n²))
- concatenação de listas usando `+`
- concatenação de strings em loops
- chamadas repetidas a banco de dados
- chamadas HTTP dentro de loops
- escrita repetida em arquivos
- criação excessiva de objetos
- uso ineficiente de NumPy
- detecção automática de complexidade assintótica
- geração de sugestões automáticas de refatoração

Também é possível integrar o analisador com:

- GitHub Actions
- GitLab CI
- pre-commit hooks
- VSCode
- PyCharm

---

# 13. Como Executar

## Clone ou copie o projeto

Estrutura recomendada:

```
performance-detector/

├── detector.py
├── seu_script.py
└── README.md
```

---

## Execute o analisador

Analisando um arquivo específico:

```bash
python detector.py meu_codigo.py
```

Ou, caso nenhum arquivo seja informado:

```bash
python detector.py
```

Nesse caso será analisado automaticamente:

```text
seu_script.py
```

---

## Saída esperada

Se forem encontrados problemas:

```text
✅ Análise completa: 8 vilões detectados.
Veja 'relatorio_performance.md'.
```

Caso o código esteja limpo:

```text
✅ Código limpo! Nenhuma violação detectada.
```

Após a execução será criado o arquivo:

```
relatorio_performance.md
```

contendo todas as ocorrências detectadas.

---

# 14. Conclusão

Este projeto demonstra como utilizar a API `ast` do Python para construir um analisador estático voltado à identificação de gargalos de desempenho.

Embora relativamente compacto, ele implementa conceitos importantes de compiladores e análise estática, como o percurso de árvores sintáticas, inspeção estrutural de código e aplicação de regras semânticas.

Além de servir como ferramenta prática para inspeção de código, o projeto constitui um excelente exemplo de portfólio por combinar análise estática, estruturas de dados, automação e boas práticas de engenharia de software.

</div>
````

