from PIL import Image
import numpy
import matplotlib.pyplot as plt
import matplotlib
import datetime
import io
import base64
import db_session
from models import likes_in_day_table

matplotlib.use('TkAgg')


def get_dates(pr_id):
    '''Получить все даты из таблицы likes_in_day_table'''
    sesion = db_session.create_session()
    dates = [date[0] for date in sesion.query(likes_in_day_table.c.date).filter(
        likes_in_day_table.c.project_id == pr_id)]
    return set(dates)


def get_project_likes(pr_id):
    '''Получить все оценки из таблицы likes_in_day_table'''
    sesion = db_session.create_session()
    likes_db = sesion.query(likes_in_day_table).filter(likes_in_day_table.c.project_id == pr_id)
    ans = []
    for likes_ses in likes_db:
        ans.append({'rates_5': likes_ses[1],
                    'rates_4': likes_ses[2],
                    'rates_3': likes_ses[3],
                    'rates_2': likes_ses[4],
                    'rates_1': likes_ses[5],
                    'avg_rate': likes_ses[6]})
    return ans


def convert_pillow_to_base64(figure):
    '''Преобразование matplotlib фигуры в Pillow Image,
     сохранение ее в формате png и перевод с байтов в base_64(для html)'''
    w, h = figure.canvas.get_width_height()
    numpy_img_arr = numpy.frombuffer(figure.canvas.tostring_rgb(), dtype=numpy.uint8).reshape(h, w,
                                                                                              3)
    img = Image.fromarray(numpy_img_arr)
    output = io.BytesIO()
    img.save(output, format='PNG')
    output.seek(0, 0)
    img_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
    return img_base64


def plot_avg_likes(pr_id):
    '''Нарисовать график средних значений в какой-то период
        dates: Период(datetime)
        avg_likes: Лайки за этот период
    '''
    dates = get_dates(pr_id)
    avg_likes = [likes['avg_rate'] for likes in get_project_likes(pr_id)]
    fig = plt.figure()
    plot = fig.add_subplot(111)
    print('plot avg l')
    x = list(map(lambda date: date.strftime('%d.%m.%Y'), dates))
    y = avg_likes
    print(x, y)
    plot.plot(x, y)
    plot.set_ylabel('Average like')
    plot.set_xlabel('Day')
    plot.set_title('Average likes per day')
    fig.canvas.draw()
    return convert_pillow_to_base64(fig)


def plot_date_likes(pr_id):
    '''Нарисовать график всех значений в какой-то промежуток времени
        dates: Период(datetime)
        dic: Словарь оценок
    '''
    dates = get_dates(pr_id)
    dic = {'rates_5': [], 'rates_4': [], 'rates_3': [], 'rates_2': [], 'rates_1': []}
    for lik in get_project_likes(pr_id):
        for key in lik.keys():
            if key != 'avg_rate':
                dic[key].append(lik[key])
    fig = plt.figure()
    plot = fig.add_subplot(111)
    x = list(map(lambda date: date.strftime('%d.%m.%Y'), dates))
    for key in dic:
        y = dic[key]
        plot.plot(x, y, label=key)
    plot.set_title('Likes per day')
    plot.set_xlabel('Day')
    plot.set_ylabel('Like')
    plot.legend(loc='best')
    fig.canvas.draw()
    return convert_pillow_to_base64(fig)


def plot_day_likes(pr_id):
    '''Нарисовать график оценок в конкретный день'''
    ans = []
    dics = get_project_likes(pr_id)
    for i, date in enumerate(get_dates(pr_id)):
        fig = plt.figure()
        bad_dic = dics[i]
        dic = {1: bad_dic['rates_1'], 2: bad_dic['rates_2'], 3: bad_dic['rates_3'],
               4: bad_dic['rates_4'],
               5: bad_dic['rates_5']}
        colors = {1: 'red', 2: 'coral', 3: 'gold', 4: 'yellowgreen', 5: 'darkgreen'}
        plot = fig.add_subplot(111)
        names, values = zip(*dic.items())
        y_pos = numpy.arange(1, len(names) + 1)
        plot.bar(y_pos, values, color=[colors[key] for key in dic])
        plot.set_xticks(y_pos, names)
        plot.set_title(f'Likes on {date.strftime("%d.%m.%Y")}')
        fig.canvas.draw()
        ans.append([convert_pillow_to_base64(fig), date.strftime("%d.%m.%Y")])
    return ans
