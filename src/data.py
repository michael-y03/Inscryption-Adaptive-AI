
# Card Definitions
cards = [
    (0, 0, 0),     # Placeholder for "no card" (ID 0 = empty)
    (0, 1, 0),     # 1  (Squirrel)   : 0 attack, 1 health, 0 blood cost
    (3, 2, 2),     # 2  (Wolf)       : 3 attack, 2 health, 2 blood cost
    (1, 1, 1),     # 3  (Wolf Cub)   : 1 attack, 1 health, 1 blood cost (Fledgling)
    (1, 3, 1),     # 4  (Stoat)      : 1 attack, 3 health, 1 blood cost
    (1, 2, 1),     # 5  (Bullfrog)   : 1 attack, 2 health, 1 blood cost, (Mighty Leap)
    (1, 1, 0),     # 6  (Geck)       : 1 attack, 1 health, 0 blood cost
    (4, 6, 3),     # 7  (Grizzly)    : 4 attack, 6 health, 3 blood cost
    (1, 1, 2),     # 8  (Adder)      : 1 attack, 1 health, 2 blood cost, (Touch Of Death)
    (2, 4, 2),     # 9 (Elk)        : 2 attack, 4 health, 2 blood cost, (Sprinter)  
    (1, 1, 1),     # 10 (Kingfisher) : 1 attack, 1 health, 1 blood cost, (Airborne, Waterborne)
    (1, 1, 1),     # 11 (Mantis)     : 1 attack, 1 health, 1 blood cost, (Bifurcated Strike)
    (1, 2, 1)     # 12 (Porcupine)  : 1 attack, 2 health, 1 blood cost, (Sharp Quills)
]

# Sigil Lookup Data
# Each tuple: ([on_attack_sigils], [special_sigils], [on_turn_end_sigils])
sigil_lookup = [
    ([],  [],  []),     # 0
    ([],  [],  []),     # 1
    ([],  [],  []),     # 2
    ([],  [2], []),     # 3 (Wolf Cub)    :1 - Fledgling
    ([],  [],  []),     # 4
    ([],  [0], []),     # 5 (Bullfrog)    :0 - Mighty Leap
    ([],  [],  []),     # 6
    ([],  [],  []),     # 7
    ([0], [],  []),     # 8 (Adder)       :0 - touch of death
    ([],  [],  [0]),    # 9 (Elk)        :0 - Sprinter
    ([1], [1], []),     # 10 (Kingfisher) :1, 1 - Airborne, Waterborne
    ([2], [],  []),     # 11 (Mantis)     :2 - Bifurcated Strike
    ([],  [3], [])     # 12 (Porcupine)  :3 - Sharp Quills
]

# Sigil Descriptions
# Maps card id to a list of sigil names and description.
# With 0 being used to store how to play text.
sigil_descriptions = {
    0: [("1. Draw or pick a squirrel", "You start each turn by drawing a card or a squirrel."), 
        ("2. Place Cards", "Sacrifice creatures to pay their blood cost, then put new cards in open lanes."), 
        ("3. Attack", "Ring the bell. Cards strike opposing creatures or opponent directly if the lane is empty."), 
        ("4. Use sigils", "Cards with icons have special abilities - right click on cards for more information."), 
        ("5. Win", "Every direct hit tips the scale. Tip it all the way to the top to win.")],
    3: [("Fledgling","A CARD BEARING THIS SIGIL WILL GROW INTO A MORE POWERFUL FORM AFTER 1 TURN ON THE BOARD.")],
    5: [("Mighty Leap","A CARD BEARING THIS SIGIL WILL BLOCK AN OPPOSING CREATURE BEARING THE AIRBORNE SIGIL.")],
    8: [("Touch of Death","WHEN A CARD BEARING THIS SIGIL DAMAGES ANOTHER CREATURE, THAT CREATURE PERISHES.")],
    9: [("Sprinter","AT THE END OF THE OWNER'S TURN, A CARD BEARING THIS SIGIL WILL MOVE IN THE DIRECTION INSCRIBED IN THE SIGIL.")],
    10: [("Airborne","A CARD BEARING THIS SIGIL WILL STRIKE AN OPPONENT DIRECTLY, EVEN IF THERE IS A CREATURE OPPOSING IT."), 
         ("Waterborne","A CARD BEARING THIS SIGIL SUBMERGES ITSELF DURING THE OPPONENT'S TURN. WHILE SUBMERGED, OPPOSING CREATURES ATTACK ITS OWNER DIRECTLY.")],
    11: [("Bifurcated Strike","A CARD BEARING THIS SIGIL WILL STRIKE EACH OPPOSING SPACE TO THE LEFT AND RIGHT OF THE SPACE ACROSS FROM IT.")],
    12: [("Sharp Quills","ONCE A CARD BEARING THIS SIGIL IS STRUCK, THE STRIKER IS THEN DEALT A SINGLE DAMAGE POINT.")]
}

# Card Names Mapping
card_names = {
    1: "Squirrel",
    2: "Wolf",
    3: "Wolf Cub",
    4: "Stoat",
    5: "Bullfrog",
    6: "Geck",
    7: "Grizzly",
    8: "Adder",
    9: "Elk",
    10: "Kingfisher",
    11: "Mantis",
    12: "Porcupine"
}

# Lookup Tables for Blood Cost
# Each lookup table maps a 4 bit occupancy pattern to a list of tuples.
# Each Tuple in the list represents a valid sacrifice option
# Input: Occupancy Pattern
# Output: [(Board occupancy after sacrifice, Card placement location)]
lookup_table_0blood = {
    0b0000: [(0b0000,0),(0b0000,1),(0b0000,2),(0b0000,3)],
    0b0001: [(0b0001,1),(0b0001,2),(0b0001,3)],
    0b0010: [(0b0010,0),(0b0010,2),(0b0010,3)],
    0b0011: [(0b0011,2),(0b0011,3)],
    0b0100: [(0b0100,0),(0b0100,1),(0b0100,3)],
    0b0101: [(0b0101,1),(0b0101,3)],
    0b0110: [(0b0110,0),(0b0110,3)],
    0b0111: [(0b0111,3)],
    0b1000: [(0b1000,0),(0b1000,1),(0b1000,2)],
    0b1001: [(0b1001,1),(0b1001,2)],
    0b1010: [(0b1010,0),(0b1010,2)],
    0b1011: [(0b1011,2)],
    0b1100: [(0b1100,0),(0b1100,1)],
    0b1101: [(0b1101,1)],
    0b1110: [(0b1110,0)],
    0b1111: []}

lookup_table_1blood = {
    0b0001: [(0b0000,0),(0b0000,1),(0b0000,2),(0b0000,3)],
    0b0010: [(0b0000,0),(0b0000,1),(0b0000,2),(0b0000,3)],
    0b0011: [(0b0010,0),(0b0010,2),(0b0010,3),(0b0001,1),(0b0001,2),(0b0001,3)],
    0b0100: [(0b0000,0),(0b0000,1),(0b0000,2),(0b0000,3)],
    0b0101: [(0b0100,0),(0b0100,1),(0b0100,3),(0b0001,1),(0b0001,2),(0b0001,3)],
    0b0110: [(0b0100,0),(0b0100,1),(0b0100,3),(0b0010,0),(0b0010,2),(0b0010,3)],
    0b0111: [(0b0110,0),(0b0110,3),(0b0101,1),(0b0101,3),(0b0011,2),(0b0011,3)],
    0b1000: [(0b0000,0),(0b0000,1),(0b0000,2),(0b0000,3)],
    0b1001: [(0b1000,0),(0b1000,1),(0b1000,2),(0b0001,1),(0b0001,2),(0b0001,3)],
    0b1010: [(0b1000,0),(0b1000,1),(0b1000,2),(0b0010,0),(0b0010,2),(0b0010,3)],
    0b1011: [(0b1010,0),(0b1010,2),(0b1001,1),(0b1001,2),(0b0011,2),(0b0011,3)],
    0b1100: [(0b1000,0),(0b1000,1),(0b1000,2),(0b0100,0),(0b0100,1),(0b0100,3)],
    0b1101: [(0b1100,0),(0b1100,1),(0b1001,1),(0b1001,2),(0b0101,1),(0b0101,3)],
    0b1110: [(0b1100,0),(0b1100,1),(0b1010,0),(0b1010,2),(0b0110,0),(0b0110,3)],
    0b1111: [(0b1110,0),(0b1101,1),(0b1011,2),(0b0111,3)]}

lookup_table_2blood = {
    0b0011: [(0b0000,0),(0b0000,1),(0b0000,2),(0b0000,3)],
    0b0101: [(0b0000,0),(0b0000,1),(0b0000,2),(0b0000,3)],
    0b0110: [(0b0000,0),(0b0000,1),(0b0000,2),(0b0000,3)],
    0b0111: [(0b0100,0),(0b0100,1),(0b0100,3),(0b0010,0),(0b0010,2),(0b0010,3),(0b0001,1),(0b0001,2),(0b0001,3)],
    0b1001: [(0b0000,0),(0b0000,1),(0b0000,2),(0b0000,3)],
    0b1010: [(0b0000,0),(0b0000,1),(0b0000,2),(0b0000,3)],
    0b1011: [(0b1000,0),(0b1000,1),(0b1000,2),(0b0010,0),(0b0010,2),(0b0010,3),(0b0001,1),(0b0001,2),(0b0001,3)],
    0b1100: [(0b0000,0),(0b0000,1),(0b0000,2),(0b0000,3)],
    0b1101: [(0b1000,0),(0b1000,1),(0b1000,2),(0b0100,0),(0b0100,1),(0b0100,3),(0b0001,1),(0b0001,2),(0b0001,3)],
    0b1110: [(0b1000,0),(0b1000,1),(0b1000,2),(0b0100,0),(0b0100,1),(0b0100,3),(0b0010,0),(0b0010,2),(0b0010,3)],
    0b1111: [(0b1100,0),(0b1100,1),(0b1010,0),(0b1010,2),(0b0110,0),(0b0110,3),(0b1001,1),(0b1001,2),(0b0101,1),(0b0101,3),(0b0011,2),(0b0011,3)]}

lookup_table_3blood = {
    0b0111: [(0b0000,0),(0b0000,1),(0b0000,2),(0b0000,3)],
    0b1011: [(0b0000,0),(0b0000,1),(0b0000,2),(0b0000,3)],
    0b1101: [(0b0000,0),(0b0000,1),(0b0000,2),(0b0000,3)],
    0b1110: [(0b0000,0),(0b0000,1),(0b0000,2),(0b0000,3)],
    0b1111: [(0b1000,0),(0b1000,1),(0b1000,2),(0b0100,0),(0b0100,1),(0b0100,3),(0b0010,0),(0b0010,2),(0b0010,3),(0b0001,1),(0b0001,2),(0b0001,3)]}

lookup_table_4blood = {
    0b1111: [(0b0000,0),(0b0000,1),(0b0000,2),(0b0000,3)],}