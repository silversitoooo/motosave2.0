```
# Modelo de Datos para Neo4j - MotoMatch

## Nodos

### User (Usuario)
- id: string (identificador único)
- experiencia: string (Principiante, Intermedio, Avanzado)
- uso_previsto: string (Ciudad, Paseo, Deportivo, Viajes, etc.)
- presupuesto: int (presupuesto en pesos)
- edad: int

### Moto
- id: string (identificador único)
- potencia: int (potencia en CV)
- peso: int (peso en kg)
- cilindrada: int (cilindrada en cc)
- tipo: string (Deportiva, Naked, Adventure, etc.)
- precio: int (precio en pesos)
- marca: string (nombre de la marca)
- modelo: string (nombre del modelo)
- imagen: string (URL de la imagen)

### Marca
- nombre: string (identificador único, nombre de la marca)

### Estilo
- nombre: string (identificador único, tipo de moto)

## Relaciones

### FRIEND (Usuario -> Usuario)
Representa una relación de amistad entre usuarios.
- Sin propiedades adicionales (la relación es bidireccional)

### RATED (Usuario -> Moto)
Representa una valoración de un usuario a una moto.
- rating: float (valoración del 1 al 5)
- timestamp: long (marca de tiempo)

### INTERACTED (Usuario -> Moto)
Representa una interacción del usuario con una moto.
- type: string (view, like, bookmark, compare)
- weight: float (peso de la interacción)
- timestamp: long (marca de tiempo)

### PREFIERE (Usuario -> [Estilo, Marca])
Representa una preferencia del usuario por un estilo o marca.
- valor: float (intensidad de la preferencia, entre 0 y 1)

### DE_MARCA (Moto -> Marca)
Indica la marca a la que pertenece una moto.
- Sin propiedades adicionales

### DE_ESTILO (Moto -> Estilo)
Indica el estilo al que pertenece una moto.
- Sin propiedades adicionales

## Ejemplo de Consultas

### Obtener recomendaciones basadas en amigos
```cypher
MATCH (u:User {id: 'user-id'})-[:FRIEND]->(amigo)-[r:RATED]->(m:Moto)
WHERE r.rating >= 4.0
RETURN m.id, m.modelo, m.marca, r.rating, amigo.id
ORDER BY r.rating DESC
LIMIT 5
```

### Obtener motos por estilo preferido
```cypher
MATCH (u:User {id: 'user-id'})-[p:PREFIERE]->(e:Estilo)<-[:DE_ESTILO]-(m:Moto)
RETURN m.id, m.modelo, m.marca, m.tipo, p.valor
ORDER BY p.valor DESC, m.precio ASC
```

### Obtener motos por rango de precios
```cypher
MATCH (u:User {id: 'user-id'})
MATCH (m:Moto)
WHERE m.precio <= u.presupuesto
RETURN m.id, m.modelo, m.marca, m.precio
ORDER BY m.precio DESC
```
```
