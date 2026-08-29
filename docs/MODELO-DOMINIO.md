# Precision VRT Solo - Modelo de Domínio
# Documento Contrato entre Interface, Core e Banco de Dados
# Data: 11/07/2026
# Versão: 1.0

## 🎯 **Objetivo**
Definir as entidades fundamentais do sistema para garantir consistência entre interface, core e banco de dados. Este documento serve como "contrato" para evitar retrabalho ao integrar novos módulos.

---

## 🏗️ **Entidades Principais**

### **1. Cultura**
```python
@dataclass
class Cultura:
    """Entidade que representa uma cultura agrícola."""
    id: str
    nome: str  # "Soja", "Milho", "Café", etc.
    nome_cientifico: str  # "Glycine max", "Zea mays", etc.
    ciclo_cultural: int  # Dias do ciclo
    estagios_culturais: List[EstagioCultural]
    parametros_fisiologicos: Dict[str, float]  # Ex: eficiência fotossintética
    restricoes_climaticas: List[RestricaoClimatica]
    created_at: datetime
    updated_at: datetime
```

### **2. Safra**
```python
@dataclass
class Safra:
    """Entidade que representa uma safra agrícola."""
    id: str
    nome: str  # "2024", "2025", "2024-2025", etc.
    data_inicio: datetime
    data_fim: datetime
    cultura: Cultura
    propriedade: Propriedade
    status: SafraStatus  # "planejada", "em_andamento", "concluida"
    observacoes: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### **3. Camada Temática**
```python
@dataclass
class CamadaTematica:
    """Interface conceitual para qualquer camada geoespacial."""
    id: str
    nome: str  # "NDVI_2024", "Produtividade_Safra1", etc.
    tipo_camada: TipoCamada  # "indice_espectral", "mapa_produtividade", "mapa_compactacao", etc.
    fonte_dados: str  # "satelite", "drone", "laboratorio", "sensor"
    safra: Optional[Safra]
    crs: str  # "EPSG:4326", "EPSG:3857", etc.
    geometria: GeoDataFrame
    metadados: Dict[str, Any]  # Índice específico, parâmetros, etc.
    created_at: datetime
    updated_at: datetime
```

### **4. Índice Espectral**
```python
@dataclass
class IndiceEspectral(CamadaTematica):
    """Índice espectral específico (NDVI, NDRE, etc.)."""
    tipo_indice: TipoIndice  # "NDVI", "NDRE", "SAVI", "EVI", etc.
    banda_vermelha: Optional[float]  # Banda vermelha
    banda_infravermelho: Optional[float]  # Banda infravermelho
    banda_azul: Optional[float]  # Banda azul
    banda_verde: Optional[float]  # Banda verde
    fator_correcao: Optional[float]  # Fator de correção
```

### **5. Zona de Manejo**
```python
@dataclass
class ZonaDeManejo:
    """Entidade que representa uma zona de manejo homogênea."""
    id: str
    nome: str  # "Zona_A", "Zona_B", etc.
    area_ha: float
    geometria: GeoDataFrame
    propriedade: Propriedade
    safra: Safra
    caracteristicas: Dict[str, float]  # Teor de nutrientes, pH, etc.
    classificacao: Optional[ClassificacaoZona]
    created_at: datetime
    updated_at: datetime
```

### **6. Ponto de Amostragem**
```python
@dataclass
class PontoDeAmostragem:
    """Entidade que representa um ponto de amostragem no campo."""
    id: str
    codigo: str  # "P001", "P002", etc.
    geometria: Point
    propriedade: Propriedade
    safra: Safra
    zona_manejo: Optional[ZonaDeManejo]
    profundidade: float  # cm
    data_coleta: datetime
    responsavel: str
    observacoes: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### **7. Análise Laboratorial**
```python
@dataclass
class AnaliseLaboratorial:
    """Entidade que representa uma análise laboratorial."""
    id: str
    ponto_amostragem: PontoDeAmostragem
    laboratorio: str
    data_analise: datetime
    resultados: Dict[str, float]  # N, P, K, Ca, Mg, S, pH, etc.
    metodos_analise: Dict[str, str]  # Métodos utilizados
    observacoes: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### **8. Metodologia**
```python
@dataclass
class Metodologia:
    """Entidade que representa uma metodologia de recomendação."""
    id: str
    nome: str  # "IAC", "CFSEMG", "Embrapa", etc.
    instituicao: str  # "IAC", "CFSEMG", "Embrapa", etc.
    descricao: str
    referencia: str  # "Boletim Técnico 100", etc.
    parametros: Dict[str, Any]  # Parâmetros técnicos
    culturas_suportadas: List[Cultura]
    cultivos_suportados: List[Cultivo]
    created_at: datetime
    updated_at: datetime
```

### **9. Recomendação**
```python
@dataclass
class Recomendacao:
    """Entidade que representa uma recomendação técnica."""
    id: str
    zona_manejo: ZonaDeManejo
    cultura: Cultura
    safra: Safra
    metodologia: Metodologia
    recomendacoes_nutrientes: List[RecomendacaoNutriente]
    recomendacoes_corretivos: List[RecomendacaoCorretivo]
    custo_estimado: float
    observacoes: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### **10. Prescrição**
```python
@dataclass
class Prescricao:
    """Entidade que representa uma prescrição completa."""
    id: str
    propriedade: Propriedade
    safra: Safra
    zonas_manejo: List[ZonaDeManejo]
    recomendacoes: List[Recomendacao]
    status: PrescricaoStatus  # "rascunho", "validada", "aprovada", "aplicada"
    created_at: datetime
    updated_at: datetime
```

### **11. Exportação**
```python
@dataclass
class Exportacao:
    """Entidade que representa uma exportação de resultados."""
    id: str
    prescricao: Prescricao
    formato: TipoExportacao  # "caderno_tecnico", "cartao_cabine", "maquina"
    arquivo: str  # Caminho do arquivo gerado
    parametros: Dict[str, Any]  # Parâmetros da exportação
    criado_por: str
    data_criacao: datetime
```

---

## 🎯 **Enumerações**

### **TipoCamada**
```python
class TipoCamada(Enum):
    INDICE_ESPECTRAL = "indice_espectral"
    MAPA_PRODUTIVIDADE = "mapa_produtividade"
    MAPA_COMPACTACAO = "mapa_compactacao"
    MAPA_UMIDADE = "mapa_umidade"
    MAPA_CONDUTIVIDADE = "mapa_condutividade"
    MAPA_ALTITUDE = "mapa_altitude"
    MAPA_DECLIVIDADE = "mapa_declividade"
    MAPA_RELEVO = "mapa_relevo"
    MAPA_DRONE = "mapa_drone"
    MAPA_SENSOR = "mapa_sensor"
    MAPA_LABORATORIO = "mapa_laboratorio"
    OUTRO = "outro"
```

### **TipoIndice**
```python
class TipoIndice(Enum):
    NDVI = "NDVI"
    NDRE = "NDRE"
    GNDVI = "GNDVI"
    EVI = "EVI"
    SAVI = "SAVI"
    MSAVI = "MSAVI"
    OSAVI = "OSAVI"
    VARI = "VARI"
    ARVI = "ARVI"
    CCCI = "CCCI"
    SIPI = "SIPI"
    MCARI = "MCARI"
    MTVI2 = "MTVI2"
    CI_GREEN = "CI_Green"
    CI_RED_EDGE = "CI_Red_Edge"
    LAI = "LAI"
    FAPAR = "FAPAR"
    FRACTIONAL_COVER = "Fractional_Cover"
    BIOMASSA = "Biomassa"
    CLOROFILA = "Clorofila"
    ESTRESSE_HIDRICO = "Estresse_Hidrico"
    TEMPERATURA = "Temperatura"
```

### **SafraStatus**
```python
class SafraStatus(Enum):
    PLANEJADA = "planejada"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
```

### **PrescricaoStatus**
```python
class PrescricaoStatus(Enum):
    RASCUNHO = "rascunho"
    VALIDADA = "validada"
    APROVADA = "aprovada"
    APLICADA = "aplicada"
```

### **TipoExportacao**
```python
class TipoExportacao(Enum):
    CADENO_TECNICO = "caderno_tecnico"
    CARTAO_CABINE = "cartao_cabine"
    MAQUINA = "maquina"
```

---

## 🎯 **Relacionamentos entre Entidades**

```
Cultura ──┬──> Metodologia (culturas_suportadas)
          └──> Safra (cultura)

Safra ──┬──> ZonaDeManejo (safra)
        ├──> PontoDeAmostragem (safra)
        ├──> CamadaTematica (safra)
        └──> Prescricao (safra)

ZonaDeManejo ──┬──> Recomendacao (zona_manejo)
               └──> PontoDeAmostragem (zona_manejo)

PontoDeAmostragem ──> AnaliseLaboratorial (ponto_amostragem)

Recomendacao ──┬──> ZonaDeManejo (zona_manejo)
                ├──> Cultura (cultura)
                └──> Metodologia (metodologia)

Prescricao ──┬──> ZonaDeManejo (zonas_manejo)
              └──> Recomendacao (recomendacoes)

Exportacao ──> Prescricao (prescricao)
```

---

## 🎯 **Regras de Negócio**

### **1. Regra de Safras**
- **Sempre usar `List[Safra]`, nunca safras específicas**
- Permitir combinação de múltiplas safras
- Nunca assumir anos específicos

### **2. Regra de Camadas Temáticas**
- **Sempre usar `CamadaTematica`, não tipos específicos**
- Permitir qualquer tipo de camada geoespacial
- Motor não deve conhecer tipos específicos (NDVI, NDRE, etc.)

### **3. Regra de Metodologias**
- **Sempre usar `Metodologia`, não métodos específicos**
- Permitir adição de novas metodologias sem alterar core
- Cada metodologia define seus próprios parâmetros

### **4. Regra de Culturas**
- **Sempre usar `Cultura`, não culturas específicas**
- Permitir adição de novas culturas sem alterar core
- Cada cultura define seus próprios parâmetros

---

## 🎯 **Contratos entre Camadas**

### **Interface ↔ Core**
- Interface envia `List[CamadaTematica]` para o Core
- Core retorna `Prescricao` para a Interface
- Interface nunca manipula diretamente entidades do Core

### **Core ↔ Banco de Dados**
- Core usa entidades do Modelo de Domínio
- Banco de dados armazena entidades do Modelo de Domínio
- Core isola a lógica de negócio do acesso a dados

### **Core ↔ Config**
- Core usa `ConfigPrescricao` para parâmetros estáticos
- Configuração é injetada, não hardcoded
- Permite mudanças de configuração sem alterar core

---

## 🎯 **Extensões Futuras**

### **Novas Camadas Temáticas**
- Adicionar novo tipo em `TipoCamada`
- Criar classe específica herdando de `CamadaTematica`
- Motor não precisa saber sobre o novo tipo

### **Novas Metodologias**
- Adicionar nova metodologia em `Metodologia`
- Definir parâmetros específicos
- Motor usa interface comum

### **Novas Culturas**
- Adicionar nova cultura em `Cultura`
- Definir parâmetros específicos
- Motor usa interface comum

---

## 🎯 **Documentação do Contrato**

Este documento é o **contrato central** do sistema. Qualquer alteração nas entidades deve ser refletida aqui, e todas as camadas (Interface, Core, Banco de Dados) devem seguir este contrato.

**Próximos Passos:**
1. Implementar as entidades no banco de dados
2. Criar classes de repositório para acesso a dados
3. Implementar o Core usando este modelo
4. Criar interface usando este modelo
5. Testar integração completa

**Versão:** 1.0  
**Data:** 11/07/2026  
**Responsável:** Hermes Agent