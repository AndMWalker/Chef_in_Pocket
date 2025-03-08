# app.py

from flask import Flask, request, jsonify, render_template
import os
import openai
from dotenv import load_dotenv
from openai import OpenAI

# Load variables from .env into the environment
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
app = Flask(__name__)

client = OpenAI(api_key=openai.api_key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_recipes', methods=['POST'])
def generate_recipes():
    data = request.json
    ingredients = data.get('ingredients', '')
    dietary_preferences = data.get('dietary_preferences', '') 
    caloric_target = data.get('caloric_target', '')
    health_conditions = data.get('health_conditions', '')
    meal_time = data.get('meal_time', 'No preference')
    cooking_experience = data.get('cooking_experience', 'No preference')
    quick_meals = data.get('quick_meals', False)

    prompt = (
        "You are an AI recipe generator. Generate 3 distinct, detailed recipes based on these inputs: "
        f"Ingredients: {ingredients}; Dietary or Cuisine Preferences: {dietary_preferences}; Caloric Target: {caloric_target}; "
        f"Health Conditions: {health_conditions}; Meal Time Preference: {meal_time}; Cooking Experience: {cooking_experience}; "
        f"Quick Meals Only: {quick_meals}.\n\n"
        "For each recipe, follow this exact format using valid markdown:\n\n"
        "1. **Recipe Name:** Output the dish name as an HTML h1 header with center alignment. For example:\n"
        "<h1 style='text-align:center;'><strong>Dish Name</strong></h1>\n\n"
        "2. **Information Section:** Immediately below the dish name, output a markdown table with two columns titled **Ingredients** and **Equipment**. Use valid markdown table syntax. For example:\n\n"
        "| Ingredients               | Equipment              |\n"
        "| ------------------------- | :--------------------: |\n"
        "| ingredient list here      | equipment list here    |\n\n"
        "3. Directly below the table, output on separate lines:\n\n"
        "Approximate Time Required: [time]\n\n"
        "Calories: [calories]\n\n"
        "Recommended Cooking Experience: [experience]\n\n"
        "4. Insert a horizontal rule (using three hyphens on a new line) to separate the information section from the recipe instructions.\n\n"
        "5. **Recipe Instructions:** Finally, provide clear, detailed, step-by-step cooking instructions for the dish.\n\n"
        "6. Insert a horizontal rule (using three hyphens on a new line) to separate the recipe instructions from the information section of the following dish, this is not required if there is no following dish.\n\n"
        "Do not include any introductory text. Ensure that the markdown is valid and renders correctly."
    )

    try:
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful AI recipe generator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=5000,
            temperature=0.7,
            stream=True
        )
        gpt_answer = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end="")
                gpt_answer += content
        
        return jsonify({"recipes": gpt_answer}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
