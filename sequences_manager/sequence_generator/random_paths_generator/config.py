SEQUENCE_CONFIG = {
    'starting_node': '1',
    'sceneries_tags': {
        # Biebrza National Park
        "1": ["biebrza_national_park", "fog", "sunrise", "frost"],
        "7": ["biebrza_national_park", "river", "reeds"],
        "16": ["biebrza_national_park", "meadows", "sunrise", "frost"],
        "17": ["biebrza_national_park", "river"],
        "22": ["biebrza_national_park", "river"],

        # Slowinski National Park
        "2": ["slowinski_national_park", "white_dunes", "pioneer_grass"],
        "3": ["slowinski_national_park", "gray_dunes"],
        "8": ["slowinski_national_park", "grasses", "gray_dunes"],
        "13": ["slowinski_national_park", "white_dunes", "clouds"],
        "15": ["slowinski_national_park", "sea", "beach"],
        "23": ["slowinski_national_park", "white_dunes", "grasses"],
        "24": ["slowinski_national_park", "sea", "beach", "grasses"],

        # Table Mountains National Park
        "4": ["table_mountains_national_park", "mountain", "forest"],
        "27": ["table_mountains_national_park", "rocks", "forest"],

        # Tatra National Park
        "5": ["tatra_national_park", "fog", "gentle_peaks"],
        "6": ["tatra_national_park", "fog", "gentle_peaks"],
        "9": ["tatra_national_park", "steep_peaks", "mountain_grasses", "snow"],
        "12": ["tatra_national_park", "steep_peaks", "mountain_grasses", "rocks"],
        "26": ["tatra_national_park", "steep_peaks", "mountain_grasses", "rocks"],
        "18": ["tatra_national_park", "fog", "mountain_pine", "snow"],

        # Ojcow National Park
        "10": ["ojcow_national_park", "fog", "krakow_gate", "limestone_rocks", "forest", "autumn"],
        "11": ["ojcow_national_park", "pradnik_valley", "limestone_rocks"],
        "14": ["ojcow_national_park", "fog", "limestone_rocks", "trees"],
        "21": ["ojcow_national_park", "snow", "limestone_rocks", "winter"],

        # Bieszczady National Park
        "25": ["bieszczady_national_park", "snow", "forest", "fog"]
    },
    'tags_weights': {
        "biebrza_national_park": 3,
        "bieszczady_national_park": 5,
        "krakow_gate": 2,
        "clouds": 1,
        "pradnik_valley": 4,
        "trees": 1,
        "mountain": 1,
        "mountain_grasses": 1,
        "autumn": 2,
        "mountain_pine": 3,
        "gentle_peaks": 1,
        "meadows": 3,
        "forest": 0,
        "fog": 3,
        "sea": 5,
        "ojcow_national_park": 2,
        "beach": 4,
        "table_mountains_national_park": 2,
        "pioneer_grass": 2,
        "river": 3,
        "rocks": 1,
        "limestone_rocks": 3,
        "slowinski_national_park": 4,
        "snow": 2,
        "steep_peaks": 1,
        "frost": 3,
        "tatra_national_park": 0,
        "grasses": 1,
        "reeds": 3,
        "sunrise": 3,
        "white_dunes": 5,
        "gray_dunes": 4,
        "winter": 2
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
        "14": ["18"],
        "15": ["16"],
        "16": ["2", "17"],
        "17": ["23", "13"],
        "18": ["21"],
        "21": ["11", "22"],
        "22": ["23"],
        "23": ["1", "24"],
        "24": ["25", "26"],
        "25": ["8"],
        "26": ["27"],
        "27": ["17"]
    }
}