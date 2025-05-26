"""
Sistema híbrido de recomendaciones que combina múltiples algoritmos para mayor variabilidad y precisión
"""
import pandas as pd
import numpy as np
import logging
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import random
from typing import List, Dict, Any
from .quantitative_evaluator import QuantitativeEvaluator

logger = logging.getLogger(__name__)

class HybridMotoRecommender:
    """
    Sistema híbrido que combina:
    1. Filtrado basado en contenido (características de motos)
    2. Filtrado colaborativo (comportamiento de usuarios similares)
    3. Algoritmo basado en conocimiento (reglas expertas)
    4. Diversificación activa
    5. Exploración vs Explotación
    """
    def __init__(self, neo4j_connector=None):
        self.neo4j_connector = neo4j_connector
        self.motos_df = None
        self.users_df = None
        self.interactions_df = None
        self.user_similarity_matrix = None
        self.moto_features_matrix = None
        self.scaler = StandardScaler()
        self.quantitative_evaluator = QuantitativeEvaluator()
        self.logger = logging.getLogger(__name__)
        
    def _load_data(self):
        """Carga y prepara todos los datos necesarios"""
        if not self.neo4j_connector:
            return False
            
        try:
            with self.neo4j_connector.driver.session() as session:
                # Cargar motos con todas sus características
                motos_query = """
                MATCH (m:Moto)
                RETURN m.id as id, m.marca as marca, m.modelo as modelo, 
                       m.tipo as tipo, m.cilindrada as cilindrada, m.precio as precio,
                       m.potencia as potencia, m.peso as peso, m.descripcion as descripcion,
                       m.imagen as imagen, m.año as año
                """
                result = session.run(motos_query)
                motos_data = []
                for record in result:
                    motos_data.append({
                        'id': record['id'],
                        'marca': record['marca'],
                        'modelo': record['modelo'],
                        'tipo': record['tipo'],
                        'cilindrada': self._parse_numeric(record['cilindrada']),
                        'precio': self._parse_numeric(record['precio']),
                        'potencia': self._parse_numeric(record['potencia']),
                        'peso': self._parse_numeric(record['peso']),
                        'descripcion': record['descripcion'] or '',
                        'imagen': record['imagen'] or '',
                        'año': self._parse_numeric(record['año'])
                    })
                self.motos_df = pd.DataFrame(motos_data)
                
                # Cargar usuarios y sus preferencias
                users_query = """
                MATCH (u:User)
                OPTIONAL MATCH (u)-[:HAS_PREFERENCE]->(p:UserPreference)
                RETURN u.id as id, u.username as username, u.email as email,
                       p.experiencia as experiencia, p.presupuesto as presupuesto,
                       p.uso_previsto as uso_previsto, p.estilos_preferidos as estilos,
                       p.marcas_preferidas as marcas, p.datos_test as datos_test
                """
                result = session.run(users_query)
                users_data = []
                for record in result:
                    users_data.append({
                        'id': record['id'],
                        'username': record['username'],
                        'email': record['email'],
                        'experiencia': record['experiencia'],
                        'presupuesto': self._parse_numeric(record['presupuesto']),
                        'uso_previsto': record['uso_previsto'],
                        'estilos': record['estilos'] or '{}',
                        'marcas': record['marcas'] or '{}',
                        'datos_test': record['datos_test'] or '{}'
                    })
                self.users_df = pd.DataFrame(users_data)
                
                # Cargar interacciones (likes, views, etc.)
                interactions_query = """
                MATCH (u:User)-[r:INTERACTED]->(m:Moto)
                RETURN u.id as user_id, m.id as moto_id, r.type as interaction_type,
                       r.weight as weight, r.timestamp as timestamp
                """
                result = session.run(interactions_query)
                interactions_data = []
                for record in result:
                    interactions_data.append({
                        'user_id': record['user_id'],
                        'moto_id': record['moto_id'],
                        'interaction_type': record['interaction_type'],
                        'weight': float(record['weight']) if record['weight'] else 1.0,
                        'timestamp': record['timestamp']
                    })
                self.interactions_df = pd.DataFrame(interactions_data)
                
                logger.info(f"Datos cargados: {len(self.motos_df)} motos, {len(self.users_df)} usuarios, {len(self.interactions_df)} interacciones")
                return True
                
        except Exception as e:
            logger.error(f"Error cargando datos: {str(e)}")
            return False
    
    def _parse_numeric(self, value):
        """Convierte valores a numérico de forma segura"""
        if value is None:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        try:
            import re
            # Extraer números de strings
            numbers = re.findall(r'\d+\.?\d*', str(value))
            return float(numbers[0]) if numbers else 0.0
        except:
            return 0.0
    
    def _prepare_feature_matrices(self):
        """Prepara matrices de características para similitud"""
        if self.motos_df is None:
            return
            
        # Crear matriz de características de motos
        numeric_features = ['cilindrada', 'precio', 'potencia', 'peso', 'año']
        feature_matrix = []
        
        for _, moto in self.motos_df.iterrows():
            features = []
            
            # Características numéricas normalizadas
            for feature in numeric_features:
                features.append(moto[feature])
            
            # Características categóricas (one-hot encoding simplificado)
            # Tipos de moto
            tipos = ['naked', 'sport', 'touring', 'trail', 'scooter', 'cruiser', 'enduro']
            tipo_moto = str(moto['tipo']).lower()
            for tipo in tipos:
                features.append(1.0 if tipo in tipo_moto else 0.0)
            
            # Marcas principales
            marcas = ['yamaha', 'honda', 'kawasaki', 'suzuki', 'bmw', 'ducati', 'ktm', 'aprilia']
            marca_moto = str(moto['marca']).lower()
            for marca in marcas:
                features.append(1.0 if marca in marca_moto else 0.0)
            
            feature_matrix.append(features)
        
        # Normalizar características numéricas
        self.moto_features_matrix = self.scaler.fit_transform(feature_matrix)
        logger.info(f"Matriz de características creada: {self.moto_features_matrix.shape}")
    
    def _calculate_user_similarity(self):
        """Calcula similitud entre usuarios basada en sus interacciones y preferencias"""
        if self.users_df is None or self.interactions_df is None:
            return
            
        # Crear matriz usuario-moto
        users_list = self.users_df['id'].tolist()
        motos_list = self.motos_df['id'].tolist()
        
        user_moto_matrix = np.zeros((len(users_list), len(motos_list)))
        
        for _, interaction in self.interactions_df.iterrows():
            try:
                user_idx = users_list.index(interaction['user_id'])
                moto_idx = motos_list.index(interaction['moto_id'])
                
                # Pesos diferentes según tipo de interacción
                weight = interaction['weight']
                if interaction['interaction_type'] == 'like':
                    weight *= 2.0
                elif interaction['interaction_type'] == 'view':
                    weight *= 0.5
                
                user_moto_matrix[user_idx, moto_idx] = weight
            except ValueError:
                continue  # Usuario o moto no encontrados
        
        # Calcular similitud coseno entre usuarios
        self.user_similarity_matrix = cosine_similarity(user_moto_matrix)
        logger.info(f"Matriz de similitud de usuarios calculada: {self.user_similarity_matrix.shape}")
    
    def get_hybrid_recommendations(self, user_id: str, preferences: Dict, top_n: int = 10) -> List[Dict]:
        """
        Obtiene recomendaciones híbridas combinando múltiples enfoques
        """
        # Asegurar que los datos están cargados
        if self.motos_df is None:
            if not self._load_data():
                return []
            self._prepare_feature_matrices()
            self._calculate_user_similarity()
        
        # 1. FILTRADO BASADO EN CONTENIDO (40% del peso)
        content_recs = self._content_based_recommendations(user_id, preferences, top_n * 2)
        
        # 2. FILTRADO COLABORATIVO (30% del peso)
        collaborative_recs = self._collaborative_filtering_recommendations(user_id, top_n * 2)
        
        # 3. ALGORITMO BASADO EN CONOCIMIENTO (20% del peso)
        knowledge_recs = self._knowledge_based_recommendations(preferences, top_n * 2)
        
        # 4. RECOMENDACIONES POPULARES/TENDENCIAS (10% del peso)
        popularity_recs = self._popularity_based_recommendations(top_n)
        
        # 5. COMBINAR Y DIVERSIFICAR
        final_recs = self._combine_and_diversify_recommendations(
            content_recs, collaborative_recs, knowledge_recs, popularity_recs,
            user_id, preferences, top_n
        )
        
        return final_recs
    
    def _content_based_recommendations(self, user_id: str, preferences: Dict, top_n: int) -> List[Dict]:
        """Recomendaciones basadas en contenido usando FORZADAMENTE el evaluador cuantitativo"""
        if self.motos_df is None:
            self.logger.warning("No hay datos de motos cargados")
            return []
        
        scores = {}
        self.logger.info(f"[HYBRID] FORZANDO uso de QuantitativeEvaluator para {len(self.motos_df)} motos")
        self.logger.info(f"[HYBRID] Preferencias recibidas: {preferences}")
        
        # FORZAR el uso del evaluador cuantitativo para TODAS las motos
        motos_evaluadas = 0
        for idx, moto in self.motos_df.iterrows():
            try:
                self.logger.info(f"[HYBRID] Evaluando moto {moto['id']} con QuantitativeEvaluator")
                
                # USAR OBLIGATORIAMENTE el evaluador cuantitativo
                score, reasons = self.quantitative_evaluator.evaluate_moto_quantitative(preferences, moto)
                
                self.logger.info(f"[HYBRID] Moto {moto['id']} - Score obtenido: {score}")
                
                if score > 0:
                    scores[moto['id']] = {
                        'score': score,
                        'reasons': reasons,
                        'method': 'content_quantitative',
                        'moto_data': moto.to_dict()
                    }
                
                motos_evaluadas += 1
                if motos_evaluadas >= 10:  # Limitar para debug
                    break
                    
            except Exception as e:
                self.logger.error(f"[HYBRID] ERROR evaluando moto {moto.get('id', 'unknown')}: {str(e)}")
                import traceback
                self.logger.error(f"[HYBRID] Traceback completo: {traceback.format_exc()}")
                continue
        
        self.logger.info(f"[HYBRID] Motas evaluadas: {motos_evaluadas}, Motos con score > 0: {len(scores)}")
        
        # Ordenar y devolver top N
        sorted_scores = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)
        self.logger.info(f"[HYBRID] Top 5 motos por score: {[(k, v['score']) for k, v in sorted_scores[:5]]}")
        
        return [{'moto_id': k, **v} for k, v in sorted_scores[:top_n]]
    
    def _knowledge_based_recommendations(self, preferences: Dict, top_n: int) -> List[Dict]:
        """Recomendaciones basadas en reglas expertas"""
        if self.motos_df is None:
            return []
        
        recommendations = {}
        
        # Reglas expertas basadas en uso previsto
        uso = preferences.get('uso', preferences.get('uso_previsto', '')).lower()
        experiencia = preferences.get('experiencia', '').lower()
        
        for _, moto in self.motos_df.iterrows():
            score = 0.0
            reasons = []
            
            tipo_moto = str(moto['tipo']).lower()
            cilindrada = moto['cilindrada']
            
            # Reglas por uso
            if uso == 'ciudad':
                if any(x in tipo_moto for x in ['naked', 'scooter', 'urbana']):
                    score += 3.0
                    reasons.append("Ideal para ciudad")
                if cilindrada <= 400:
                    score += 1.0
                    reasons.append("Cilindrada urbana")
                    
            elif uso == 'carretera':
                if any(x in tipo_moto for x in ['sport', 'touring', 'deportiva']):
                    score += 3.0
                    reasons.append("Perfecta para carretera")
                if cilindrada >= 500:
                    score += 1.0
                    reasons.append("Potencia para carretera")
                    
            elif uso == 'mixto':
                if any(x in tipo_moto for x in ['trail', 'adventure', 'naked']):
                    score += 3.0
                    reasons.append("Versátil para uso mixto")
                if 300 <= cilindrada <= 700:
                    score += 1.0
                    reasons.append("Cilindrada versátil")
            
            # Reglas por experiencia
            if experiencia == 'principiante':
                if cilindrada <= 400:
                    score += 2.0
                    reasons.append("Adecuada para principiantes")
                elif cilindrada > 600:
                    score -= 2.0  # Penalizar motos muy potentes
                    
            elif experiencia == 'intermedio':
                if 300 <= cilindrada <= 700:
                    score += 2.0
                    reasons.append("Perfecta para nivel intermedio")
                    
            elif experiencia == 'avanzado':
                if cilindrada >= 600:
                    score += 2.0
                    reasons.append("Potencia para expertos")
            
            # Regla de seguridad moderna
            descripcion = str(moto['descripcion']).lower()
            if any(x in descripcion for x in ['abs', 'tcs', 'control tracción']):
                score += 0.5
                reasons.append("Sistemas de seguridad modernos")
            
            if score > 0:
                recommendations[moto['id']] = {
                    'score': score,
                    'reasons': reasons,
                    'method': 'knowledge',
                    'moto_data': moto.to_dict()
                }
        
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1]['score'], reverse=True)
        return [{'moto_id': k, **v} for k, v in sorted_recs[:top_n]]
    
    def _popularity_based_recommendations(self, top_n: int) -> List[Dict]:
        """Recomendaciones basadas en popularidad general"""
        if self.interactions_df is None:
            return []
        
        # Calcular popularidad por número de interacciones
        popularity = self.interactions_df.groupby('moto_id').agg({
            'weight': 'sum',
            'user_id': 'count'
        }).reset_index()
        
        popularity['popularity_score'] = popularity['weight'] + (popularity['user_id'] * 0.5)
        popularity = popularity.sort_values('popularity_score', ascending=False)
        
        result = []
        for _, row in popularity.head(top_n).iterrows():
            moto_data = self.motos_df[self.motos_df['id'] == row['moto_id']]
            if not moto_data.empty:
                result.append({
                    'moto_id': row['moto_id'],
                    'score': row['popularity_score'],
                    'reasons': [f"Popular entre usuarios ({row['user_id']} interacciones)"],
                    'method': 'popularity',
                    'moto_data': moto_data.iloc[0].to_dict()
                })
        
        return result
    
    def _combine_and_diversify_recommendations(self, content_recs, collaborative_recs, 
                                             knowledge_recs, popularity_recs, 
                                             user_id, preferences, top_n):
        """Combina recomendaciones de diferentes métodos y asegura diversidad"""
        
        # Pesos para cada método
        weights = {
            'content': 0.4,
            'collaborative': 0.3,
            'knowledge': 0.2,
            'popularity': 0.1
        }
        
        all_recommendations = {}
        
        # Combinar todas las recomendaciones
        for recs, weight in [(content_recs, weights['content']), 
                           (collaborative_recs, weights['collaborative']),
                           (knowledge_recs, weights['knowledge']), 
                           (popularity_recs, weights['popularity'])]:
            
            for rec in recs:
                moto_id = rec['moto_id']
                if moto_id not in all_recommendations:
                    all_recommendations[moto_id] = {
                        'combined_score': 0.0,
                        'methods': [],
                        'all_reasons': [],
                        'moto_data': rec.get('moto_data', {})
                    }
                
                # Agregar score ponderado
                all_recommendations[moto_id]['combined_score'] += rec['score'] * weight
                all_recommendations[moto_id]['methods'].append(rec.get('method', 'unknown'))
                all_recommendations[moto_id]['all_reasons'].extend(rec.get('reasons', []))
        
        # Agregar factor de diversidad
        all_recommendations = self._add_diversity_factor(all_recommendations, preferences)
        
        # Agregar factor de exploración vs explotación
        all_recommendations = self._add_exploration_factor(all_recommendations, user_id)
        
        # Ordenar por score combinado
        sorted_recs = sorted(all_recommendations.items(), 
                           key=lambda x: x[1]['combined_score'], reverse=True)
        
        # Asegurar diversidad en el resultado final
        final_recs = self._ensure_final_diversity(sorted_recs, top_n)
        
        return final_recs
    
    def _add_diversity_factor(self, recommendations, preferences):
        """Añade factor de diversidad para evitar recomendaciones muy similares"""
        
        # Agrupar por marca y tipo
        marca_count = {}
        tipo_count = {}
        
        for moto_id, rec in recommendations.items():
            moto_data = rec['moto_data']
            marca = moto_data.get('marca', '').lower()
            tipo = moto_data.get('tipo', '').lower()
            
            marca_count[marca] = marca_count.get(marca, 0) + 1
            tipo_count[tipo] = tipo_count.get(tipo, 0) + 1
        
        # Penalizar sobre-representación
        for moto_id, rec in recommendations.items():
            moto_data = rec['moto_data']
            marca = moto_data.get('marca', '').lower()
            tipo = moto_data.get('tipo', '').lower()
            
            # Penalizar si hay demasiadas motos de la misma marca o tipo
            if marca_count[marca] > 2:
                rec['combined_score'] *= 0.8
            if tipo_count[tipo] > 3:
                rec['combined_score'] *= 0.9
        
        return recommendations
    
    def _add_exploration_factor(self, recommendations, user_id):
        """Añade factor de exploración para mostrar opciones nuevas"""
        
        # Obtener motos ya vistas por el usuario
        seen_motos = set()
        if self.interactions_df is not None:
            user_interactions = self.interactions_df[self.interactions_df['user_id'] == user_id]
            seen_motos = set(user_interactions['moto_id'].tolist())
        
        # Dar boost a motos no vistas (exploración)
        for moto_id, rec in recommendations.items():
            if moto_id not in seen_motos:
                rec['combined_score'] *= 1.1  # 10% de boost por exploración
                rec['all_reasons'].append("Nueva opción para explorar")
        
        return recommendations
    
    def _ensure_final_diversity(self, sorted_recs, top_n):
        """Asegura diversidad en el resultado final"""
        
        final_results = []
        used_marcas = set()
        used_tipos = set()
        
        # Primera pasada: seleccionar diversas opciones
        for moto_id, rec_data in sorted_recs:
            if len(final_results) >= top_n:
                break
                
            moto_data = rec_data['moto_data']
            marca = moto_data.get('marca', '').lower()
            tipo = moto_data.get('tipo', '').lower()
            
            # Permitir máximo 2 motos por marca y 3 por tipo
            marca_count = sum(1 for r in final_results if r['marca'].lower() == marca)
            tipo_count = sum(1 for r in final_results if r['tipo'].lower() == tipo)
            
            if marca_count < 2 and tipo_count < 3:
                final_results.append({
                    'moto_id': moto_id,
                    'score': rec_data['combined_score'],
                    'marca': moto_data.get('marca', ''),
                    'modelo': moto_data.get('modelo', ''),
                    'tipo': moto_data.get('tipo', ''),
                    'precio': moto_data.get('precio', 0),
                    'cilindrada': moto_data.get('cilindrada', 0),
                    'imagen': moto_data.get('imagen', ''),
                    'methods_used': list(set(rec_data['methods'])),
                    'note': ' | '.join(list(set(rec_data['all_reasons']))),
                    'details': moto_data
                })
                used_marcas.add(marca)
                used_tipos.add(tipo)
        
        # Segunda pasada: llenar espacios restantes si es necesario
        if len(final_results) < top_n:
            for moto_id, rec_data in sorted_recs:
                if len(final_results) >= top_n:
                    break
                    
                # Si no está ya en los resultados, agregarlo
                if not any(r['moto_id'] == moto_id for r in final_results):
                    moto_data = rec_data['moto_data']
                    final_results.append({
                        'moto_id': moto_id,
                        'score': rec_data['combined_score'],
                        'marca': moto_data.get('marca', ''),
                        'modelo': moto_data.get('modelo', ''),
                        'tipo': moto_data.get('tipo', ''),
                        'precio': moto_data.get('precio', 0),
                        'cilindrada': moto_data.get('cilindrada', 0),
                        'imagen': moto_data.get('imagen', ''),
                        'methods_used': list(set(rec_data['methods'])),
                        'note': ' | '.join(list(set(rec_data['all_reasons']))),
                        'details': moto_data
                    })
        
        return final_results
    
    def _calculate_experience_score(self, cilindrada, experiencia):
        """Calcula puntuación basada en experiencia y cilindrada"""
        if not cilindrada or not experiencia:
            return 0.0
            
        exp = experiencia.lower()
        cc = float(cilindrada)
        
        if exp == 'principiante':
            if cc <= 250:
                return 2.0
            elif cc <= 400:
                return 1.5
            elif cc <= 600:
                return 0.5
            else:
                return -1.0
                
        elif exp == 'intermedio':
            if cc <= 200:
                return 0.5
            elif 250 <= cc <= 700:
                return 2.0
            elif cc <= 900:
                return 1.0
            else:
                return -0.5
                
        elif exp == 'avanzado':
            if cc <= 400:
                return 0.5
            elif cc >= 600:
                return 2.0
            else:
                return 1.5
        
        return 0.0