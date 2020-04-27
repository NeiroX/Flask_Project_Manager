from PIL import Image
import numpy
import matplotlib.pyplot as plt
import datetime
import io
import base64
import db_session
from models import likes_in_day_table


def get_dates():
    sesion = db_session.create_session()
    dates = [date for date in sesion.query(likes_in_day_table.c.date).all()]
    return dates


def convert_pillow_to_base64(figure):
    w, h = figure.canvas.get_width_height()
    numpy_img_arr = numpy.frombuffer(figure.canvas.tostring_rgb(), dtype=numpy.uint8).reshape(h, w, 3)
    img = Image.fromarray(numpy_img_arr)
    output = io.BytesIO()
    img.save(output, format='PNG')
    output.seek(0, 0)
    img_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
    return img_base64


def plot_avg_likes(avg_likes, dates):
    da = get_dates()
    print('dates', da)
    fig = plt.figure()
    plot = fig.add_subplot(111)
    x = list(map(lambda date: date.strftime('%d.%m.%Y'), dates))
    y = avg_likes
    plot.plot(x, y)
    plot.set_ylabel('Average like')
    plot.set_xlabel('Day')
    plot.set_title('Average likes per day')
    fig.canvas.draw()
    return convert_pillow_to_base64(fig)


def plot_date_likes(dates, dic):
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


def plot_day_likes(date, dic):
    fig = plt.figure()
    colors = {1: 'red', 2: 'coral', 3: 'gold', 4: 'yellowgreen', 5: 'darkgreen'}
    plot = fig.add_subplot(111)
    names, values = zip(*dic.items())
    y_pos = numpy.arange(len(names))
    plot.bar(y_pos, values, color=[colors[key] for key in dic])
    plot.set_xticks(y_pos, names)
    plot.set_title(f'Likes on {date.strftime("%d.%m.%Y")}')
    fig.canvas.draw()
    return convert_pillow_to_base64(fig)


plot_date_likes([datetime.datetime(2020, 3, 1),
                 datetime.datetime(2020, 3, 20),
                 datetime.datetime(2020, 4, 6)],
                {1: [1, 2, 3], 2: [2, 4, 3], 3: [5, 2, 1], 4: [2, 5, 7], 5: [3, 4, 2]})
