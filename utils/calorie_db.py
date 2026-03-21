# calorie_db.py
# NutriLens - Nutrition Database
# Exactly 22 classes matching trained model
# All values PER 100 GRAMS

FOOD_DATABASE = {

    # ---------- MAIN COURSE ----------
    "biryani": {
        "calories": 150,
        "protein": 7,
        "carbs": 20,
        "fat": 5,
        "serving_size": 300,
        "category": "Main Course"
    },
    "chole_bhature": {
        "calories": 200,
        "protein": 7,
        "carbs": 28,
        "fat": 8,
        "serving_size": 250,
        "category": "Main Course"
    },
    "pav_bhaji": {
        "calories": 175,
        "protein": 5,
        "carbs": 28,
        "fat": 6,
        "serving_size": 250,
        "category": "Main Course"
    },
    "paneer": {
        "calories": 265,
        "protein": 18,
        "carbs": 3,
        "fat": 20,
        "serving_size": 100,
        "category": "Main Course"
    },
    "rajma_chawal": {
        "calories": 140,
        "protein": 7,
        "carbs": 24,
        "fat": 2,
        "serving_size": 250,
        "category": "Main Course"
    },

    # ---------- BREADS ----------
    "roti": {
        "calories": 297,
        "protein": 9,
        "carbs": 57,
        "fat": 4,
        "serving_size": 40,
        "category": "Bread"
    },
    "naan": {
        "calories": 310,
        "protein": 9,
        "carbs": 55,
        "fat": 7,
        "serving_size": 90,
        "category": "Bread"
    },

    # ---------- SOUTH INDIAN ----------
    "dosa": {
        "calories": 168,
        "protein": 4,
        "carbs": 30,
        "fat": 4,
        "serving_size": 100,
        "category": "South Indian"
    },
    "idli": {
        "calories": 58,
        "protein": 2,
        "carbs": 11,
        "fat": 0.4,
        "serving_size": 120,
        "category": "South Indian"
    },
    "medu_wada": {
        "calories": 260,
        "protein": 7,
        "carbs": 30,
        "fat": 13,
        "serving_size": 100,
        "category": "South Indian"
    },

    # ---------- STREET FOOD ----------
    "samosa": {
        "calories": 262,
        "protein": 5,
        "carbs": 30,
        "fat": 14,
        "serving_size": 100,
        "category": "Street Food"
    },
    "pani_puri": {
        "calories": 180,
        "protein": 3,
        "carbs": 28,
        "fat": 6,
        "serving_size": 100,
        "category": "Street Food"
    },
    "vada_pav": {
        "calories": 290,
        "protein": 7,
        "carbs": 40,
        "fat": 12,
        "serving_size": 150,
        "category": "Street Food"
    },
    "pakode": {
        "calories": 310,
        "protein": 6,
        "carbs": 28,
        "fat": 20,
        "serving_size": 100,
        "category": "Street Food"
    },
    "momos": {
        "calories": 150,
        "protein": 8,
        "carbs": 20,
        "fat": 4,
        "serving_size": 150,
        "category": "Street Food"
    },
    "roll": {
        "calories": 220,
        "protein": 8,
        "carbs": 32,
        "fat": 7,
        "serving_size": 180,
        "category": "Street Food"
    },

    # ---------- BREAKFAST ----------
    "poha": {
        "calories": 130,
        "protein": 3,
        "carbs": 26,
        "fat": 2,
        "serving_size": 200,
        "category": "Breakfast"
    },
    "dhokla": {
        "calories": 160,
        "protein": 5,
        "carbs": 25,
        "fat": 5,
        "serving_size": 150,
        "category": "Breakfast"
    },

    # ---------- DESSERTS ----------
    "gulab_jamun": {
        "calories": 380,
        "protein": 5,
        "carbs": 60,
        "fat": 13,
        "serving_size": 100,
        "category": "Dessert"
    },
    "jalebi": {
        "calories": 360,
        "protein": 2,
        "carbs": 65,
        "fat": 10,
        "serving_size": 100,
        "category": "Dessert"
    },
    "kulfi": {
        "calories": 225,
        "protein": 5,
        "carbs": 28,
        "fat": 11,
        "serving_size": 80,
        "category": "Dessert"
    },

    # ---------- BEVERAGES ----------
    "chai": {
        "calories": 45,
        "protein": 2,
        "carbs": 6,
        "fat": 2,
        "serving_size": 150,
        "category": "Beverage"
    },
}


# -------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------

def get_nutrition(food_name):
    food_name = food_name.lower().strip().replace(" ", "_")
    if food_name not in FOOD_DATABASE:
        return None
    info       = FOOD_DATABASE[food_name]
    serving    = info["serving_size"]
    multiplier = serving / 100
    return {
        "food"                : food_name,
        "category"            : info["category"],
        "serving_size_g"      : serving,
        "calories_per_100g"   : info["calories"],
        "protein_per_100g"    : info["protein"],
        "carbs_per_100g"      : info["carbs"],
        "fat_per_100g"        : info["fat"],
        "calories_per_serving": round(info["calories"] * multiplier),
        "protein_per_serving" : round(info["protein"]  * multiplier, 1),
        "carbs_per_serving"   : round(info["carbs"]    * multiplier, 1),
        "fat_per_serving"     : round(info["fat"]      * multiplier, 1),
    }


def get_calories_for_weight(food_name, weight_in_grams):
    food_name = food_name.lower().strip().replace(" ", "_")
    if food_name not in FOOD_DATABASE:
        return None
    return round((FOOD_DATABASE[food_name]["calories"] / 100) * weight_in_grams)


def print_nutrition_card(food_name):
    info = get_nutrition(food_name)
    if info is None:
        print(f"'{food_name}' not found. Available: {list(FOOD_DATABASE.keys())}")
        return
    print("=" * 45)
    print(f"  {info['food'].upper().replace('_', ' ')}")
    print(f"  Category     : {info['category']}")
    print(f"  Serving size : {info['serving_size_g']}g")
    print("=" * 45)
    print(f"  Calories : {info['calories_per_serving']} kcal")
    print(f"  Protein  : {info['protein_per_serving']} g")
    print(f"  Carbs    : {info['carbs_per_serving']} g")
    print(f"  Fat      : {info['fat_per_serving']} g")
    print("=" * 45)
    print(f"  (Per 100g: {info['calories_per_100g']} kcal)")


def get_all_foods():
    return list(FOOD_DATABASE.keys())