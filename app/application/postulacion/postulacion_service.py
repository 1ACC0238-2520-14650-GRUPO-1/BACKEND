"""
Servicio de Postulación - Enriquecimiento de datos
Agrega información relacionada a las postulaciones (candidato, puesto, empresa)
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from app.infrastructure.postulacion.repositories import PostulacionRepositoryImpl
from app.infrastructure.puesto.repositories import PuestoRepositoryImpl
from app.infrastructure.iam.repositories import CuentaRepositoryImpl


class PostulacionService:
    """Servicio que enriquece datos de postulaciones con información relacionada"""
    
    def __init__(self):
        self.postulacion_repo = PostulacionRepositoryImpl()
        self.puesto_repo = PuestoRepositoryImpl()
        self.cuenta_repo = CuentaRepositoryImpl()
    
    def enriquecer_postulacion(
        self,
        postulacion_data: Dict[str, Any],
        incluir_candidato: bool = True,
        incluir_puesto: bool = True,
        incluir_empresa: bool = True
    ) -> Dict[str, Any]:
        """
        Enriquece una postulación individual con datos relacionados
        
        Args:
            postulacion_data: Datos básicos de la postulación
            incluir_candidato: Si debe incluir info del candidato
            incluir_puesto: Si debe incluir info del puesto
            incluir_empresa: Si debe incluir info de la empresa
            
        Returns:
            Postulación enriquecida con datos relacionados
        """
        postulacion_enriquecida = postulacion_data.copy()
        
        try:
            # Obtener información del candidato
            if incluir_candidato and "candidato_id" in postulacion_data:
                candidato_info = self._obtener_info_candidato(
                    UUID(postulacion_data["candidato_id"])
                )
                if candidato_info:
                    postulacion_enriquecida["candidato"] = candidato_info
            
            # Obtener información del puesto
            if incluir_puesto and "puesto_id" in postulacion_data:
                puesto_info = self._obtener_info_puesto(
                    UUID(postulacion_data["puesto_id"])
                )
                if puesto_info:
                    postulacion_enriquecida["puesto"] = puesto_info
                    
                    # Obtener información de la empresa (si tenemos el puesto)
                    if incluir_empresa and "empresa_id" in puesto_info:
                        empresa_info = self._obtener_info_empresa(
                            UUID(puesto_info["empresa_id"])
                        )
                        if empresa_info:
                            postulacion_enriquecida["empresa"] = empresa_info
        
        except Exception as e:
            # Log del error pero no fallar - devolver datos básicos
            print(f"Error enriqueciendo postulación: {str(e)}")
        
        return postulacion_enriquecida
    
    def enriquecer_postulaciones(
        self,
        postulaciones: List[Dict[str, Any]],
        incluir_candidato: bool = True,
        incluir_puesto: bool = True,
        incluir_empresa: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Enriquece múltiples postulaciones con datos relacionados
        
        Args:
            postulaciones: Lista de postulaciones básicas
            incluir_candidato: Si debe incluir info del candidato
            incluir_puesto: Si debe incluir info del puesto
            incluir_empresa: Si debe incluir info de la empresa
            
        Returns:
            Lista de postulaciones enriquecidas
        """
        return [
            self.enriquecer_postulacion(
                post,
                incluir_candidato=incluir_candidato,
                incluir_puesto=incluir_puesto,
                incluir_empresa=incluir_empresa
            )
            for post in postulaciones
        ]
    
    def _obtener_info_candidato(self, candidato_id: UUID) -> Optional[Dict[str, Any]]:
        """Obtiene información básica del candidato"""
        try:
            cuenta = self.cuenta_repo.obtener_por_id(candidato_id)
            if cuenta:
                return {
                    "cuenta_id": str(candidato_id),
                    "nombre_completo": cuenta.get("nombre_completo", ""),
                    "email": cuenta.get("email", ""),
                    "carrera": cuenta.get("carrera"),
                    "telefono": cuenta.get("telefono"),
                    "ciudad": cuenta.get("ciudad")
                }
        except Exception as e:
            print(f"Error obteniendo candidato {candidato_id}: {str(e)}")
        
        return None
    
    def _obtener_info_puesto(self, puesto_id: UUID) -> Optional[Dict[str, Any]]:
        """Obtiene información básica del puesto"""
        try:
            puesto = self.puesto_repo.obtener_por_id(puesto_id)
            if puesto:
                return {
                    "puesto_id": str(puesto_id),
                    "titulo": puesto.get("titulo", ""),
                    "descripcion": puesto.get("descripcion", ""),
                    "ubicacion": puesto.get("ubicacion", ""),
                    "salario_min": puesto.get("salario_min"),
                    "salario_max": puesto.get("salario_max"),
                    "moneda": puesto.get("moneda", "MXN"),
                    "tipo_contrato": puesto.get("tipo_contrato", ""),
                    "empresa_id": str(puesto.get("empresa_id", ""))
                }
        except Exception as e:
            print(f"Error obteniendo puesto {puesto_id}: {str(e)}")
        
        return None
    
    def _obtener_info_empresa(self, empresa_id: UUID) -> Optional[Dict[str, Any]]:
        """Obtiene información básica de la empresa"""
        try:
            empresa = self.cuenta_repo.obtener_por_id(empresa_id)
            if empresa:
                return {
                    "empresa_id": str(empresa_id),
                    "nombre": empresa.get("nombre_completo", ""),
                    "email": empresa.get("email", "")
                }
        except Exception as e:
            print(f"Error obteniendo empresa {empresa_id}: {str(e)}")
        
        return None
