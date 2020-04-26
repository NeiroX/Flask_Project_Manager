from PIL import Image
import numpy
import matplotlib.pyplot as plt
import datetime
import io
import base64


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
    fig = plt.figure()
    plot = fig.add_subplot(111)
    x = list(map(lambda date: date.strftime('%d.%m.%Y'), dates))
    y = avg_likes
    plot.plot(x, y)
    plot.set_ylabel('Average like')
    plot.set_xlabel('Day')
    plot.set_title('Project statistics')
    plot.legend()
    fig.canvas.draw()
    return convert_pillow_to_base64(fig)


plot_avg_likes([1, 2, 3],
               [datetime.datetime(2020, 3, 1), datetime.datetime(2020, 3, 20), datetime.datetime(2020, 4, 3)])
