# Guia prático: SQL e NoSQL

## Escolha o modelo pelos requisitos

| Tecnologia | Modelo | Adequada quando | Atenção |
|---|---|---|---|
| PostgreSQL | Relacional, SQL | Transações, relações, constraints, relatórios | Modelar relações e índices conforme consultas reais |
| MySQL | Relacional, SQL | Aplicações transacionais e ecossistemas que já o operam | Validar diferenças de SQL, isolamento e recursos entre versões |
| MongoDB | Documentos BSON | Registros agregados acessados juntos e esquema evolutivo | Evitar documentos/arrays sem limite e referências excessivas |

Não existe vencedor universal. Decida com base em consistência, consultas,
volume, latência, operação, competências do time e custo de migração. SQL e
NoSQL podem coexistir, mas cada sistema adicional cria obrigações de backup,
observabilidade, segurança e recuperação.

## PostgreSQL e MySQL: SQL essencial

Supondo `users(id, email)` e `events(id, user_id, severity, created_at)`:

```sql
-- JOIN relaciona a ocorrência ao proprietário; o filtro evita cruzar tenants.
SELECT u.email, e.severity, e.created_at
FROM users AS u
JOIN events AS e ON e.user_id = u.id
WHERE u.id = :user_id
  AND e.created_at >= :since
ORDER BY e.created_at DESC
LIMIT :page_size;
```

```sql
-- GROUP BY produz uma linha por severidade; COUNT agrega eventos de cada grupo.
SELECT e.severity, COUNT(*) AS event_count
FROM events AS e
WHERE e.user_id = :user_id
  AND e.created_at >= :since
GROUP BY e.severity
ORDER BY event_count DESC;
```

Funções agregadoras frequentes incluem `COUNT`, `SUM`, `AVG`, `MIN` e `MAX`.
Use parâmetros vinculados (`:user_id`) em vez de concatenar entrada do usuário
em SQL; isso evita injeção e melhora a reutilização de planos. `WHERE` filtra
linhas antes da agregação; `HAVING` filtra os grupos depois do `GROUP BY`.

### Índices B-Tree e Hash

- **B-Tree:** índice padrão apropriado para igualdade e intervalos (`=`, `<`,
  `>`, `BETWEEN`), ordenação e prefixos úteis. Um índice `(user_id,
  created_at)` pode atender consultas que filtram pelo primeiro campo e
  ordenam/façam intervalo pelo segundo.
- **Hash:** otimizado para igualdade exata em implementações que o suportam;
  não resolve ordenação nem intervalos. B-Tree tende a ser a escolha geral.
- Índices aceleram leitura seletiva, mas ocupam espaço e aumentam o custo de
  `INSERT`/`UPDATE`/`DELETE`. Meça planos (`EXPLAIN`, `EXPLAIN ANALYZE`) com
  dados representativos. Evite indexar toda coluna sem evidência.
- Índices compostos respeitam ordem das colunas. Índices separados de
  `severity` e `created_at` podem ajudar filtros isolados; o índice composto
  por usuário e data favorece consultas tenant-scoped do projeto.

## MongoDB: documentos e agregação

Um documento de evento pode ser armazenado como:

```javascript
{
  userId: 42,
  severity: "ERROR",
  message: "database timeout",
  createdAt: ISODate("2026-01-15T12:30:00Z")
}
```

Agregação por usuário e severidade:

```javascript
db.events.aggregate([
  { $match: { userId: 42, createdAt: { $gte: ISODate("2026-01-01T00:00:00Z") } } },
  { $group: { _id: "$severity", eventCount: { $sum: 1 } } },
  { $sort: { eventCount: -1 } }
]);
```

Um índice de consulta pode ser:

```javascript
db.events.createIndex({ userId: 1, createdAt: -1 });
```

No MongoDB, `$match` reduz os documentos que entram nos estágios seguintes;
`$group` agrega e `$sum: 1` conta documentos. Coloque filtros seletivos cedo
no pipeline. `$lookup` pode realizar junções, mas modelagem por agregados e
duplicação controlada de dados são opções comuns; avalie consistência e custos.
Use validação de schema e imponha limites a arrays e tamanho de documento.

## Laboratório sugerido

1. Execute `EXPLAIN ANALYZE` na consulta analítica antes e depois do índice.
2. Compare tempo de leitura e custo de escrita em volume de teste.
3. Repita o relatório com pipeline MongoDB e compare o formato do resultado.
4. Documente os trade-offs; não use dados pessoais em ambientes de estudo.
