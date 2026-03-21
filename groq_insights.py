"""
groq_insights.py
NutriLens - Free AI nutrition insights using Groq
"""

from groq import Groq
from datetime import datetime
import os

# ======================
# SETUP GROQ
# ======================

client = Groq(api_key="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")


# ======================
# INSTANT MEAL INSIGHTS
# ======================

def get_meal_insights(food_name, portion_grams, calories,
                      protein, carbs, fat, meal_type="meal"):

    prompt = f"""
You are a friendly Indian nutrition expert.

Food: {food_name}
Portion: {portion_grams}g
Meal Type: {meal_type}
Calories: {calories} kcal
Protein: {protein}g
Carbs: {carbs}g
Fat: {fat}g

Give a short insight:
1. Is this healthy?
2. One nutritional highlight
3. One quick improvement tip

Keep under 50 words.
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an Indian nutritionist."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Meal logged successfully! (Error: {e})"


# ======================
# WEEKLY SUMMARY
# ======================

def generate_weekly_summary(meals_data, user_goals=None):

    total_days = 7

    total_calories = sum(m['calories'] for m in meals_data)
    total_protein = sum(m['protein'] for m in meals_data)
    total_carbs = sum(m['carbs'] for m in meals_data)
    total_fat = sum(m['fat'] for m in meals_data)

    avg_cal = total_calories / total_days
    avg_pro = total_protein / total_days
    avg_carb = total_carbs / total_days
    avg_fat = total_fat / total_days

    food_counts = {}

    for meal in meals_data:
        food = meal['food_name']
        food_counts[food] = food_counts.get(food, 0) + 1

    top_foods = sorted(food_counts.items(),
                       key=lambda x: x[1],
                       reverse=True)[:5]

    top_foods_str = ", ".join([f"{f} ({c}x)" for f, c in top_foods])

    goals_context = ""

    if user_goals:
        goals_context = f"""
User Goals:
Calories: {user_goals.get('daily_calories',2000)}
Protein: {user_goals.get('daily_protein',80)}
Carbs: {user_goals.get('daily_carbs',250)}
Fat: {user_goals.get('daily_fat',65)}
"""

    prompt = f"""
Analyze this weekly eating data.

Daily averages:
Calories: {avg_cal:.0f}
Protein: {avg_pro:.0f}g
Carbs: {avg_carb:.0f}g
Fat: {avg_fat:.0f}g

Most eaten foods: {top_foods_str}
Total meals logged: {len(meals_data)}

{goals_context}

Provide:

WEEKLY SUMMARY
2-3 sentences

HIGHLIGHTS
- point
- point

AREAS TO WATCH
- concern
- concern

THIS WEEK'S GOALS
1. tip
2. tip
3. tip

KEEP IT UP
Short motivation
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert Indian nutritionist."},
                {"role": "user", "content": prompt}
            ]
        )

        return {
            "full_report": response.choices[0].message.content.strip(),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

    except Exception as e:

        return {
            "full_report": f"Weekly summary unavailable. Error: {e}",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }


# ======================
# TEST
# ======================

if __name__ == "__main__":

    print("Testing Groq AI Integration\n")

    print("TEST 1: Meal Insight")
    print("=" * 40)

    insight = get_meal_insights(
        food_name="Chicken Biryani",
        portion_grams=280,
        calories=364,
        protein=14.5,
        carbs=66.6,
        fat=7.0,
        meal_type="lunch"
    )

    print(insight)

    print("\nTEST 2: Weekly Summary")
    print("=" * 40)

    sample_meals = [
        {'food_name': 'Biryani', 'calories': 450, 'protein': 15, 'carbs': 70, 'fat': 12},
        {'food_name': 'Dosa', 'calories': 200, 'protein': 5, 'carbs': 35, 'fat': 3},
        {'food_name': 'Dal Rice', 'calories': 350, 'protein': 12, 'carbs': 60, 'fat': 5},
        {'food_name': 'Paneer Tikka', 'calories': 300, 'protein': 18, 'carbs': 8, 'fat': 22},
        {'food_name': 'Idli', 'calories': 150, 'protein': 4, 'carbs': 28, 'fat': 1},
    ] * 3

    summary = generate_weekly_summary(sample_meals)

    print(summary["full_report"])
    print("\nGenerated at:", summary["generated_at"])