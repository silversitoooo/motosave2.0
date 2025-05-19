@fixed_routes.route('/moto_ideal')
def moto_ideal():
    """Página de moto ideal."""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    username = session.get('username', '')
    user_id = session.get('user_id', '')
    
    try:
        # Obtener el adaptador
        adapter = current_app.config.get('MOTO_RECOMMENDER')
        
        if not adapter:
            return render_template('error.html', 
                             title="Sistema no disponible",
                             error="El sistema de recomendaciones no está disponible en este momento.")
        
        # Buscar el ID real del usuario en la base de datos
        db_user_id = username  # Por defecto, usamos el nombre de usuario
        if adapter.users_df is not None:
            user_rows = adapter.users_df[adapter.users_df['username'] == username]
            if not user_rows.empty:
                db_user_id = user_rows.iloc[0].get('user_id', username)
                logger.info(f"ID de usuario encontrado en la base de datos: {db_user_id}")
            else:
                logger.warning(f"Usuario {username} no encontrado en la base de datos")
        
        # Obtener la moto ideal para el usuario de Neo4j
        if hasattr(adapter, '_ensure_neo4j_connection'):
            adapter._ensure_neo4j_connection()
            with adapter.driver.session() as neo4j_session:
                result = neo4j_session.run(
                    """
                    MATCH (u:User {id: $user_id})-[r:IDEAL]->(m:Moto)
                    RETURN m.id as moto_id, r.score as score, r.reasons as reasons
                    """,
                    user_id=db_user_id
                )
                
                record = result.single()
                
                if record:
                    moto_id = record['moto_id']
                    score = record['score']
                    reasons_str = record['reasons'] if 'reasons' in record else '[]'
                    
                    try:
                        reasons = json.loads(reasons_str)
                    except:
                        reasons = [reasons_str] if reasons_str else ["Recomendación personalizada"]
                    
                    # Obtener los detalles de la moto
                    moto_info = adapter.motos_df[adapter.motos_df['moto_id'] == moto_id]
                    
                    if not moto_info.empty:
                        moto_row = moto_info.iloc[0]
                        moto = {
                            "modelo": moto_row.get('modelo', 'Modelo Desconocido'),
                            "marca": moto_row.get('marca', 'Marca Desconocida'),
                            "precio": float(moto_row.get('precio', 0)),
                            "tipo": moto_row.get('tipo', 'Estilo Desconocido'),
                            "imagen": moto_row.get('imagen', ''),
                            "razones": reasons,
                            "score": score,
                            "moto_id": moto_id
                        }
                        
                        return render_template('moto_ideal.html', moto=moto)
        
        # Si no encontramos una moto ideal, mostrar ejemplo por defecto
        logger.warning(f"No se encontró moto ideal para usuario {username}, mostrando ejemplo")
        moto = {
            "modelo": "MT-09", 
            "marca": "Yamaha", 
            "precio": 9999.0,
            "tipo": "Naked",
            "imagen": "https://www.yamaha-motor.eu/es/es/products/motorcycles/hyper-naked/mt-09/_jcr_content/root/verticalnavigationcontainer/verticalnavigation/image_copy.img.jpg/1678272292818.jpg",
            "razones": ["Perfecta combinación de potencia y manejabilidad", "Se adapta a tu nivel de experiencia", "Dentro de tu presupuesto"],
            "score": 95.8
        }
        
        return render_template('moto_ideal.html', moto=moto)
            
    except Exception as e:
        logger.error(f"Error al obtener moto ideal: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return render_template('error.html', 
                             title="Error al cargar moto ideal",
                             error=f"Ocurrió un error al cargar tu moto ideal: {str(e)}")
