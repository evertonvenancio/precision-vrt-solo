"""
Precision VRT Solo — Submódulo de Exportação

Suporta todos os formatos especificados: PDF, CSV, Excel, GeoJSON, Shapefile, GeoTIFF.
Nunca cria exportadores específicos para fabricantes.
"""

from .motor import (
    ConfigExportadorPDF,
    ConfigExportadorCSV,
    ConfigExportadorExcel,
    ExportadorPDF,
    ExportadorCSV,
    ExportadorExcel,
    ExportadorGeoJSON,
    ExportadorShapefile,
    ExportadorGeoTIFF,
    MotorExportacao
)

__all__ = [
    'ConfigExportadorPDF',
    'ConfigExportadorCSV',
    'ConfigExportadorExcel',
    'ExportadorPDF',
    'ExportadorCSV',
    'ExportadorExcel',
    'ExportadorGeoJSON',
    'ExportadorShapefile',
    'ExportadorGeoTIFF',
    'MotorExportacao'
]