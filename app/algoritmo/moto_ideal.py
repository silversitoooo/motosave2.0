"""
Algoritmo de recomendación de moto ideal mejorado con sistema híbrido
"""
import pandas as pd
import numpy as np
from ..models import User, Moto, UserPreference
import logging
from .hybrid_recommender import HybridMotoRecommender

logger = logging.getLogger(__name__)

class MotoIdealRecommender:
    """
    Clase mejorada que usa un sistema híbrido para mayor variabilidad y precisión
    """
    
    def __init__(self, df_motos=None, neo4j_connector=None):
        self.df_motos = df_motos
        self.neo4j_connector = neo4j_connector
        self.hybrid_system = HybridMotoRecommender(neo4j_connector)
        self.logger = logging.getLogger(__name__)
        self.logger.info("MotoIdealRecommender inicializado con sistema híbrido")
    
    def get_recommendations(self, user_id, top_n=5, preferences=None):
        """
        Obtiene recomendaciones usando el sistema híbrido mejorado
        """
        self.logger.info(f"Calculando recomendaciones híbridas para {user_id} con preferencias: {preferences}")
        
        # Si no se proporcionan preferencias, obtenerlas de Neo4j
        if preferences is None and self.neo4j_connector:
            preferences = self._get_user_preferences(user_id)
            
        if not preferences:
            self.logger.warning(f"No se encontraron preferencias para {user_id}")
            preferences = {}
        
        try:
            # Usar el sistema híbrido para obtener recomendaciones
            hybrid_recommendations = self.hybrid_system.get_hybrid_recommendations(
                user_id, preferences, top_n
            )
            
            if hybrid_recommendations:
                self.logger.info(f"Generadas {len(hybrid_recommendations)} recomendaciones híbridas para {user_id}")
                return hybrid_recommendations
            else:
                # Fallback al método original si el híbrido falla
                self.logger.warning("Sistema híbrido no devolvió resultados, usando fallback")
                return self._fallback_recommendations(top_n)
                
        except Exception as e:
            self.logger.error(f"Error en recomendaciones híbridas: {str(e)}")
            return self._fallback_recommendations(top_n)
    
    def _get_user_preferences(self, user_id):
        """Obtiene las preferencias del usuario desde Neo4j"""
        if not self.neo4j_connector:
            return None
            
        try:
            with self.neo4j_connector.driver.session() as session:
                result = session.run("""
                    MATCH (u:User {id: $user_id})-[:HAS_PREFERENCE]->(p:UserPreference)
                    RETURN p.estilos_preferidos as estilos, p.marcas_preferidas as marcas,
                           p.experiencia as experiencia, p.presupuesto as presupuesto,
                           p.uso_previsto as uso_previsto, p.datos_test as datos_test
                """, user_id=user_id)
                
                record = result.single()
                if record:
                    preferences = {}
                    
                    # Procesar estilos preferidos
                    estilos_str = record.get('estilos', '')
                    if estilos_str:
                        try:
                            import json
                            preferences['estilos'] = json.loads(estilos_str)
                        except:
                            estilos = {}
                            for estilo in estilos_str.split(','):
                                estilo = estilo.strip()
                                if estilo:
                                    estilos[estilo] = 1.0
                            preferences['estilos'] = estilos
                    
                    # Procesar marcas preferidas
                    marcas_str = record.get('marcas', '')
                    if marcas_str:
                        try:
                            import json
                            preferences['marcas'] = json.loads(marcas_str)
                        except:
                            marcas = {}
                            for marca in marcas_str.split(','):
                                marca = marca.strip()
                                if marca:
                                    marcas[marca] = 1.0
                            preferences['marcas'] = marcas
                    
                    # Datos simples
                    preferences['experiencia'] = record.get('experiencia')
                    preferences['presupuesto'] = record.get('presupuesto')
                    preferences['uso_previsto'] = record.get('uso_previsto')
                    
                    # Datos de test completos
                    datos_test = record.get('datos_test')
                    if datos_test:
                        try:
                            import json
                            test_data = json.loads(datos_test)
                            for key, value in test_data.items():
                                if key not in preferences:
                                    preferences[key] = value
                        except:
                            pass
                    
                    return preferences
                    
                return None
        except Exception as e:
            self.logger.error(f"Error al obtener preferencias para {user_id}: {str(e)}")
            return None
    
    def _fallback_recommendations(self, top_n):
        """Recomendaciones de fallback cuando el sistema híbrido falla"""
        if not self.neo4j_connector:
            return []
            
        try:
            with self.neo4j_connector.driver.session() as session:
                result = session.run("""
                    MATCH (m:Moto)
                    OPTIONAL MATCH (m)<-[r:INTERACTED]-()
                    WITH m, count(r) as interactions
                    ORDER BY interactions DESC, m.precio ASC
                    LIMIT $limit
                    RETURN m.id as moto_id, m.marca as marca, m.modelo as modelo,
                           m.tipo as tipo, m.precio as precio, m.cilindrada as cilindrada,
                           m.imagen as imagen, interactions as score
                """, limit=top_n)
                
                result_list = []
                for record in result:
                    result_list.append({
                        'moto_id': record['moto_id'],
                        'marca': record['marca'],
                        'modelo': record['modelo'],
                        'tipo': record.get('tipo', 'N/A'),
                        'precio': record.get('precio', 0),
                        'cilindrada': record.get('cilindrada', 0),
                        'imagen': record.get('imagen', ''),
                        'score': record['score'],
                        'note': 'Recomendación popular (sistema de respaldo)',
                        'methods_used': ['popularity_fallback']
                    })
                
                return result_list
        except Exception as e:
            self.logger.error(f"Error en recomendaciones de fallback: {str(e)}")
            return []