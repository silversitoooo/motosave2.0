"""
Funciones de recomendación para motosave, independientes de la lógica de las rutas
"""
from app.algoritmo.label_propagation import MotoLabelPropagation

def get_label_propagation_recommendations(user_id, db_session, top_n=5):
    """
    Genera recomendaciones usando el algoritmo de propagación de etiquetas.
    
    Args:
        user_id: ID del usuario para el que se generan recomendaciones
        db_session: Sesión de Neo4j
        top_n: Número de recomendaciones a generar
        
    Returns:
        list: Lista de diccionarios con recomendaciones {moto_id, marca, modelo, score}
    """
    try:
        # 1. Obtener amigos del usuario
        friends_result = db_session.run("""
            MATCH (u:User {id: $user_id})-[:FRIEND_OF]-(f:User)
            RETURN f.id as friend_id
        """, user_id=user_id)
        
        friend_ids = [record["friend_id"] for record in friends_result]
        
        # 2. Obtener interacciones del usuario y sus amigos
        interactions_result = db_session.run("""
            MATCH (u:User)-[r:INTERACTED {type: 'like'}]->(m:Moto)
            WHERE u.id IN [$user_id] + $friend_ids
            RETURN u.id as user_id, m.id as moto_id,
                   m.marca as marca, m.modelo as modelo, r.weight as weight
        """, user_id=user_id, friend_ids=friend_ids)
        
        interactions = [dict(record) for record in interactions_result]
        
        # 3. Generar recomendaciones con label propagation
        label_propagation = MotoLabelPropagation()
        
        # Inicializar y obtener recomendaciones
        recommendations = []
        if interactions:
            recommendations = label_propagation.initialize_from_interactions(interactions).get_recommendations(user_id, top_n)
        
        # 4. NUEVO PASO: Si no hay suficientes recomendaciones, obtener motos adicionales
        if len(recommendations) < top_n:
            # Obtener motos que el usuario no ha valorado aún
            additional_motos_result = db_session.run("""
                // Encuentra motos que el usuario no ha valorado
                MATCH (m:Moto)
                WHERE NOT EXISTS {
                    MATCH (u:User {id: $user_id})-[:INTERACTED]->(m)
                }
                RETURN m.id as moto_id, m.marca as marca, m.modelo as modelo,
                       m.cilindrada as cilindrada, m.potencia as potencia,
                       m.image_url as image_url
                // Ordenar por algún criterio como popularidad o novedades
                ORDER BY m.created_at DESC
                LIMIT $limit
            """, user_id=user_id, limit=top_n-len(recommendations))
            
            for record in additional_motos_result:
                moto_dict = dict(record)
                recommendations.append({
                    "moto_id": moto_dict["moto_id"],
                    "score": 0.5,  # Puntuación neutra para motos sin valoración social
                    "marca": moto_dict["marca"],
                    "modelo": moto_dict["modelo"],
                    "image_url": moto_dict.get("image_url", ""),
                    "cilindrada": moto_dict.get("cilindrada", ""),
                    "potencia": moto_dict.get("potencia", ""),
                    "source": "catalog"  # Indicar que viene del catálogo, no de propagación
                })
        
        # 5. Enriquecer recomendaciones con detalles adicionales si es necesario
        enriched_recommendations = []
        for rec in recommendations:
            # Si la recomendación ya tiene marca y modelo, no es necesario enriquecerla
            if "marca" in rec and "modelo" in rec:
                enriched_recommendations.append(rec)
                continue
                
            # Para recomendaciones que solo tienen moto_id y score, obtener detalles
            moto_result = db_session.run("""
                MATCH (m:Moto {id: $moto_id})
                RETURN m.marca as marca, m.modelo as modelo, m.cilindrada as cilindrada,
                      m.potencia as potencia, m.image_url as image_url
            """, moto_id=rec["moto_id"])
            
            moto_record = moto_result.single()
            if moto_record:
                rec.update(dict(moto_record))
                enriched_recommendations.append(rec)
        
        return enriched_recommendations
        
    except Exception as e:
        import logging
        logging.error(f"Error al generar recomendaciones con label propagation para {user_id}: {str(e)}")
        return []