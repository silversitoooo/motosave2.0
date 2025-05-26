"""
Evaluador mejorado que maneja AMBOS tipos de input: cuantitativo y cualitativo.
Versión robusta que garantiza compatibilidad con cualquier formato de preferencias.
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Any, Optional, Union
from .qualitative_evaluator import QualitativeEvaluator

logger = logging.getLogger(__name__)

class QuantitativeEvaluatorEnhanced:
    """
    Evaluador robusto que combina criterios cuantitativos (rangos numéricos) 
    con criterios cualitativos (preferencias no numéricas).
    
    COMPATIBLE CON:
    1. Input cuantitativo: rangos numéricos (presupuesto_min/max, potencia_min/max, etc.)
    2. Input cualitativo: preferencias categóricas (experiencia, tipo_uso, etc.)
    3. Input mixto: combinación de ambos tipos
    4. Input legacy: formatos antiguos del sistema
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.qualitative_evaluator = QualitativeEvaluator()
        
    def _has_quantitative_inputs(self, preferences: Dict[str, Any]) -> bool:
        """Detecta si las preferencias incluyen inputs cuantitativos (rangos)."""
        quantitative_keys = [
            'presupuesto_min', 'presupuesto_max',
            'potencia_min', 'potencia_max', 
            'cilindrada_min', 'cilindrada_max',
            'peso_min', 'peso_max',
            'torque_min', 'torque_max',
            'ano_min', 'ano_max'
        ]
        return any(key in preferences for key in quantitative_keys)
    
    def _has_qualitative_inputs(self, preferences: Dict[str, Any]) -> bool:
        """Detecta si las preferencias incluyen inputs cualitativos."""
        qualitative_keys = [
            'experiencia', 'tipo_uso', 'pasajeros_carga',
            'combustible_potencia', 'preferencia_potencia_peso',
            'preferencia_rendimiento'
        ]
        return any(key in preferences for key in qualitative_keys)
    
    def _has_legacy_inputs(self, preferences: Dict[str, Any]) -> bool:
        """Detecta si las preferencias usan formato legacy (valores únicos)."""
        legacy_keys = ['presupuesto', 'potencia', 'cilindrada', 'peso', 'torque', 'ano']
        return any(key in preferences for key in legacy_keys)
    
    def _evaluate_presupuesto(self, preferences: Dict[str, Any], precio_moto: float, reasons: List[str]) -> float:
        """Evalúa presupuesto soportando múltiples formatos de input."""
        score = 0.0
        
        # Formato 1: Rango (presupuesto_min/max) - PREFERIDO
        if 'presupuesto_min' in preferences and 'presupuesto_max' in preferences:
            presupuesto_min = float(preferences['presupuesto_min'])
            presupuesto_max = float(preferences['presupuesto_max'])
            
            self.logger.info(f"[PRESUPUESTO] Rango: {presupuesto_min:,.0f}€ - {presupuesto_max:,.0f}€, Moto: {precio_moto:,.0f}€")
            
            if presupuesto_min <= precio_moto <= presupuesto_max:
                score = 3.0
                reasons.append(f"✓ DENTRO del rango de presupuesto ({precio_moto:,.0f}€) [+3.0]")
            elif precio_moto <= presupuesto_max * 1.15:  # Hasta 15% por encima
                score = 2.0
                reasons.append(f"⚠ Hasta 15% por encima del presupuesto ({precio_moto:,.0f}€) [+2.0]")
            elif precio_moto <= presupuesto_max * 1.30:  # Hasta 30% por encima
                score = 1.0
                reasons.append(f"⚠ Hasta 30% por encima del presupuesto ({precio_moto:,.0f}€) [+1.0]")
            else:
                score = 0.0
                reasons.append(f"✗ Excede significativamente el presupuesto ({precio_moto:,.0f}€) [0]")
                
        # Formato 2: Valor único (legacy)
        elif 'presupuesto' in preferences:
            presupuesto = float(preferences['presupuesto'])
            self.logger.info(f"[PRESUPUESTO] Legacy - Límite: {presupuesto:,.0f}€, Moto: {precio_moto:,.0f}€")
            
            if precio_moto <= presupuesto:
                score = 3.0
                reasons.append(f"✓ Dentro del presupuesto ({precio_moto:,.0f}€ ≤ {presupuesto:,.0f}€) [+3.0]")
            elif precio_moto <= presupuesto * 1.15:
                score = 2.0
                reasons.append(f"⚠ Ligeramente por encima del presupuesto [+2.0]")
            else:
                score = 0.0
                reasons.append(f"✗ Excede el presupuesto [0]")
                
        # Formato 3: Sin restricción de presupuesto
        else:
            score = 1.0  # Puntuación neutral
            reasons.append(f"ⓘ Sin restricción de presupuesto (precio: {precio_moto:,.0f}€) [+1.0]")
            self.logger.info(f"[PRESUPUESTO] Sin restricciones definidas")
            
        return score
    
    def _evaluate_marcas(self, preferences: Dict[str, Any], moto: pd.Series, reasons: List[str]) -> float:
        """Evalúa preferencias de marca con múltiples formatos."""
        score = 0.0
        marca_moto = str(moto.get('marca', '')).lower()
        
        if 'marcas' in preferences and preferences['marcas']:
            self.logger.info(f"[MARCAS] Evaluando marca moto: '{marca_moto}'")
            
            # Formato 1: Diccionario con pesos {marca: peso}
            if isinstance(preferences['marcas'], dict):
                for marca_pref, peso in preferences['marcas'].items():
                    if str(marca_pref).lower() in marca_moto:
                        puntos = float(peso) * 5.0  # Multiplicador de marca
                        score += puntos
                        reasons.append(f"✓ Marca preferida: {marca_pref} (peso: {peso}) [+{puntos:.1f}]")
                        self.logger.info(f"[MARCAS] Coincidencia: {marca_pref} -> +{puntos:.1f}")
                        break
                        
            # Formato 2: Lista de marcas preferidas
            elif isinstance(preferences['marcas'], list):
                for marca_pref in preferences['marcas']:
                    if str(marca_pref).lower() in marca_moto:
                        score += 4.0  # Puntuación estándar para lista
                        reasons.append(f"✓ Marca en lista de preferidas: {marca_pref} [+4.0]")
                        break
                        
            # Formato 3: Marca única
            elif isinstance(preferences['marcas'], str):
                if str(preferences['marcas']).lower() in marca_moto:
                    score += 4.0
                    reasons.append(f"✓ Marca preferida: {preferences['marcas']} [+4.0]")
                    
        else:
            # Sin preferencia de marca
            score += 1.0  # Puntuación neutral
            reasons.append(f"ⓘ Sin preferencia específica de marca [+1.0]")
            
        return score
    
    def _evaluate_estilos(self, preferences: Dict[str, Any], moto: pd.Series, reasons: List[str]) -> float:
        """Evalúa preferencias de estilo/tipo con múltiples formatos."""
        score = 0.0
        tipo_moto = str(moto.get('tipo', '')).lower()
        
        # Buscar en múltiples claves posibles
        style_keys = ['estilos', 'tipos', 'estilo', 'tipo']
        styles_pref = None
        
        for key in style_keys:
            if key in preferences and preferences[key]:
                styles_pref = preferences[key]
                break
                
        if styles_pref:
            self.logger.info(f"[ESTILOS] Evaluando tipo moto: '{tipo_moto}'")
            
            # Formato 1: Diccionario con pesos {estilo: peso}
            if isinstance(styles_pref, dict):
                for estilo_pref, peso in styles_pref.items():
                    if str(estilo_pref).lower() in tipo_moto:
                        puntos = float(peso) * 6.0  # Multiplicador de estilo
                        score += puntos
                        reasons.append(f"✓ Estilo preferido: {estilo_pref} (peso: {peso}) [+{puntos:.1f}]")
                        self.logger.info(f"[ESTILOS] Coincidencia: {estilo_pref} -> +{puntos:.1f}")
                        break
                        
            # Formato 2: Lista de estilos preferidos
            elif isinstance(styles_pref, list):
                for estilo_pref in styles_pref:
                    if str(estilo_pref).lower() in tipo_moto:
                        score += 5.0  # Puntuación estándar para lista
                        reasons.append(f"✓ Estilo en lista de preferidos: {estilo_pref} [+5.0]")
                        break
                        
            # Formato 3: Estilo único
            elif isinstance(styles_pref, str):
                if str(styles_pref).lower() in tipo_moto:
                    score += 5.0
                    reasons.append(f"✓ Estilo preferido: {styles_pref} [+5.0]")
                    
        else:
            # Sin preferencia de estilo
            score += 1.0  # Puntuación neutral
            reasons.append(f"ⓘ Sin preferencia específica de estilo [+1.0]")
            
        return score
    
    def _evaluate_numeric_range(self, preferences: Dict[str, Any], moto: pd.Series, 
                              param_name: str, default_value: float = 0) -> Tuple[float, str]:
        """Evalúa rangos numéricos de forma genérica."""
        min_key = f"{param_name}_min"
        max_key = f"{param_name}_max"
        legacy_key = param_name
        
        moto_value = float(moto.get(param_name, default_value))
        
        # Formato 1: Rango (preferido)
        if min_key in preferences and max_key in preferences:
            min_val = float(preferences[min_key])
            max_val = float(preferences[max_key])
            
            if min_val <= moto_value <= max_val:
                return 2.0, f"✓ {param_name.title()} en rango preferido ({moto_value}) [+2.0]"
            else:
                # Penalización proporcional a la distancia del rango
                center = (min_val + max_val) / 2
                distance_factor = abs(moto_value - center) / center if center > 0 else 0
                penalty = min(1.5, distance_factor * 0.5)
                score = max(0.0, 2.0 - penalty)
                return score, f"⚠ {param_name.title()} fuera de rango ({moto_value}) [-{penalty:.1f}]"
                
        # Formato 2: Valor único (legacy)
        elif legacy_key in preferences:
            target_val = float(preferences[legacy_key])
            
            # Para valores legacy, asumimos un rango del ±20%
            tolerance = target_val * 0.2
            if abs(moto_value - target_val) <= tolerance:
                return 2.0, f"✓ {param_name.title()} cerca del objetivo ({moto_value}) [+2.0]"
            else:
                distance_factor = abs(moto_value - target_val) / target_val if target_val > 0 else 0
                penalty = min(1.5, distance_factor)
                score = max(0.0, 2.0 - penalty)
                return score, f"⚠ {param_name.title()} lejos del objetivo ({moto_value}) [-{penalty:.1f}]"
                
        # Sin restricción
        else:
            return 1.0, f"ⓘ Sin restricción de {param_name} ({moto_value}) [+1.0]"
    
    def evaluate_moto_quantitative(self, user_preferences: Dict[str, Any], 
                                 moto: pd.Series) -> Tuple[float, List[str]]:
        """
        Evalúa una moto combinando criterios cuantitativos y cualitativos.
        MÉTODO PRINCIPAL - Compatible con CUALQUIER formato de input.
        """
        total_score = 0.0
        reasons = []
        
        self.logger.info(f"[EVALUATOR] === Iniciando evaluación de moto {moto.get('id')} ===")
        self.logger.info(f"[EVALUATOR] Claves de preferencias: {list(user_preferences.keys())}")
        
        # DETECTAR TIPOS DE INPUT
        has_quantitative = self._has_quantitative_inputs(user_preferences)
        has_qualitative = self._has_qualitative_inputs(user_preferences)
        has_legacy = self._has_legacy_inputs(user_preferences)
        
        self.logger.info(f"[INPUT_TYPE] Cuantitativo: {has_quantitative}, Cualitativo: {has_qualitative}, Legacy: {has_legacy}")
        
        # 1. EVALUACIÓN DE PRESUPUESTO
        presupuesto_score = self._evaluate_presupuesto(user_preferences, float(moto.get('precio', 0)), reasons)
        total_score += presupuesto_score
        
        # 2. EVALUACIÓN DE MARCAS
        marcas_score = self._evaluate_marcas(user_preferences, moto, reasons)
        total_score += marcas_score
        
        # 3. EVALUACIÓN DE ESTILOS/TIPOS
        estilos_score = self._evaluate_estilos(user_preferences, moto, reasons)
        total_score += estilos_score
        
        # 4. EVALUACIÓN DE PARÁMETROS NUMÉRICOS
        numeric_params = ['potencia', 'cilindrada', 'peso', 'torque', 'ano']
        for param in numeric_params:
            score, reason = self._evaluate_numeric_range(user_preferences, moto, param)
            total_score += score
            reasons.append(reason)
        
        self.logger.info(f"[QUANTITATIVE] Moto {moto.get('id')} - Score cuantitativo: {total_score:.2f}")
        
        # 5. INTEGRACIÓN CUALITATIVA (si hay preferencias cualitativas)
        qualitative_score = 0.0
        qualitative_reasons = []
        
        if has_qualitative:
            qualitative_score, qualitative_reasons = self.qualitative_evaluator.evaluate_moto_qualitative(
                user_preferences, moto
            )
            
            # Aplicar factor de peso cualitativo
            qualitative_weight = self.qualitative_evaluator.get_qualitative_weight_factor(user_preferences)
            weighted_qualitative_score = qualitative_score * qualitative_weight
            
            self.logger.info(f"[QUALITATIVE] Score: {qualitative_score:.2f}, Peso: {qualitative_weight:.2f}, Final: {weighted_qualitative_score:.2f}")
        else:
            # Sin evaluación cualitativa
            weighted_qualitative_score = 0.0
            qualitative_reasons = ["ⓘ Sin criterios cualitativos para evaluar"]
            self.logger.info(f"[QUALITATIVE] No hay preferencias cualitativas")
        
        # 6. COMBINACIÓN FINAL DE SCORES
        if has_qualitative:
            # Con evaluación cualitativa: 70% cuant + 30% cual
            quantitative_weight = 0.7
            qualitative_final_weight = 0.3
            final_score = (total_score * quantitative_weight) + (weighted_qualitative_score * qualitative_final_weight)
            
            reasons.append(f"--- Evaluación Cualitativa (peso: {qualitative_final_weight}) ---")
            reasons.extend(qualitative_reasons)
            reasons.append(f"[FINAL] Cuantitativo: {total_score:.2f} × {quantitative_weight} + Cualitativo: {weighted_qualitative_score:.2f} × {qualitative_final_weight} = {final_score:.2f}")
            
        else:
            # Solo evaluación cuantitativa
            final_score = total_score
            reasons.append(f"[FINAL] Solo evaluación cuantitativa: {final_score:.2f}")
        
        self.logger.info(f"[COMBINED] Moto {moto.get('id')} - Score FINAL: {final_score:.2f}")
        
        return final_score, reasons
    
    def get_supported_input_formats(self) -> Dict[str, List[str]]:
        """Retorna documentación de formatos de input soportados."""
        return {
            "cuantitativo_rangos": [
                "presupuesto_min, presupuesto_max",
                "potencia_min, potencia_max",
                "cilindrada_min, cilindrada_max",
                "peso_min, peso_max",
                "torque_min, torque_max",
                "ano_min, ano_max"
            ],
            "cuantitativo_legacy": [
                "presupuesto", "potencia", "cilindrada", 
                "peso", "torque", "ano"
            ],
            "cualitativo": [
                "experiencia: principiante|intermedio|experto",
                "tipo_uso: ciudad|carretera|mixto|aventura",
                "pasajeros_carga: solo|ocasional|frecuente",
                "combustible_potencia: ahorro|equilibrio|potencia",
                "preferencia_potencia_peso: baja|media|alta",
                "preferencia_rendimiento: economia|balance|rendimiento"
            ],
            "marcas_estilos": [
                "marcas: dict {marca: peso} | list [marcas] | str marca",
                "estilos: dict {estilo: peso} | list [estilos] | str estilo"
            ]
        }


# Alias para compatibilidad con código existente
QuantitativeEvaluator = QuantitativeEvaluatorEnhanced
