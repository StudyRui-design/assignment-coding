# -*- coding: utf-8 -*-
"""
Oxford 102 Flowers dataset — official English category names.
Source: torchvision.datasets.Flowers102.classes
Each index (0-101) maps to the corresponding folder name "001"-"102"
in the checkpoint's class_names list.
"""

FLOWER_NAMES = [
    "pink primrose",              # 001 / index 0
    "hard-leaved pocket orchid",  # 002 / index 1
    "canterbury bells",           # 003 / index 2
    "sweet pea",                  # 004 / index 3
    "english marigold",           # 005 / index 4
    "tiger lily",                 # 006 / index 5
    "moon orchid",                # 007 / index 6
    "bird of paradise",           # 008 / index 7
    "monkshood",                  # 009 / index 8
    "globe thistle",              # 010 / index 9
    "snapdragon",                 # 011 / index 10
    "colt's foot",                # 012 / index 11
    "king protea",                # 013 / index 12
    "spear thistle",              # 014 / index 13
    "yellow iris",                # 015 / index 14
    "globe-flower",               # 016 / index 15
    "purple coneflower",          # 017 / index 16
    "peruvian lily",              # 018 / index 17
    "balloon flower",             # 019 / index 18
    "giant white arum lily",      # 020 / index 19
    "fire lily",                  # 021 / index 20
    "pincushion flower",          # 022 / index 21
    "fritillary",                 # 023 / index 22
    "red ginger",                 # 024 / index 23
    "grape hyacinth",             # 025 / index 24
    "corn poppy",                 # 026 / index 25
    "prince of wales feathers",   # 027 / index 26
    "stemless gentian",           # 028 / index 27
    "artichoke",                  # 029 / index 28
    "sweet william",              # 030 / index 29
    "carnation",                  # 031 / index 30
    "garden phlox",               # 032 / index 31
    "love in the mist",           # 033 / index 32
    "mexican aster",              # 034 / index 33
    "alpine sea holly",           # 035 / index 34
    "ruby-lipped cattleya",       # 036 / index 35
    "cape flower",                # 037 / index 36
    "great masterwort",           # 038 / index 37
    "siam tulip",                 # 039 / index 38
    "lenten rose",                # 040 / index 39
    "barbeton daisy",             # 041 / index 40
    "daffodil",                   # 042 / index 41
    "sword lily",                 # 043 / index 42
    "poinsettia",                 # 044 / index 43
    "bolero deep blue",           # 045 / index 44
    "wallflower",                 # 046 / index 45
    "marigold",                   # 047 / index 46
    "buttercup",                  # 048 / index 47
    "oxeye daisy",                # 049 / index 48
    "common dandelion",           # 050 / index 49
    "petunia",                    # 051 / index 50
    "wild pansy",                 # 052 / index 51
    "primula",                    # 053 / index 52
    "sunflower",                  # 054 / index 53
    "pelargonium",                # 055 / index 54
    "bishop of llandaff",         # 056 / index 55
    "gaura",                      # 057 / index 56
    "geranium",                   # 058 / index 57
    "orange dahlia",              # 059 / index 58
    "pink-yellow dahlia?",        # 060 / index 59
    "cautleya spicata",           # 061 / index 60
    "japanese anemone",           # 062 / index 61
    "black-eyed susan",           # 063 / index 62
    "silverbush",                 # 064 / index 63
    "californian poppy",          # 065 / index 64
    "osteospermum",               # 066 / index 65
    "spring crocus",              # 067 / index 66
    "bearded iris",               # 068 / index 67
    "windflower",                 # 069 / index 68
    "tree poppy",                 # 070 / index 69
    "gazania",                    # 071 / index 70
    "azalea",                     # 072 / index 71
    "water lily",                 # 073 / index 72
    "rose",                       # 074 / index 73
    "thorn apple",                # 075 / index 74
    "morning glory",              # 076 / index 75
    "passion flower",             # 077 / index 76
    "lotus",                      # 078 / index 77
    "toad lily",                  # 079 / index 78
    "anthurium",                  # 080 / index 79
    "frangipani",                 # 081 / index 80
    "clematis",                   # 082 / index 81
    "hibiscus",                   # 083 / index 82
    "columbine",                  # 084 / index 83
    "desert-rose",                # 085 / index 84
    "tree mallow",                # 086 / index 85
    "magnolia",                   # 087 / index 86
    "cyclamen",                   # 088 / index 87
    "watercress",                 # 089 / index 88
    "canna lily",                 # 090 / index 89
    "hippeastrum",                # 091 / index 90
    "bee balm",                   # 092 / index 91
    "ball moss",                  # 093 / index 92
    "foxglove",                   # 094 / index 93
    "bougainvillea",              # 095 / index 94
    "camellia",                   # 096 / index 95
    "mallow",                     # 097 / index 96
    "mexican petunia",            # 098 / index 97
    "bromelia",                   # 099 / index 98
    "blanket flower",             # 100 / index 99
    "trumpet creeper",            # 101 / index 100
    "blackberry lily",            # 102 / index 101
]

# Verify count
assert len(FLOWER_NAMES) == 102, f"Expected 102 flower names, got {len(FLOWER_NAMES)}"


def get_flower_name(class_index: int) -> str:
    """Return the English flower name for a given class index (0-101)."""
    if 0 <= class_index < 102:
        return FLOWER_NAMES[class_index]
    return f"Unknown (index {class_index})"


def get_flower_name_by_folder(folder_name: str) -> str:
    """Return the English flower name for a folder name like '001'-'102'."""
    try:
        idx = int(folder_name) - 1
        return get_flower_name(idx)
    except (ValueError, IndexError):
        return f"Unknown ({folder_name})"
