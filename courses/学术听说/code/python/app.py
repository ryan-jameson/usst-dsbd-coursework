from flask import Flask, request, render_template
import nutrition_analysis

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def meal_planner():
    if request.method == 'POST':
        age = int(request.form.get('age'))
        weight = float(request.form.get('weight'))
        height = float(request.form.get('height'))

        # 生成食谱，并接收额外的数据
        meal_plan, bmi, status = nutrition_analysis.generate_nutrition_plan(age, weight, height)
        
        # 将数据传递给模板
        return render_template('result.html', meal_plan=meal_plan, bmi=bmi, status=status)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)