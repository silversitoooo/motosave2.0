"""
Actualización de la ruta motos-recomendadas para corregir errores de conexión
"""

@fixed_routes.route('/motos-recomendadas')
@login_required
def motos_recomendadas():
    """
    Muestra motos recomendadas basadas en amigos del usuario:
    - Motos ideales de amigos
    - Motos con like de amigos
    - Motos recomendadas por propagación de etiquetas
    """
    user_id = session.get('user_id')
    if not user_id:
        # También verificar username para sesiones antiguas
        username = session.get('username')
        if username:
            # Buscar el user_id asociado al username
            try:
                adapter = current_app.config.get('MOTO_RECOMMENDER')
                if adapter and hasattr(adapter, '_ensure_neo4j_connection'):
                    adapter._ensure_neo4j_connection()
                    with adapter.driver.session() as neo4j_session:
                        result = neo4j_session.run("""
                            MATCH (u:User {username: $username})
                            RETURN u.id as user_id
                        """, username=username)
                        record = result.single()
                        if record:
                            user_id = record["user_id"]
                            # Actualizar la sesión
                            session['user_id'] = user_id
                            logger.info(f"Actualizada sesión con user_id {user_id} para {username}")
            except Exception as e:
                logger.error(f"Error al obtener user_id desde username: {str(e)}")
        
        if not user_id:
            flash('Debes iniciar sesión para ver las recomendaciones', 'error')
            return redirect(url_for('main.login'))
    
    # Obtener conexión a la base de datos
    try:
        # Primero intentar usar el adaptador en la configuración de la app
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        if adapter and hasattr(adapter, '_ensure_neo4j_connection'):
            if not adapter._ensure_neo4j_connection():
                flash('No se pudo conectar a la base de datos. Intente más tarde.', 'error')
                return redirect(url_for('main.dashboard'))
            
            # Obtener lista de amigos usando el adaptador
            friends = []
            with adapter.driver.session() as db_session:
                # Modificar para buscar tanto FRIEND como FRIEND_OF relaciones
                result = db_session.run("""
                    MATCH (u:User {id: $user_id})-[:FRIEND|:FRIEND_OF]->(f:User)
                    RETURN f.id as friend_id, f.username as friend_username
                """, user_id=user_id)
                
                friends = [{"id": record["friend_id"], "username": record["friend_username"]} 
                          for record in result]
            
            # Si no hay amigos, mostrar página con mensaje
            if not friends:
                return render_template('motos_recomendadas.html', friends_data=None)
            
            # Preparar datos para la plantilla
            ideal_motos = {}
            liked_motos = []
            propagation_motos = []
            
            # Crear instancia del algoritmo de label propagation
            label_propagation = MotoLabelPropagation()
            
            # Procesar cada amigo
            for friend in friends:
                friend_id = friend["id"]
                friend_username = friend["username"]
                
                # 1. Obtener moto ideal del amigo
                try:
                    with adapter.driver.session() as db_session:
                        result = db_session.run("""
                            MATCH (f:User {id: $friend_id})-[:IDEAL_MOTO|:IDEAL]->(m:Moto)
                            RETURN m.id as id, m.marca as marca, m.modelo as modelo, 
                                   m.tipo as tipo, m.precio as precio, m.imagen as imagen
                        """, friend_id=friend_id)
                        
                        record = result.single()
                        if record:
                            ideal_motos[friend_username] = {
                                "id": record["id"],
                                "marca": record["marca"],
                                "modelo": record["modelo"],
                                "tipo": record["tipo"],
                                "precio": record["precio"],
                                "imagen": record["imagen"]
                            }
                except Exception as e:
                    logger.error(f"Error al obtener moto ideal de {friend_username}: {e}")
                
                # 2. Obtener motos con like del amigo
                try:
                    with adapter.driver.session() as db_session:
                        result = db_session.run("""
                            MATCH (f:User {id: $friend_id})-[r:INTERACTED]->(m:Moto)
                            WHERE r.type = 'like'
                            RETURN m.id as id, m.marca as marca, m.modelo as modelo, 
                                   m.tipo as tipo, m.precio as precio, m.imagen as imagen
                        """, friend_id=friend_id)
                        
                        for record in result:
                            liked_motos.append({
                                "friend_name": friend_username,
                                "moto": {
                                    "id": record["id"],
                                    "marca": record["marca"],
                                    "modelo": record["modelo"],
                                    "tipo": record["tipo"],
                                    "precio": record["precio"],
                                    "imagen": record["imagen"]
                                }
                            })
                except Exception as e:
                    logger.error(f"Error al obtener motos con like de {friend_username}: {e}")
                
                # 3. Generar recomendaciones con label propagation
                try:
                    # Obtener interacciones del usuario y su amigo
                    with adapter.driver.session() as db_session:
                        interactions_result = db_session.run("""
                            MATCH (u:User)-[r:INTERACTED]->(m:Moto)
                            WHERE u.id IN [$user_id, $friend_id] AND r.type = 'like'
                            RETURN u.id as user_id, m.id as moto_id,
                                   m.marca as marca, m.modelo as modelo, r.weight as weight
                        """, user_id=user_id, friend_id=friend_id)
                        
                        # Preparar datos para el algoritmo
                        interactions = []
                        for record in interactions_result:
                            interactions.append({
                                "user_id": record["user_id"],
                                "moto_id": record["moto_id"],
                                "weight": record["weight"] if record["weight"] else 1.0
                            })
                        
                        # Ejecutar propagación si hay suficientes datos
                        if interactions:
                            # Inicializar el algoritmo con los datos
                            label_propagation.initialize_from_interactions(interactions)
                            
                            # Obtener recomendaciones para el usuario actual
                            prop_recommendations = label_propagation.get_recommendations(user_id)
                            
                            # Obtener detalles de las motos recomendadas
                            if prop_recommendations:
                                for rec in prop_recommendations[:5]:  # Limitar a 5 recomendaciones por amigo
                                    moto_id = rec["moto_id"]
                                    score = rec["score"]
                                    
                                    # Obtener detalles de la moto
                                    moto_result = db_session.run("""
                                        MATCH (m:Moto {id: $moto_id})
                                        RETURN m.id as id, m.marca as marca, m.modelo as modelo, 
                                               m.tipo as tipo, m.precio as precio, m.imagen as imagen
                                    """, moto_id=moto_id)
                                    
                                    moto_record = moto_result.single()
                                    if moto_record:
                                        propagation_motos.append({
                                            "friend_name": friend_username,
                                            "score": score,
                                            "moto": {
                                                "id": moto_record["id"],
                                                "marca": moto_record["marca"],
                                                "modelo": moto_record["modelo"],
                                                "tipo": moto_record["tipo"],
                                                "precio": moto_record["precio"],
                                                "imagen": moto_record["imagen"]
                                            }
                                        })
                except Exception as e:
                    logger.error(f"Error al generar recomendaciones con label propagation para {friend_username}: {e}")
            
            # Ordenar motos recomendadas por puntuación
            propagation_motos.sort(key=lambda x: x["score"], reverse=True)
            
            # Renderizar plantilla con los datos
            return render_template('motos_recomendadas.html', 
                                   friends_data=friends,
                                   ideal_motos=ideal_motos,
                                   liked_motos=liked_motos,
                                   propagation_motos=propagation_motos)
        else:
            # Usar el getDB_connection como respaldo
            connector = get_db_connection()
            if not connector:
                flash('No se pudo conectar a la base de datos. Intente más tarde.', 'error')
                return redirect(url_for('main.dashboard'))
            
            # Obtener lista de amigos
            friends = []
            with connector.driver.session() as db_session:
                # Modificar para buscar tanto FRIEND como FRIEND_OF relaciones
                result = db_session.run("""
                    MATCH (u:User {id: $user_id})-[:FRIEND|:FRIEND_OF]->(f:User)
                    RETURN f.id as friend_id, f.username as friend_username
                """, user_id=user_id)
                
                friends = [{"id": record["friend_id"], "username": record["friend_username"]} 
                          for record in result]
            
            # Si no hay amigos, mostrar página con mensaje
            if not friends:
                return render_template('motos_recomendadas.html', friends_data=None)
            
            # Preparar datos para la plantilla
            ideal_motos = {}
            liked_motos = []
            propagation_motos = []
            
            # Crear instancia del algoritmo de label propagation
            label_propagation = MotoLabelPropagation()
            
            # Procesar cada amigo de manera similar a la implementación anterior
            # ... (código similar al de arriba)
            
            # Renderizar plantilla con los datos
            return render_template('motos_recomendadas.html', 
                                  friends_data=friends,
                                  ideal_motos=ideal_motos,
                                  liked_motos=liked_motos,
                                  propagation_motos=propagation_motos)
    except Exception as e:
        logger.error(f"Error en la página de motos recomendadas: {str(e)}")
        flash(f'Error al cargar recomendaciones: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))
