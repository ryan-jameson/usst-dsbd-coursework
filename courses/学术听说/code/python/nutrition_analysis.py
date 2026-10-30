import math

def calculate_bmi(weight, height):
    """计算BMI（身体质量指数）"""
    return weight / (height / 100) ** 2

def assess_nutritional_status(bmi, age):
    """根据BMI和年龄评估营养状况"""
    if age < 18:
        # 使用儿童BMI百分位数来评估
        if bmi < 15:
            return 'Underweight'
        elif 15 <= bmi <= 85:
            return 'Healthy weight'
        else:
            return 'Overweight'
    else:
        # 使用成人BMI分类来评估
        if bmi < 18.5:
            return 'Underweight'
        elif 18.5 <= bmi <= 24.9:
            return 'Healthy weight'
        else:
            return 'Overweight'

def generate_nutrition_plan(age, weight, height):
    """根据儿童的年龄、体重和身高生成营养食谱"""
    bmi = calculate_bmi(weight, height)
    status = assess_nutritional_status(bmi, age)
    
    # 根据营养状况调整食谱
    if status == 'Underweight':
        meal_plan = {
            'breakfast': 'High-protein cereal with milk and a banana',
            'lunch': 'Chicken sandwich with avocado and a side of sweet potato fries',
            'dinner': 'Beef steak with a baked potato and vegetables',
            'snack': 'Greek yogurt with honey and almonds'
        }
    elif status == 'Healthy weight':
        meal_plan = {
            'breakfast': 'Whole grain cereal with milk and fresh berries',
            'lunch': 'Turkey wrap with mixed greens and a side of carrot sticks',
            'dinner': 'Grilled salmon with quinoa and steamed vegetables',
            'snack': 'Apple with a tablespoon of peanut butter'
        }
    else:  # Overweight
        meal_plan = {
            'breakfast': 'High-fiber cereal with skim milk and a piece of fruit',
            'lunch': 'Veggie whole wheat pasta with tomato sauce',
            'dinner': 'Baked chicken with brown rice and a side salad',
            'snack': 'Vegetable sticks with hummus'
        }
    
    return meal_plan, bmi, status

# Example usage:
# meal_plan, bmi, status = generate_nutrition_plan(10, 40, 150)
# print("BMI:", bmi)
# print("Nutritional Status:", status)
# print("Meal Plan:", meal_plan)