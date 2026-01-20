from flask import Flask, render_template, request, session, redirect, url_for
from professions import PROFESSIONS, EGE_MAP, CAREER_LADDERS
import random

app = Flask(__name__)
app.secret_key = "your-secret-key-change-in-production"

QUESTIONS = [
    {"text": "Представьте: перед вами незнакомая система. Что вы сделаете первым?",
     "answers": [
         ("Разберу, как устроены её компоненты и связи", "tech"),
         ("Выясню, кто в ней принимает решения и что их мотивирует", "social"),
         ("Зафиксирую ощущение от её внешнего вида и ритма", "creative"),
         ("Оценю, какие ресурсы она потребляет и что возвращает", "econ"),
         ("Определю, какие живые элементы в ней присутствуют", "bio"),
     ]},
    {"text": "Вам поручили описать один день через 20 лет. Что займёт большую часть описания?",
     "answers": [
         ("Алгоритмы и инструменты, которыми я управляю", "tech"),
         ("Люди, с кем я взаимодействую и что мы обсуждаем", "social"),
         ("Пространство, свет, формы и ощущения от них", "creative"),
         ("Показатели эффективности и баланс доходов/расходов", "econ"),
         ("Состояние организма и окружающей среды", "bio"),
     ]},
    {"text": "Какой тип аргументации для вас самый убедительный?",
     "answers": [
         ("Пример, воспроизводимый опытом и измерениями", "tech"),
         ("История, подтверждённая жизнью конкретных людей", "social"),
         ("Метафора, вызывающая эмоциональный отклик", "creative"),
         ("Расчёт, показывающий выгоду или риск", "econ"),
         ("Данные, полученные наблюдением и экспериментом", "bio"),
     ]},
    {"text": "Вы получаете неожиданный блок свободного времени. Что выберете?",
     "answers": [
         ("Разобрать и починить то, что давно не работает", "tech"),
         ("Устроить встречу с тем, с кем давно хотел поговорить", "social"),
         ("Попробовать новый способ запечатлеть образ", "creative"),
         ("Проанализировать свои траты за последний квартал", "econ"),
         ("Провести наблюдение за природным объектом", "bio"),
     ]},
    {"text": "Какой подход вы считаете наиболее надёжным для снижения неопределённости?",
     "answers": [
         ("Построение прототипа и итеративная проверка", "tech"),
         ("Обсуждение с заинтересованными сторонами", "social"),
         ("Создание образа, который объединяет разные точки зрения", "creative"),
         ("Оценка вероятностей и резервирование ресурсов", "econ"),
         ("Сбор первичных данных в полевых условиях", "bio"),
     ]},
    {"text": "Что для вас первично при оценке новой идеи?",
     "answers": [
         ("Возможность реализовать её существующими средствами", "tech"),
         ("Влияние на людей и их взаимоотношения", "social"),
         ("Целостность образа и внутренняя гармония", "creative"),
         ("Соотношение вложений и потенциального эффекта", "econ"),
         ("Совместимость с биологическими и экологическими ограничениями", "bio"),
     ]},
    {"text": "Какой критерий вы используете для окончательного выбора из нескольких равнозначных вариантов?",
     "answers": [
         ("Минимальная сложность и максимальная воспроизводимость", "tech"),
         ("Наибольшее понимание и принятие окружающими", "social"),
         ("Наиболее полное соответствие внутреннему ощущению правильности", "creative"),
         ("Наилучшее соотношение ресурсов и долгосрочной устойчивости", "econ"),
         ("Наименьший риск нарушения жизненных процессов", "bio"),
     ]},
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/test")
def start_test():
    session["answers"] = {}
    session["current_question"] = 1
    return redirect(url_for("show_question", q_num=1))

@app.route("/test/<int:q_num>", methods=["GET", "POST"])
def show_question(q_num):
    """Отображение одного вопроса"""
    if "answers" not in session:
        return redirect(url_for("start_test"))
    
    # Проверка номера вопроса
    if q_num < 1 or q_num > len(QUESTIONS):
        return redirect(url_for("start_test"))
    
    # Обработка ответа
    if request.method == "POST":
        answer = request.form.get("answer")
        if answer:
            session["answers"][str(q_num)] = answer
            session.modified = True
        
        # Переход к следующему вопросу или результату
        if q_num < len(QUESTIONS):
            return redirect(url_for("show_question", q_num=q_num+1))
        else:
            return redirect(url_for("calculate_result"))
    
    # Отображение вопроса
    question = QUESTIONS[q_num-1]
    saved_answer = session["answers"].get(str(q_num))
    
    return render_template("question.html",
                           q_num=q_num,
                           total=len(QUESTIONS),
                           question=question,
                           saved_answer=saved_answer)

@app.route("/calculate")
def calculate_result():

    if "answers" not in session:
        return redirect(url_for("start_test"))
    
    scores = {"tech": 0, "social": 0, "creative": 0, "econ": 0, "bio": 0}
    
    for q_num, answer in session["answers"].items():
        if answer in scores:
            scores[answer] += 1
    
    sorted_areas = sorted(scores.items(), key=lambda x: -x[1])
    top_candidates = [area for area, score in sorted_areas[:3]]
    top_area = random.choice(top_candidates)
    
    session["professions"] = PROFESSIONS.get(top_area, [])
    session["ege_subjects"] = EGE_MAP.get(top_area, [])
    
    return redirect(url_for("show_result"))

@app.route("/result")
def show_result():
    """Показ результатов"""
    professions = session.get("professions", [])
    ege_subjects = session.get("ege_subjects", [])
    
    if not professions:
        return redirect(url_for("start_test"))
    
    return render_template("result.html",
                           professions=professions,
                           ege_subjects=ege_subjects)

@app.route("/career/<prof_name>")
def career(prof_name):
    ladder = CAREER_LADDERS.get(prof_name, [])
    return render_template("career.html", prof_name=prof_name, ladder=ladder)

if __name__ == "__main__":
    app.run(debug=True)