"""
Modelos de datos para la aplicación MotoMatch con compatibilidad Neo4j
"""

class User:
    """Modelo de usuario"""
    
    def __init__(self, id=None, username=None, email=None, **kwargs):
        self.id = id
        self.username = username
        self.email = email
        self._preferences = None
        
        # Propiedades adicionales
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @property
    def preferences(self):
        """Obtiene las preferencias del usuario"""
        return self._preferences
    
    @preferences.setter
    def preferences(self, value):
        """Establece las preferencias del usuario"""
        self._preferences = value


class Moto:
    """Modelo de motocicleta"""
    
    def __init__(self, id=None, marca=None, modelo=None, **kwargs):
        self.id = id
        self.marca = marca
        self.modelo = modelo
        
        # Propiedades adicionales
        for key, value in kwargs.items():
            setattr(self, key, value)


class UserPreference:
    """Modelo de preferencias de usuario"""
    
    def __init__(self, user=None, **kwargs):
        self.user = user
        self.estilos_preferidos = kwargs.get('estilos_preferidos', {})
        self.marcas_preferidas = kwargs.get('marcas_preferidas', {})
        self.experiencia = kwargs.get('experiencia', '')
        self.presupuesto = kwargs.get('presupuesto', 0)
        self.uso_previsto = kwargs.get('uso_previsto', '')
        self.datos_test = kwargs.get('datos_test', {})
        
        # Propiedades adicionales
        for key, value in kwargs.items():
            if key not in ['estilos_preferidos', 'marcas_preferidas', 'experiencia', 
                          'presupuesto', 'uso_previsto', 'datos_test']:
                setattr(self, key, value)