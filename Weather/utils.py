import base64
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy
import matplotlib.ticker as mticker
import seaborn as sns
from io import BytesIO
from datetime import date, datetime
from sklearn.preprocessing import PolynomialFeatures
# for creating pipeline
from sklearn.pipeline import Pipeline

from sklearn import linear_model
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures


def get_image():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph


def get_simple_plot(graphType, graphTitle, **kwargs):
    plt.switch_backend('AGG')
    plt.figure(figsize=(10, 5))
    weather = kwargs.get('weather')
    data = kwargs.get('data')
    sns.set_style("whitegrid")

    if not weather:
        if graphType == "bar plot":
            title = graphTitle
            plt.title(title)
            g = sns.barplot(x='Compounds', y='Concentration', data=data)
            g.set_yscale("log")
        elif graphType == "line plot":
            title = graphTitle
            plt.title(title)
            g = sns.lineplot(x='Date', y='Concentration', hue='Compounds', data=data)
            g.set_yscale("log")
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
            plt.xticks(rotation=70)
        elif graphType == "count plot":
            title = graphTitle
            plt.title(title)
            sns.catplot(x='Compounds', y='Concentration', kind='swarm', data=data)
            plt.xticks(rotation=70)
        else:
            title = graphTitle
            plt.title(title)
            sns.regplot(x="Date", y="Concentration", data=data)
            plt.xticks(rotation=70)
    else:
        if graphType == "bar plot":
            title = graphTitle
            plt.title(title)
            sns.barplot(x='Components', y='Volume', data=data)
        elif graphType == "line plot":
            title = graphTitle
            plt.title(title)
            sns.lineplot(x='Date', y='Volume', hue='Components', data=data)
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
            plt.xticks(rotation=70)
        else:
            title = graphTitle
            plt.title(title)
            sns.catplot(x='Components', y='Volume', kind='swarm', data=data)
            plt.xticks(rotation=70)

    plt.tight_layout()
    plt.legend(loc='upper right')
    graph = get_image()
    return graph


def update_ticks(x, pos):
    if x == 0:
        return 'Mean'
    elif pos == 1:
        return 'pos is 6'
    else:
        return x


def get_regression_plot(graphTitle, **kwargs):
    plt.switch_backend('AGG')

    data = kwargs.get('data')
    sns.set_style("whitegrid")
    title = graphTitle

    x = data.Date.values.astype('float64')
    y = data.Concentration.values

    plt.figure(figsize=(12, 6))
    plt.scatter(x, y, s=15)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Concentration', fontsize=14)
    #plt.show()

    # Training Model
    lm = LinearRegression()
    lm.fit(x.reshape(-1, 1), y.reshape(-1, 1))

    y_pred = lm.predict(x.reshape(-1, 1))

    Input = [('polynomial', PolynomialFeatures(degree=2)), ('modal', LinearRegression())]
    pipe = Pipeline(Input)
    pipe.fit(x.reshape(-1, 1), y.reshape(-1, 1))
    poly_pred = pipe.predict(x.reshape(-1, 1))
    # sorting predicted values with respect to predictor
    sorted_zip = sorted(zip(x, poly_pred))
    x_poly, poly_pred = zip(*sorted_zip)
    # plotting predictions

    #fig, ax = plt.subplots()

    plt.figure(figsize=(12, 6))

    plt.scatter(x, y, s=10, label='Scatter')
    plt.plot(x, y_pred, color='r', label='Linear Regression')
    plt.plot(x_poly, poly_pred, color='g', label='Polynomial Regression')

    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Concentration', fontsize=14)
    plt.legend()
    plt.title(title)

    locs, labels = plt.xticks()

    newL = []
    #print(f'int lab: {int(labels[0])}')
    for label in locs:
        lab = datetime.fromtimestamp(int(label))
        d = lab.strftime("%d-%m-%Y")
        newL.append(d)

    plt.xticks(locs, newL, rotation=70)

    plt.tight_layout()
    plt.legend(loc='upper right')

    graph = get_image()
    return graph
