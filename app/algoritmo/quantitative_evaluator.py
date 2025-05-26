"""
Evaluador cuantitativo para el algoritmo de recomendación de motos.
Extiende el sistema actual para manejar rangos numéricos generados por preguntas cuantitativas.
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Any, Optional, Union
from .qualitative_evaluator import QualitativeEvaluator

logger = logging.getLogger(__name__)

class QuantitativeEvaluator:
    """
    Evaluador que combina criterios cuantitativos (rangos numéricos) 
    con criterios cualitativos (ponderaciones).
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.qualitative_evaluator = QualitativeEvaluator()
        
    def evaluate_moto_quantitative(self, user_preferences: Dict[str, Any], 
                                 moto: pd.Series) -> Tuple[float, List[str]]:
        """
        Evalúa una moto usando EXACTAMENTE el sistema de ponderaciones solicitado
        """
        total_score = 0.0
        reasons = []
        
        self.logger.info(f"[QUANTITATIVE] Iniciando evaluación de moto {moto.get('id')}")
        self.logger.info(f"[QUANTITATIVE] Preferencias: {user_preferences}")
        
        # 1. PRESUPUESTO - FORZAR uso de rangos numéricos
        precio_moto = float(moto.get('precio', 0))
        
        if 'presupuesto_min' in user_preferences and 'presupuesto_max' in user_preferences:
            presupuesto_min = float(user_preferences['presupuesto_min'])
            presupuesto_max = float(user_preferences['presupuesto_max'])
            self.logger.info(f"[QUANTITATIVE] Usando RANGO de presupuesto: {presupuesto_min} - {presupuesto_max}")
            self.logger.info(f"[QUANTITATIVE] Precio de moto {moto.get('id')}: {precio_moto}")
            
            # Aplicar EXACTAMENTE las reglas solicitadas
            if presupuesto_min <= precio_moto <= presupuesto_max:
                total_score += 3
                reasons.append(f"✓ DENTRO del rango de presupuesto ({precio_moto:,.0f}€) [+3]")
                self.logger.info(f"[QUANTITATIVE] DENTRO del presupuesto: +3 puntos")
            elif precio_moto <= presupuesto_max * 1.15:  # Hasta 15% por encima
                total_score += 2
                reasons.append(f"⚠ HASTA 15% por encima del presupuesto ({precio_moto:,.0f}€) [+2]")
                self.logger.info(f"[QUANTITATIVE] Hasta 15% por encima: +2 puntos")
            else:  # Excede significativamente
                total_score += 0
                reasons.append(f"✗ EXCEDE significativamente el presupuesto ({precio_moto:,.0f}€) [0]")
                self.logger.info(f"[QUANTITATIVE] Excede significativamente: 0 puntos")
        else:
            # Fallback si no hay rangos
            self.logger.warning(f"[QUANTITATIVE] NO hay rangos de presupuesto en preferencias!")
            if 'presupuesto' in user_preferences:
                presupuesto = float(user_preferences['presupuesto'])
                if precio_moto <= presupuesto:
                    total_score += 3
                    reasons.append(f"✓ Dentro del presupuesto ({precio_moto:,.0f}€) [+3]")
        
        # 2. MARCAS - Aplicar ponderación
        if 'marcas' in user_preferences:
            marca_moto = str(moto.get('marca', '')).lower()
            self.logger.info(f"[QUANTITATIVE] Evaluando marca: {marca_moto}")
            for marca, peso_marca in user_preferences['marcas'].items():
                if marca.lower() in marca_moto:
                    puntos = float(peso_marca) * 5.0  # Aumentar peso de marcas
                    total_score += puntos
                    reasons.append(f"✓ Marca preferida: {marca} [+{puntos:.1f}]")
                    self.logger.info(f"[QUANTITATIVE] Marca {marca} coincide: +{puntos:.1f} puntos")
          # 3. ESTILOS - Aplicar ponderación
        if 'estilos' in user_preferences:
            tipo_moto = str(moto.get('tipo', '')).lower()
            self.logger.info(f"[QUANTITATIVE] Evaluando tipo: {tipo_moto}")
            for estilo, peso_estilo in user_preferences['estilos'].items():
                if estilo.lower() in tipo_moto:
                    puntos = float(peso_estilo) * 6.0  # Aumentar peso de estilos
                    total_score += puntos
                    reasons.append(f"✓ Estilo preferido: {estilo} [+{puntos:.1f}]")
                    self.logger.info(f"[QUANTITATIVE] Estilo {estilo} coincide: +{puntos:.1f} puntos")
        
        # 4. AÑO - Evaluar rango de años
        if 'ano_min' in user_preferences and 'ano_max' in user_preferences:
            ano_moto = int(moto.get('ano', 2020))
            ano_min = int(user_preferences['ano_min'])
            ano_max = int(user_preferences['ano_max'])
            
            if ano_min <= ano_moto <= ano_max:
                total_score += 2
                reasons.append(f"✓ Año dentro del rango preferido ({ano_moto}) [+2]")
            else:
                penalty = min(1.5, abs(ano_moto - ((ano_min + ano_max) / 2)) / 5)
                total_score -= penalty
                reasons.append(f"⚠ Año fuera del rango preferido ({ano_moto}) [-{penalty:.1f}]")
        
        # 5. PESO - Evaluar rango de peso
        if 'peso_min' in user_preferences and 'peso_max' in user_preferences:
            peso_moto = float(moto.get('peso', 0))
            peso_min = float(user_preferences['peso_min'])
            peso_max = float(user_preferences['peso_max'])
            
            if peso_min <= peso_moto <= peso_max:
                total_score += 2
                reasons.append(f"✓ Peso dentro del rango preferido ({peso_moto}kg) [+2]")
            else:
                penalty = min(1.0, abs(peso_moto - ((peso_min + peso_max) / 2)) / 50)
                total_score -= penalty
                reasons.append(f"⚠ Peso fuera del rango preferido ({peso_moto}kg) [-{penalty:.1f}]")
        
        # 6. POTENCIA - Evaluar rango de potencia
        if 'potencia_min' in user_preferences and 'potencia_max' in user_preferences:
            potencia_moto = float(moto.get('potencia', 0))
            potencia_min = float(user_preferences['potencia_min'])
            potencia_max = float(user_preferences['potencia_max'])
            
            if potencia_min <= potencia_moto <= potencia_max:
                total_score += 3
                reasons.append(f"✓ Potencia dentro del rango preferido ({potencia_moto}CV) [+3]")
            else:
                penalty = min(2.0, abs(potencia_moto - ((potencia_min + potencia_max) / 2)) / 30)
                total_score -= penalty
                reasons.append(f"⚠ Potencia fuera del rango preferido ({potencia_moto}CV) [-{penalty:.1f}]")
        
        # 7. CILINDRADA - Evaluar rango de cilindrada
        if 'cilindrada_min' in user_preferences and 'cilindrada_max' in user_preferences:
            cilindrada_moto = float(moto.get('cilindrada', 0))
            cilindrada_min = float(user_preferences['cilindrada_min'])
            cilindrada_max = float(user_preferences['cilindrada_max'])
            
            if cilindrada_min <= cilindrada_moto <= cilindrada_max:
                total_score += 2
                reasons.append(f"✓ Cilindrada dentro del rango preferido ({cilindrada_moto}cc) [+2]")
            else:
                penalty = min(1.5, abs(cilindrada_moto - ((cilindrada_min + cilindrada_max) / 2)) / 200)
                total_score -= penalty
                reasons.append(f"⚠ Cilindrada fuera del rango preferido ({cilindrada_moto}cc) [-{penalty:.1f}]")
        
        # 8. TORQUE - Evaluar rango de torque
        if 'torque_min' in user_preferences and 'torque_max' in user_preferences:
            torque_moto = float(moto.get('torque', 0))
            torque_min = float(user_preferences['torque_min'])
            torque_max = float(user_preferences['torque_max'])
            
            if torque_min <= torque_moto <= torque_max:
                total_score += 2
                reasons.append(f"✓ Torque dentro del rango preferido ({torque_moto}Nm) [+2]")
            else:
                penalty = min(1.0, abs(torque_moto - ((torque_min + torque_max) / 2)) / 20)
                total_score -= penalty
                reasons.append(f"⚠ Torque fuera del rango preferido ({torque_moto}Nm) [-{penalty:.1f}]")
        
        self.logger.info(f"[QUANTITATIVE] Moto {moto.get('id')} - Score cuantitativo: {total_score}")
        
        # INTEGRAR EVALUACIÓN CUALITATIVA
        qualitative_score, qualitative_reasons = self.qualitative_evaluator.evaluate_moto_qualitative(
            user_preferences, moto
        )
        
        # Aplicar factor de peso cualitativo basado en experiencia del usuario
        qualitative_weight = self.qualitative_evaluator.get_qualitative_weight_factor(user_preferences)
        weighted_qualitative_score = qualitative_score * qualitative_weight
        
        # Combinar puntuaciones: 70% cuantitativo, 30% cualitativo
        quantitative_weight = 0.7
        qualitative_final_weight = 0.3
        
        final_score = (total_score * quantitative_weight) + (weighted_qualitative_score * qualitative_final_weight)
        
        # Combinar razones
        final_reasons = reasons + [f"--- Evaluación Cualitativa (peso: {qualitative_final_weight}) ---"] + qualitative_reasons
        final_reasons.append(f"[FINAL] Score cuantitativo: {total_score:.1f} | Score cualitativo: {weighted_qualitative_score:.1f} | Score final: {final_score:.1f}")
        self.logger.info(f"[COMBINED] Moto {moto.get('id')} - Score FINAL: {final_score:.1f} (Cuant: {total_score:.1f} + Cual: {weighted_qualitative_score:.1f})")
        
        return final_score, final_reasons
