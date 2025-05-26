"""
Evaluador cuantitativo para el algoritmo de recomendación de motos.
Extiende el sistema actual para manejar rangos numéricos generados por preguntas cuantitativas.
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Any, Optional, Union

logger = logging.getLogger(__name__)

class QuantitativeEvaluator:
    """
    Evaluador que combina criterios cuantitativos (rangos numéricos) 
    con criterios cualitativos (ponderaciones).
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
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
        
        self.logger.info(f"[QUANTITATIVE] Moto {moto.get('id')} - Score FINAL: {total_score}")
        
        return total_score, reasons
