SEQUENCE_CONFIG = {
    'starting_node': '1',
    'sceneries_tags': {
        # Biebrzanski PN
        "1": ["biebrzanski_pn", "mgla", "wschod_slonca", "szron"],
        "7": ["biebrzanski_pn", "rzeka", "trzciny"],
        "16": ["biebrzanski_pn", "laki", "wschod_slonca", "szron"],
        "17": ["biebrzanski_pn", "rzeka"],
        "22": ["biebrzanski_pn", "rzeka"],

        # Slowinki PN
        "2": ["slowinski_pn", "wydmy_biale", "rosliny_pionierskie"],
        "3": ["slowinski_pn", "wydmy_szare"],
        "8": ["slowinski_pn", "trawy", "wydmy_szare"],
        "13": ["slowinski_pn", "wydmy_biale", "chmury"],
        "15": ["slowinski_pn", "morze", "plaza"],
        "23": ["slowinski_pn", "wydmy_biale", "trawy"],
        "24": ["slowinski_pn", "morze", "plaza", "trawy"],

        # PN Gor Stolowych
        "4": ["pn_gor_stolowych", "gora", "las"],
        "27": ["pn_gor_stolowych", "skaly", "las"],

        # Tatrzanski PN
        "5": ["tatrzanski_pn", "mgla", "lagodne_szczyty"],
        "6": ["tatrzanski_pn", "mgla", "lagodne_szczyty"],
        "9": ["tatrzanski_pn", "strome_szczyty", "gorskie_trawy", "snieg"],
        "12": ["tatrzanski_pn", "strome_szczyty", "gorskie_trawy", "skaly"],
        "26": ["tatrzanski_pn", "strome_szczyty", "gorskie_trawy", "skaly"],
        "18": ["tatrzanski_pn", "mgla", "kosodrzewina", "snieg"],

        # Ojcowski PN
        "10": ["ojcowski_pn", "mgla", "brama_krakowska", "skaly_wapienne", "las", "jesien"],
        "11": ["ojcowski_pn", "dolina_pradnika", "skaly_wapienne"],
        "14": ["ojcowski_pn", "mgla", "skaly_wapienne", "drzewa"],
        "21": ["ojcowski_pn", "snieg", "skaly_wapienne", "zima"],

        # Bieszczadzki PN
        "25": ["bieszczadzki_pn", "snieg", "las", "mgla"]
    },
    'tags_weights': {
        "biebrzanski_pn": 3,
        "bieszczadzki_pn": 5,
        "brama_krakowska": 2,
        "chmury": 1,
        "dolina_pradnika": 4,
        "drzewa": 1,
        "gora": 1,
        "gorskie_trawy": 1,
        "jesien": 2,
        "kosodrzewina": 3, # ERROR: unreachable tag
        "lagodne_szczyty": 1,
        "laki": 3,
        "las": 0,
        "mgla": 3,
        "morze": 5,
        "ojcowski_pn": 2,
        "plaza": 4,
        "pn_gor_stolowych": 2,
        "rosliny_pionierskie": 2,
        "rzeka": 3,
        "skaly": 1,
        "skaly_wapienne": 3,
        "slowinski_pn": 4,
        "snieg": 2,
        "strome_szczyty": 1,
        "szron": 3,
        "tatrzanski_pn": 0,
        "trawy": 1,
        "trzciny": 3,
        "wschod_slonca": 3,
        "wydmy_biale": 5,
        "wydmy_szare": 4,
        "zima": 2
    },
    'transitions': {
        "1": ["2"],
        "2": ["3", "6"],
        "3": ["4", "7"],
        "4": ["5", "14"],
        "5": ["15", "25"],
        "6": ["7", "21"],
        "7": ["8"],
        "8": ["9"],
        "9": ["5", "10"],
        "10": ["11"],
        "11": ["5", "12"],
        "12": ["5"],
        "13": ["24"],
        "14": ["13"],
        "15": ["16"],
        "16": ["2", "17"],
        "17": ["23", "13"],
        "18": ["21"], # ERROR: unreachable node
        "21": ["11", "22"],
        "22": ["23"],
        "23": ["1", "24"],
        "24": ["25", "26"],
        "25": ["8"],
        "26": ["27"],
        "27": ["17"]
    }
}