# config/culturas.py
# Base Tecnica de Culturas - Precision VRT Solo
# Dados agronomicos baseados em medias da Embrapa e SBCS

CULTURAS = {
    # --- GRAMINEAS DE GRAOS ---
    "milho": {
        "nome": "Milho",
        "nome_cientifico": "Zea mays L.",
        "unidade_produtividade": "sc/ha",
        "exportacao_nutrientes": {
            "N": 18.0, "P2O5": 4.5, "K2O": 5.2, "CaO": 1.2, "MgO": 1.0, "S": 1.5,
            "B": 0.008, "Zn": 0.025, "Fe": 0.015, "Mn": 0.012, "Cu": 0.003
        },
        "meta_produtividade_padrao": 80,
        "eficiencia_fertilizante": {
            "N": 0.60, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Milho e Sorgo - Boletim Tecnico 201",
        "bibliografia": "FAGERIA, N. K.; BALIGAR, V. C.; JONES, C. A. Growth and Mineral Nutrition of Field Crops. 3rd ed. CRC Press, 2011. 600 p."
    },
    "soja": {
        "nome": "Soja",
        "nome_cientifico": "Glycine max (L.) Merr.",
        "unidade_produtividade": "sc/ha",
        "exportacao_nutrientes": {
            "N": 50.0, "P2O5": 6.0, "K2O": 18.0, "CaO": 3.5, "MgO": 2.0, "S": 2.0,
            "B": 0.015, "Zn": 0.035, "Fe": 0.020, "Mn": 0.018, "Cu": 0.005
        },
        "meta_produtividade_padrao": 55,
        "eficiencia_fertilizante": {
            "N": 0.0, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Soja - Circular Tecnica 48",
        "bibliografia": "MOREIRA, A.; MORAES, L. A. C.; SCHROTH, G. Adubacao e nutricao da soja. In: Tecnologias de Producao de Soja. EMBRAPA Soja, 2018. p. 45-92."
    },
    "trigo": {
        "nome": "Trigo",
        "nome_cientifico": "Triticum aestivum L.",
        "unidade_produtividade": "sc/ha",
        "exportacao_nutrientes": {
            "N": 22.0, "P2O5": 5.0, "K2O": 5.5, "CaO": 1.5, "MgO": 1.2, "S": 1.8,
            "B": 0.006, "Zn": 0.020, "Fe": 0.012, "Mn": 0.010, "Cu": 0.002
        },
        "meta_produtividade_padrao": 45,
        "eficiencia_fertilizante": {
            "N": 0.55, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "Comite Tecnico Sul-Brasileiro de Pesquisa de Trigo - 2023",
        "bibliografia": "COMITE TECNICO SUL-BRASILEIRO DE PESQUISA DE TRIGO. Manual de Trigo. Fundacao ABC, 2023. 312 p."
    },
    "arroz": {
        "nome": "Arroz",
        "nome_cientifico": "Oryza sativa L.",
        "unidade_produtividade": "sc/ha",
        "exportacao_nutrientes": {
            "N": 16.0, "P2O5": 4.0, "K2O": 4.5, "CaO": 1.0, "MgO": 0.8, "S": 1.2,
            "B": 0.005, "Zn": 0.018, "Fe": 0.010, "Mn": 0.008, "Cu": 0.002
        },
        "meta_produtividade_padrao": 70,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "SOSBAI - Sistema de Producao de Arroz Irrigado do Rio Grande do Sul",
        "bibliografia": "SOSBAI. Arroz Irrigado: Recomendacoes Tecnicas da Pesquisa para o Sul do Brasil. Bento Goncalves: IRGA, 2024. 196 p."
    },
    "sorgo": {
        "nome": "Sorgo",
        "nome_cientifico": "Sorghum bicolor (L.) Moench",
        "unidade_produtividade": "sc/ha",
        "exportacao_nutrientes": {
            "N": 16.0, "P2O5": 4.2, "K2O": 4.8, "CaO": 1.1, "MgO": 0.9, "S": 1.3,
            "B": 0.007, "Zn": 0.022, "Fe": 0.014, "Mn": 0.011, "Cu": 0.003
        },
        "meta_produtividade_padrao": 60,
        "eficiencia_fertilizante": {
            "N": 0.55, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Milho e Sorgo - Boletim Tecnico 201",
        "bibliografia": "FREITAS, F. C. L.; VIANA, A. H. M.; OLIVEIRA, E. F. de. Nutricao e adubacao do sorgo. Sete Lagoas: EMBRAPA Milho e Sorgo, 2017. 48 p."
    },
    "aveia": {
        "nome": "Aveia",
        "nome_cientifico": "Avena sativa L.",
        "unidade_produtividade": "sc/ha",
        "exportacao_nutrientes": {
            "N": 20.0, "P2O5": 4.5, "K2O": 5.0, "CaO": 1.3, "MgO": 1.0, "S": 1.5,
            "B": 0.006, "Zn": 0.018, "Fe": 0.011, "Mn": 0.009, "Cu": 0.002
        },
        "meta_produtividade_padrao": 40,
        "eficiencia_fertilizante": {
            "N": 0.55, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Trigo - Circular Tecnica 17",
        "bibliografia": "CUNHA, G. R. da; BENIN, G. Sistema de Producao de Aveia. Passo Fundo: EMBRAPA Trigo, 2015. 68 p."
    },
    "cevada": {
        "nome": "Cevada",
        "nome_cientifico": "Hordeum vulgare L.",
        "unidade_produtividade": "sc/ha",
        "exportacao_nutrientes": {
            "N": 18.0, "P2O5": 4.0, "K2O": 4.8, "CaO": 1.2, "MgO": 1.0, "S": 1.4,
            "B": 0.005, "Zn": 0.016, "Fe": 0.010, "Mn": 0.008, "Cu": 0.002
        },
        "meta_produtividade_padrao": 35,
        "eficiencia_fertilizante": {
            "N": 0.55, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Trigo - Circular Tecnica 18",
        "bibliografia": "CUNHA, G. R. da. Sistema de Producao de Cevada. Passo Fundo: EMBRAPA Trigo, 2016. 72 p."
    },
    "girassol": {
        "nome": "Girassol",
        "nome_cientifico": "Helianthus annuus L.",
        "unidade_produtividade": "sc/ha",
        "exportacao_nutrientes": {
            "N": 28.0, "P2O5": 7.0, "K2O": 12.0, "CaO": 2.5, "MgO": 1.8, "S": 2.0,
            "B": 0.012, "Zn": 0.030, "Fe": 0.018, "Mn": 0.015, "Cu": 0.004
        },
        "meta_produtividade_padrao": 25,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Soja - Circular Tecnica 50",
        "bibliografia": "CASTRO, C.; LEITE, R. M. V. B. C. Girassol no Brasil. Londrina: EMBRAPA Soja, 2018. 112 p."
    },
    "canola": {
        "nome": "Canola",
        "nome_cientifico": "Brassica napus L.",
        "unidade_produtividade": "sc/ha",
        "exportacao_nutrientes": {
            "N": 32.0, "P2O5": 7.5, "K2O": 14.0, "CaO": 3.0, "MgO": 2.0, "S": 6.0,
            "B": 0.015, "Zn": 0.035, "Fe": 0.020, "Mn": 0.018, "Cu": 0.005
        },
        "meta_produtividade_padrao": 20,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.50,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Trigo - Circular Tecnica 19",
        "bibliografia": "CUNHA, G. R. da; BENIN, G. Canola no Sistema de Producao Sul-Brasileiro. Passo Fundo: EMBRAPA Trigo, 2017. 56 p."
    },

    # --- LEGUMINOSAS ---
    "feijao": {
        "nome": "Feijao",
        "nome_cientifico": "Phaseolus vulgaris L.",
        "unidade_produtividade": "sc/ha",
        "exportacao_nutrientes": {
            "N": 35.0, "P2O5": 5.5, "K2O": 12.0, "CaO": 2.5, "MgO": 1.5, "S": 1.8,
            "B": 0.012, "Zn": 0.030, "Fe": 0.018, "Mn": 0.015, "Cu": 0.004
        },
        "meta_produtividade_padrao": 25,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Arroz e Feijao - Circular Tecnica 183",
        "bibliografia": "FAGERIA, N. K.; SANTOS, A. B. dos; MORAES, M. F. Nutricao mineral do feijoeiro. Santo Antonio de Goias: EMBRAPA Arroz e Feijao, 2015. 48 p."
    },
    "amendoim": {
        "nome": "Amendoim",
        "nome_cientifico": "Arachis hypogaea L.",
        "unidade_produtividade": "sc/ha",
        "exportacao_nutrientes": {
            "N": 40.0, "P2O5": 8.0, "K2O": 14.0, "CaO": 3.0, "MgO": 2.0, "S": 2.5,
            "B": 0.015, "Zn": 0.035, "Fe": 0.022, "Mn": 0.018, "Cu": 0.005
        },
        "meta_produtividade_padrao": 30,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Agropecuaria Oeste - Circular Tecnica 108",
        "bibliografia": "GODOY, I. J. de. Amendoim: Tecnologia de Producao. Dourados: EMBRAPA Agropecuaria Oeste, 2016. 64 p."
    },

    # --- FIBRA ---
    "algodao": {
        "nome": "Algodao",
        "nome_cientifico": "Gossypium hirsutum L.",
        "unidade_produtividade": "sc/ha",
        "exportacao_nutrientes": {
            "N": 25.0, "P2O5": 8.0, "K2O": 15.0, "CaO": 4.0, "MgO": 2.5, "S": 2.5,
            "B": 0.020, "Zn": 0.040, "Fe": 0.025, "Mn": 0.020, "Cu": 0.006
        },
        "meta_produtividade_padrao": 40,
        "eficiencia_fertilizante": {
            "N": 0.55, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "APLA - Associacao Paulista de Algodao",
        "bibliografia": "BELTRAO, N. E. de M.; LIMA, L. M. de. Manual de Adubacao do Algodoeiro. Campina Grande: EMBRAPA Algodao, 2018. 92 p."
    },

    # --- CAFE ---
    "cafe_arabica": {
        "nome": "Cafe Arabica",
        "nome_cientifico": "Coffea arabica L.",
        "unidade_produtividade": "sc/ha",
        "exportacao_nutrientes": {
            "N": 35.0, "P2O5": 6.0, "K2O": 25.0, "CaO": 5.0, "MgO": 3.0, "S": 2.0,
            "B": 0.025, "Zn": 0.030, "Fe": 0.020, "Mn": 0.015, "Cu": 0.005
        },
        "meta_produtividade_padrao": 30,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EPAMIG/UFV - Manual de Cafeicultura",
        "bibliografia": "GUIMARAES, R. J.; GARCIA, A. W. R.; MARTINEZ, H. E. P. Nutricao e adubacao do cafeeiro. In: Manual de Cafeicultura. Lavras: EPAMIG/UFV, 2019. p. 287-340."
    },
    "cafe_conilon": {
        "nome": "Cafe Conilon",
        "nome_cientifico": "Coffea canephora Pierre ex A. Froehner",
        "unidade_produtividade": "sc/ha",
        "exportacao_nutrientes": {
            "N": 40.0, "P2O5": 7.0, "K2O": 30.0, "CaO": 6.0, "MgO": 3.5, "S": 2.5,
            "B": 0.030, "Zn": 0.035, "Fe": 0.022, "Mn": 0.018, "Cu": 0.006
        },
        "meta_produtividade_padrao": 35,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Cafe - Circular Tecnica 115",
        "bibliografia": "BRAGANCA, S. M.; MARTINEZ, H. E. P.; GUIMARAES, R. J. Nutricao do cafeeiro conilon. In: Cafe Conilon. Vitoria: INCAPER, 2017. p. 215-260."
    },

    # --- CANA ---
    "cana": {
        "nome": "Cana-de-Acucar",
        "nome_cientifico": "Saccharum officinarum L.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 1.2, "P2O5": 0.3, "K2O": 1.8, "CaO": 0.4, "MgO": 0.3, "S": 0.2,
            "B": 0.001, "Zn": 0.003, "Fe": 0.002, "Mn": 0.001, "Cu": 0.0005
        },
        "meta_produtividade_padrao": 80,
        "eficiencia_fertilizante": {
            "N": 0.60, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "IAC - Boletim Tecnico 200",
        "bibliografia": "VAN RAIJ, B.; CANTARELLA, H.; QUAGGIO, J. A.; FURLANI, A. M. C. Recomendacao de adubacao e calagem para o Estado de Sao Paulo. 2. ed. Campinas: IAC, 1996. 285 p. (Boletim Tecnico, 100)."
    },

    # --- HORTICULTURAS ---
    "tomate": {
        "nome": "Tomate",
        "nome_cientifico": "Solanum lycopersicum L.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 3.0, "P2O5": 1.0, "K2O": 5.0, "CaO": 2.5, "MgO": 0.8, "S": 0.6,
            "B": 0.005, "Zn": 0.012, "Fe": 0.008, "Mn": 0.006, "Cu": 0.001
        },
        "meta_produtividade_padrao": 60,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Hortalicas - Circular Tecnica 76",
        "bibliografia": "FILGUEIRA, F. A. R. Novo Manual de Olericultura: Agrotecnologia Moderna na Producao e Comercializacao de Hortalicas. 3. ed. Vicosa: UFV, 2012. 421 p."
    },
    "batata": {
        "nome": "Batata",
        "nome_cientifico": "Solanum tuberosum L.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 4.0, "P2O5": 1.5, "K2O": 6.0, "CaO": 1.5, "MgO": 0.6, "S": 0.5,
            "B": 0.004, "Zn": 0.010, "Fe": 0.006, "Mn": 0.005, "Cu": 0.001
        },
        "meta_produtividade_padrao": 30,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Hortalicas - Circular Tecnica 78",
        "bibliografia": "FONTES, P. C. R. Adubacao da batata. In: Adubacao de Hortalicas. Vicosa: UFV, 2016. p. 145-178."
    },
    "cebola": {
        "nome": "Cebola",
        "nome_cientifico": "Allium cepa L.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 2.5, "P2O5": 1.0, "K2O": 3.5, "CaO": 1.2, "MgO": 0.5, "S": 1.0,
            "B": 0.006, "Zn": 0.012, "Fe": 0.007, "Mn": 0.006, "Cu": 0.001
        },
        "meta_produtividade_padrao": 40,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Hortalicas - Circular Tecnica 82",
        "bibliografia": "RESENDE, G. M. de; COSTA, N. D. da. Producao de Cebola. Brasilia: EMBRAPA Hortalicas, 2018. 56 p."
    },
    "alho": {
        "nome": "Alho",
        "nome_cientifico": "Allium sativum L.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 3.5, "P2O5": 1.2, "K2O": 4.5, "CaO": 1.5, "MgO": 0.6, "S": 1.2,
            "B": 0.008, "Zn": 0.015, "Fe": 0.008, "Mn": 0.007, "Cu": 0.001
        },
        "meta_produtividade_padrao": 15,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Hortalicas - Circular Tecnica 83",
        "bibliografia": "RESENDE, G. M. de; COSTA, N. D. da. Producao de Alho. Brasilia: EMBRAPA Hortalicas, 2019. 48 p."
    },
    "pimentao": {
        "nome": "Pimentao",
        "nome_cientifico": "Capsicum annuum L.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 3.5, "P2O5": 1.2, "K2O": 5.5, "CaO": 2.0, "MgO": 0.8, "S": 0.7,
            "B": 0.006, "Zn": 0.014, "Fe": 0.009, "Mn": 0.007, "Cu": 0.001
        },
        "meta_produtividade_padrao": 25,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Hortalicas - Circular Tecnica 77",
        "bibliografia": "FILGUEIRA, F. A. R. Novo Manual de Olericultura. 3. ed. Vicosa: UFV, 2012. p. 289-312."
    },
    "melancia": {
        "nome": "Melancia",
        "nome_cientifico": "Citrullus lanatus (Thunb.) Matsum. & Nakai",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 2.0, "P2O5": 0.8, "K2O": 3.5, "CaO": 1.8, "MgO": 0.6, "S": 0.4,
            "B": 0.003, "Zn": 0.008, "Fe": 0.005, "Mn": 0.004, "Cu": 0.001
        },
        "meta_produtividade_padrao": 40,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Hortalicas - Circular Tecnica 80",
        "bibliografia": "FILGUEIRA, F. A. R. Novo Manual de Olericultura. 3. ed. Vicosa: UFV, 2012. p. 355-372."
    },
    "abobora": {
        "nome": "Abobora",
        "nome_cientifico": "Cucurbita moschata Duchesne",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 2.5, "P2O5": 1.0, "K2O": 4.0, "CaO": 2.0, "MgO": 0.8, "S": 0.5,
            "B": 0.004, "Zn": 0.010, "Fe": 0.006, "Mn": 0.005, "Cu": 0.001
        },
        "meta_produtividade_padrao": 25,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Hortalicas - Circular Tecnica 81",
        "bibliografia": "FILGUEIRA, F. A. R. Novo Manual de Olericultura. 3. ed. Vicosa: UFV, 2012. p. 373-388."
    },

    # --- FRUTICULTURA ---
    "citros": {
        "nome": "Citros",
        "nome_cientifico": "Citrus spp.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 1.8, "P2O5": 0.5, "K2O": 3.0, "CaO": 2.5, "MgO": 0.5, "S": 0.4,
            "B": 0.015, "Zn": 0.018, "Fe": 0.012, "Mn": 0.010, "Cu": 0.004
        },
        "meta_produtividade_padrao": 35,
        "eficiencia_fertilizante": {
            "N": 0.45, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "IAC - Boletim Tecnico 200",
        "bibliografia": "VAN RAIJ, B.; CANTARELLA, H.; QUAGGIO, J. A.; FURLANI, A. M. C. Recomendacao de adubacao e calagem para o Estado de Sao Paulo. 2. ed. Campinas: IAC, 1996. 285 p."
    },
    "manga": {
        "nome": "Manga",
        "nome_cientifico": "Mangifera indica L.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 2.0, "P2O5": 0.6, "K2O": 3.5, "CaO": 2.0, "MgO": 0.6, "S": 0.3,
            "B": 0.010, "Zn": 0.015, "Fe": 0.010, "Mn": 0.008, "Cu": 0.003
        },
        "meta_produtividade_padrao": 25,
        "eficiencia_fertilizante": {
            "N": 0.40, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Semi-Arido - Circular Tecnica 112",
        "bibliografia": "DONADIO, L. C.; MARTINS, F. de P.; NOGUEIRA, D. J. Manga: Producao e Mercado. Jaboticabal: Funep, 2015. 320 p."
    },
    "uva": {
        "nome": "Uva",
        "nome_cientifico": "Vitis vinifera L.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 2.5, "P2O5": 0.8, "K2O": 4.0, "CaO": 2.5, "MgO": 0.8, "S": 0.4,
            "B": 0.012, "Zn": 0.020, "Fe": 0.012, "Mn": 0.010, "Cu": 0.004
        },
        "meta_produtividade_padrao": 20,
        "eficiencia_fertilizante": {
            "N": 0.45, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EPAGRI - Sistema de Producao Uva",
        "bibliografia": "MIELE, A.; RIZZON, L. A. Manual de Viticultura. Bento Goncalves: EMBRAPA Uva e Vinho, 2017. 412 p."
    },
    "maca": {
        "nome": "Maca",
        "nome_cientifico": "Malus domestica Borkh.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 1.5, "P2O5": 0.5, "K2O": 2.5, "CaO": 1.5, "MgO": 0.4, "S": 0.3,
            "B": 0.010, "Zn": 0.012, "Fe": 0.010, "Mn": 0.008, "Cu": 0.003
        },
        "meta_produtividade_padrao": 30,
        "eficiencia_fertilizante": {
            "N": 0.40, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EPAGRI - Sistema de Producao Maca",
        "bibliografia": "PETRI, J. L.; LEITE, G. B. Macieira: Producao. Florianopolis: EPAGRI, 2018. 256 p."
    },
    "banana": {
        "nome": "Banana",
        "nome_cientifico": "Musa spp.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 3.0, "P2O5": 1.0, "K2O": 8.0, "CaO": 2.5, "MgO": 1.0, "S": 0.5,
            "B": 0.008, "Zn": 0.020, "Fe": 0.012, "Mn": 0.010, "Cu": 0.003
        },
        "meta_produtividade_padrao": 40,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Mandioca e Fruticultura - Circular Tecnica 98",
        "bibliografia": "SILVA, S. de O. da; ALVES, E. J. Cultivo da Banana: Tecnologias e Perspectivas. Cruz das Almas: EMBRAPA Mandioca e Fruticultura, 2016. 180 p."
    },

    # --- FLORESTAS ---
    "eucalipto": {
        "nome": "Eucalipto",
        "nome_cientifico": "Eucalyptus spp.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 3.5, "P2O5": 0.8, "K2O": 2.5, "CaO": 4.0, "MgO": 1.5, "S": 0.5,
            "B": 0.006, "Zn": 0.015, "Fe": 0.010, "Mn": 0.008, "Cu": 0.002
        },
        "meta_produtividade_padrao": 35,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "IPEF - Instituto de Pesquisas e Estudos Florestais",
        "bibliografia": "GONCALVES, J. L. M.; BENEDETTI, V. Nutricao e fertilidade do solo para plantacoes florestais. Piracicaba: IPEF/ESALQ, 2015. 245 p."
    },
    "pinus": {
        "nome": "Pinus",
        "nome_cientifico": "Pinus spp.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 2.5, "P2O5": 0.5, "K2O": 1.5, "CaO": 3.0, "MgO": 1.0, "S": 0.3,
            "B": 0.004, "Zn": 0.010, "Fe": 0.008, "Mn": 0.006, "Cu": 0.001
        },
        "meta_produtividade_padrao": 25,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "IPEF - Instituto de Pesquisas e Estudos Florestais",
        "bibliografia": "GONCALVES, J. L. M.; BENEDETTI, V. Nutricao e fertilidade do solo para plantacoes florestais. Piracicaba: IPEF/ESALQ, 2015. 245 p."
    },
    "seringueira": {
        "nome": "Seringueira",
        "nome_cientifico": "Hevea brasiliensis (Willd. ex A. Juss.) Mull. Arg.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 3.0, "P2O5": 0.6, "K2O": 2.0, "CaO": 3.5, "MgO": 1.2, "S": 0.4,
            "B": 0.005, "Zn": 0.012, "Fe": 0.009, "Mn": 0.007, "Cu": 0.002
        },
        "meta_produtividade_padrao": 20,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Amazonia Ocidental - Circular Tecnica 45",
        "bibliografia": "GONCALVES, P. de S. et al. Manual de Instrucoes para o Plantio da Seringueira. Manaus: EMBRAPA Amazonia Ocidental, 2017. 68 p."
    },

    # --- PASTAGENS ---
    "brachiaria": {
        "nome": "Brachiaria",
        "nome_cientifico": "Urochloa spp.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 2.0, "P2O5": 0.5, "K2O": 2.5, "CaO": 1.0, "MgO": 0.5, "S": 0.3,
            "B": 0.003, "Zn": 0.008, "Fe": 0.005, "Mn": 0.004, "Cu": 0.001
        },
        "meta_produtividade_padrao": 12,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Gado de Corte - Circular Tecnica 36",
        "bibliografia": "EUCLIDES, V. P. B. et al. Sistema de Producao de Gado de Corte. Campo Grande: EMBRAPA Gado de Corte, 2018. 156 p."
    },
    "panicum": {
        "nome": "Panicum",
        "nome_cientifico": "Megathyrsus maximus (Jacq.) B. K. Simon & S. W. L. Jacobs",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 2.2, "P2O5": 0.6, "K2O": 3.0, "CaO": 1.2, "MgO": 0.6, "S": 0.3,
            "B": 0.003, "Zn": 0.009, "Fe": 0.006, "Mn": 0.005, "Cu": 0.001
        },
        "meta_produtividade_padrao": 15,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Gado de Corte - Circular Tecnica 37",
        "bibliografia": "EUCLIDES, V. P. B. et al. Sistema de Producao de Gado de Corte. Campo Grande: EMBRAPA Gado de Corte, 2018. 156 p."
    },
    "andropogon": {
        "nome": "Andropogon",
        "nome_cientifico": "Andropogon gayanus Kunth",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 1.8, "P2O5": 0.4, "K2O": 2.0, "CaO": 0.8, "MgO": 0.4, "S": 0.2,
            "B": 0.002, "Zn": 0.007, "Fe": 0.005, "Mn": 0.004, "Cu": 0.001
        },
        "meta_produtividade_padrao": 10,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Gado de Corte - Circular Tecnica 38",
        "bibliografia": "EUCLIDES, V. P. B. et al. Sistema de Producao de Gado de Corte. Campo Grande: EMBRAPA Gado de Corte, 2018. 156 p."
    },

    # --- OUTRAS ---
    "cacau": {
        "nome": "Cacau",
        "nome_cientifico": "Theobroma cacao L.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 2.5, "P2O5": 0.8, "K2O": 4.0, "CaO": 2.0, "MgO": 1.0, "S": 0.4,
            "B": 0.008, "Zn": 0.015, "Fe": 0.010, "Mn": 0.008, "Cu": 0.003
        },
        "meta_produtividade_padrao": 15,
        "eficiencia_fertilizante": {
            "N": 0.40, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "CEPLAC/EMBRAPA Cacau - Circular Tecnica 55",
        "bibliografia": "SOUZA, J. M. T. de; RESENDE, M. L. V. de. Cacau: Producao e Manejo. Ilheus: CEPLAC/EMBRAPA Cacau, 2016. 220 p."
    },
    "dende": {
        "nome": "Dende",
        "nome_cientifico": "Elaeis guineensis Jacq.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 3.5, "P2O5": 1.0, "K2O": 6.0, "CaO": 2.5, "MgO": 1.2, "S": 0.5,
            "B": 0.008, "Zn": 0.020, "Fe": 0.012, "Mn": 0.010, "Cu": 0.003
        },
        "meta_produtividade_padrao": 20,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Amazonia Oriental - Circular Tecnica 42",
        "bibliografia": "CLEMENT, C. R. et al. Dende: Cultivo e Manejo. Belem: EMBRAPA Amazonia Oriental, 2018. 180 p."
    },
    "mandioca": {
        "nome": "Mandioca",
        "nome_cientifico": "Manihot esculenta Crantz",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 2.5, "P2O5": 0.8, "K2O": 4.5, "CaO": 1.5, "MgO": 0.8, "S": 0.4,
            "B": 0.004, "Zn": 0.010, "Fe": 0.006, "Mn": 0.005, "Cu": 0.001
        },
        "meta_produtividade_padrao": 25,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "EMBRAPA Mandioca e Fruticultura - Circular Tecnica 95",
        "bibliografia": "FUKUDA, W. M. G.; GUEVARA, C. L. Mandioca: Producao e Manejo. Cruz das Almas: EMBRAPA Mandioca e Fruticultura, 2017. 156 p."
    },
    "tabaco": {
        "nome": "Tabaco",
        "nome_cientifico": "Nicotiana tabacum L.",
        "unidade_produtividade": "t/ha",
        "exportacao_nutrientes": {
            "N": 4.5, "P2O5": 1.5, "K2O": 8.0, "CaO": 5.0, "MgO": 1.5, "S": 1.0,
            "B": 0.010, "Zn": 0.025, "Fe": 0.015, "Mn": 0.012, "Cu": 0.003
        },
        "meta_produtividade_padrao": 3,
        "eficiencia_fertilizante": {
            "N": 0.50, "P2O5": 0.20, "K2O": 0.50, "CaO": 0.30, "MgO": 0.25, "S": 0.40,
            "B": 0.15, "Zn": 0.10, "Fe": 0.08, "Mn": 0.08, "Cu": 0.05
        },
        "fonte_dados": "SINDITABACO - Manual de Cultivo do Tabaco",
        "bibliografia": "SINDITABACO. Manual de Cultivo do Tabaco no Brasil. Rio Negro: SINDITABACO, 2019. 280 p."
    },
}


def get_cultura(nome_cultura):
    """Retorna a configuracao completa de uma cultura pelo nome chave."""
    cultura = CULTURAS.get(nome_cultura.lower())
    if not cultura:
        raise ValueError("Cultura nao encontrada")
    return cultura


def calcular_exportacao(cultura, produtividade):
    """Calcula a exportacao de nutrientes em kg/ha para uma dada produtividade."""
    config = get_cultura(cultura)
    if config["unidade_produtividade"] == "sc/ha":
        toneladas_ha = (produtividade * 60) / 1000
    else:
        toneladas_ha = produtividade
    exportacao = {}
    for nutriente, kg_por_t in config["exportacao_nutrientes"].items():
        exportacao[nutriente] = round(kg_por_t * toneladas_ha, 2)
    return exportacao


def listar_culturas():
    """Retorna lista ordenada de tuplas (chave, nome) para dropdowns."""
    return sorted([(k, v["nome"]) for k, v in CULTURAS.items()])