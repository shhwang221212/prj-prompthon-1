def get_color_by_cong(cong_level):
    if cong_level == "여유":
        return "lightblue"
    elif cong_level == "보통":
        return "purple"
    elif cong_level == "약간 붐빔":
        return "pink"
    else:
        return "red"


def get_cong_small_image(cong_level):
    if cong_level == "여유":
        return "https://github.com/shhwang221212/prj-prompthon-1/assets/126046181/7e820597-e61e-4b60-84ef-aa85dac50a1a"
    elif cong_level == "보통":
        return "https://github.com/shhwang221212/prj-prompthon-1/assets/126046181/39dc033b-dffa-45a6-b1d6-a2b82a249733"
    elif cong_level == "약간 붐빔":
        return "https://github.com/shhwang221212/prj-prompthon-1/assets/126046181/afb15bf1-7672-4697-90fa-954e5de99046"
    else:
        return "https://github.com/shhwang221212/prj-prompthon-1/assets/126046181/ea835854-1d32-4cfb-9745-ed4ae4db695d"

def get_cong_image(cong_level):
    if cong_level == "여유":
        return "https://github.com/shhwang221212/prj-prompthon-1/assets/126046181/3354ea99-46f6-41b4-8d85-9a4c17b00c89"
    elif cong_level == "보통":
        return "https://github.com/shhwang221212/prj-prompthon-1/assets/126046181/c7eef008-0c24-4321-af4a-c8959afd0ea8"
    elif cong_level == "약간 붐빔":
        return "https://github.com/shhwang221212/prj-prompthon-1/assets/126046181/8f5fdf80-3078-4269-9cd9-b11c7341aa98"
    else:
        return "https://github.com/shhwang221212/prj-prompthon-1/assets/126046181/78200a42-9d8a-45e0-827a-690913773d8d"

def get_dummy_search_value():
    return [
    {"time" : "2024-03-18", "value" : 12500},
    {"time" : "2024-03-19", "value" : 11000},
    {"time" : "2024-03-20", "value" : 13000},
    {"time" : "2024-03-21", "value" : 10500},
    {"time" : "2024-03-22", "value" : 12000},
    {"time" : "2024-03-23", "value" : 14000},
    {"time" : "2024-03-24", "value" : 11500},
    {"time" : "2024-03-25", "value" : 12500},
    {"time" : "2024-03-26", "value" : 11000},
    {"time" : "2024-03-27", "value" : 13000},
    {"time" : "2024-03-28", "value" : 10500},
    {"time" : "2024-03-29", "value" : 12000},
    {"time" : "2024-03-30", "value" : 14000},
    {"time" : "2024-03-31", "value" : 11500},
    {"time" : "2024-04-01", "value" : 12500},
    {"time" : "2024-04-02", "value" : 11000},
    {"time" : "2024-04-03", "value" : 13000},
    {"time" : "2024-04-04", "value" : 10500},
    {"time" : "2024-04-05", "value" : 12000},
    {"time" : "2024-04-06", "value" : 14000},
    {"time" : "2024-04-07", "value" : 11500},
    {"time" : "2024-04-08", "value" : 12500},
    {"time" : "2024-04-09", "value" : 11000},
    {"time" : "2024-04-10", "value" : 13000},
    {"time" : "2024-04-11", "value" : 10500},
    {"time" : "2024-04-12", "value" : 12000},
    {"time" : "2024-04-13", "value" : 14000},
    {"time" : "2024-04-14", "value" : 11500},
    {"time" : "2024-04-15", "value" : 12500},
    {"time" : "2024-04-16", "value" : 11000},
    {"time" : "2024-04-17", "value" : 13000}
]
