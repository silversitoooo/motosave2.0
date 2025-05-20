"""
Código corregido para la ruta /moto_ideal que evita problemas con múltiples relaciones IDEAL
y asegura que la moto se muestre correctamente en la página.
"""

# Ruta corregida para moto_ideal
@app.route('/moto_ideal')
def moto_ideal():
    """Muestra la moto ideal del usuario logueado."""
    if 'username' not in session:
        flash('Debes iniciar sesión para ver tu moto ideal', 'warning')
        return redirect(url_for('login'))
    
    username = session['username']
    
    # Variables para la plantilla
    moto = None
    reasons = []
    score = None
    
    try:
        # Obtener adaptador
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        if not adapter:
            logger.warning("Adaptador no disponible")
            flash('Error al cargar el adaptador de recomendaciones', 'error')
            return render_template('moto_ideal.html', moto=None)
        
        # Obtener ID de usuario desde la base de datos
        db_user_id = None
        if hasattr(adapter, 'users_df') and adapter.users_df is not None:
            user_rows = adapter.users_df[adapter.users_df['username'] == username]
            if not user_rows.empty:
                db_user_id = user_rows.iloc[0].get('user_id', username)
                logger.info(f"ID de usuario encontrado en la base de datos: {db_user_id}")
            else:
                logger.warning(f"Usuario {username} no encontrado en la base de datos")
        
        if db_user_id is None:
            db_user_id = username
        
        # Obtener la moto ideal para el usuario de Neo4j
        if hasattr(adapter, '_ensure_neo4j_connection'):
            adapter._ensure_neo4j_connection()
            with adapter.driver.session() as neo4j_session:
                # Consulta mejorada para obtener toda la información de la moto
                result = neo4j_session.run(
                    """
                    MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto)
                    RETURN m.id as moto_id, m.marca as marca, m.modelo as modelo, 
                           m.potencia as potencia, m.precio as precio, m.tipo as tipo,
                           m.imagen as imagen, m.cilindrada as cilindrada,
                           r.score as score, r.reasons as reasons
                    LIMIT 1
                    """,
                    user_id=db_user_id
                )
                
                record = result.single()
                
                if record:
                    moto_id = record['moto_id']
                    score = record['score']
                    reasons_str = record['reasons'] if 'reasons' in record else '[]'
                    
                    # Convertir razones de JSON a lista
                    try:
                        reasons = json.loads(reasons_str)
                    except (json.JSONDecodeError, TypeError):
                        reasons = []
                    
                    # Obtener datos completos de la moto
                    moto = {
                        'id': moto_id,
                        'marca': record['marca'],
                        'modelo': record['modelo'],
                        'potencia': record['potencia'],
                        'precio': record['precio'],
                        'tipo': record['tipo'],
                        'cilindrada': record['cilindrada'],
                        'imagen': record['imagen']
                    }
                    
                    logger.info(f"Moto ideal encontrada para {username}: {moto['marca']} {moto['modelo']}")
                else:
                    logger.warning(f"No se encontró moto ideal para el usuario {username}")
        
        # Renderizar plantilla con los datos obtenidos
        return render_template('moto_ideal.html', moto=moto, reasons=reasons, score=score)
        
    except Exception as e:
        logger.error(f"Error en ruta moto_ideal: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        flash('Ocurrió un error al obtener tu moto ideal', 'error')
        return render_template('moto_ideal.html', moto=None)
