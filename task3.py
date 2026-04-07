import graphviz
import matplotlib.pyplot as plt

# =========================
# 3.1. Реализовать функцию draw(vertices, edges)
# =========================

'''
Идея решения

Нужно написать функцию draw(vertices, edges), которая:
1 принимает список вершин и список рёбер;
2 переводит их в текст на языке DOT;
3 создаёт ориентированный граф digraph;
4 добавляет вершины с подписями;
5 добавляет дуги;
6 передаёт готовую строку в graphviz для визуализации.

Если вершина встречается в рёбрах, но не была явно передана в vertices, она создаётся автоматически с подписью из своего номера.
'''
def draw(vertices, edges):
    lines = ['digraph {']

    vertex_ids = set()

    for vertex_id, label in vertices:
        vertex_ids.add(vertex_id)
        lines.append(f'    {vertex_id} [label="{label}"]')

    for start, end in edges:
        if start not in vertex_ids:
            vertex_ids.add(start)
            lines.append(f'    {start} [label="{start}"]')
        if end not in vertex_ids:
            vertex_ids.add(end)
            lines.append(f'    {end} [label="{end}"]')

        lines.append(f'    {start} -> {end}')

    lines.append('}')

    dot_text = '\n'.join(lines)
    graph = graphviz.Source(dot_text)

    return graph


graph = draw([(1, 'v1'), (2, 'v2')], [(1, 2), (2, 3), (2, 2)])
graph.render('task3_graph', format='png', view=True, cleanup=True)

# =========================
# 3.2 Логистическое отображение LogisticMap
# =========================


class Chaos:
    def __init__(self, mu, state):
        self.mu = mu
        self.state = state
        self.stabilize()

    def stabilize(self):
        for _ in range(1000):
            self.next()

    def next(self):
        return self.state


class LogisticMap(Chaos):
    def next(self):
        self.state = self.mu * self.state * (1 - self.state)
        return self.state


values_mu = [2, 3.2, 3.5, 3.55]

for mu in values_mu:
    obj = LogisticMap(mu, 0.1)
    result_1 = obj.next()
    result_2 = obj.next()
    result_3 = obj.next()

    print(f'mu = {mu}: ({result_1}, {result_2}, {result_3})')

# =========================
# 3.3 Создать функцию visualize для визуализации графа изменений состояния класса LogisticMap
# =========================

'''
Нужно сделать функцию visualize(obj), которая:
1 принимает объект LogisticMap;
2 несколько раз вызывает у него next();
3 сохраняет получающиеся состояния как вершины графа;
4 соединяет их рёбрами по порядку перехода состояний;
5 передаёт всё в уже готовую функцию draw(vertices, edges).

То есть мы строим граф переходов состояния системы:
- текущее состояние
- следующее состояние
- следующее после него
- и так далее    
'''

def draw(vertices, edges):
    lines = ['digraph {']

    for vertex_id, label in vertices:
        lines.append(f'    {vertex_id} [label="{label}"]')

    for start, end in edges:
        lines.append(f'    {start} -> {end}')

    lines.append('}')

    dot_text = '\n'.join(lines)
    graph = graphviz.Source(dot_text)
    return graph


class Chaos:
    def __init__(self, mu, state):
        self.mu = mu
        self.state = state
        self.stabilize()

    def stabilize(self):
        for _ in range(1000):
            self.next()

    def next(self):
        return self.state


class LogisticMap(Chaos):
    def next(self):
        self.state = self.mu * self.state * (1 - self.state)
        return self.state


def visualize(obj):
    vertices = []
    edges = []
    state_to_id = {}

    current_state = obj.next()
    state_to_id[current_state] = 1
    vertices.append((1, str(current_state)))

    current_id = 1
    next_id = 2

    while True:
        next_state = obj.next()

        if next_state in state_to_id:
            edges.append((current_id, state_to_id[next_state]))
            break

        state_to_id[next_state] = next_id
        vertices.append((next_id, str(next_state)))
        edges.append((current_id, next_id))

        current_id = next_id
        next_id += 1

    return draw(vertices, edges)


graph = visualize(LogisticMap(3.5, 0.1))
graph.render('task3_3_graph', format='png', view=True, cleanup=True)

# =========================
# 3.4 Построить диаграмму бифуркаций для логистического отображения
# =========================

'''
Нужно построить диаграмму бифуркаций для логистического отображения при μ ∈ [1, 4].

Что это значит:
1 берём много значений μ на отрезке от 1 до 4;
2 для каждого μ создаём объект LogisticMap;
3 даём системе “успокоиться” на первых итерациях, чтобы переходный процесс ушёл;
4 потом сохраняем несколько следующих состояний;
5 каждое такое состояние отображаем точкой:
	- по оси x стоит μ
	- по оси y стоит состояние системы

Если при каком-то μ система приходит к одному устойчивому значению, увидим одну ветвь.
Если начинает чередоваться между двумя, четырьмя, многими значениями, появятся расщепления.
'''

def bifurcation_diagram():
    mu_values = []
    state_values = []

    mu = 1.0
    step = 0.01

    while mu <= 4.0:
        obj = LogisticMap(mu, 0.1)

        for _ in range(200):
            obj.next()

        for _ in range(20):
            state = obj.next()
            mu_values.append(mu)
            state_values.append(state)

        mu += step

    plt.figure(figsize=(10, 8))
    plt.scatter(mu_values, state_values, s=8)
    plt.title('Диаграмма бифуркаций логистического отображения')
    plt.xlabel('mu')
    plt.ylabel('state')
    plt.grid(True)
    plt.show()


bifurcation_diagram()

# =========================
# 3.5. Полученную динамическую систему можно использовать в качестве генераторов псевдослучайных чисел.
# =========================

'''
Нужно показать, какое распределение имеют значения, которые порождает LogisticMap при mu = 4.0.

Что делаем:
1 создаём объект LogisticMap(4.0, 0.1);
2 после стабилизации много раз вызываем next();
3 собираем значения состояний в список;
4 строим гистограмму этих значений;
5 по виду гистограммы делаем вывод о распределении.

Для mu = 4.0 значения не распределены равномерно.
Они чаще появляются около 0 и около 1, а в середине реже.
То есть распределение получается U-образным.
'''

def distribution_logistic_map():
    obj = LogisticMap(4.0, 0.1)
    values = []

    for _ in range(100000):
        values.append(obj.next())

    plt.figure(figsize=(10, 8))
    plt.hist(values, bins=30, density=True, edgecolor='white')
    plt.title('Распределение значений LogisticMap при mu = 4.0')
    plt.xlabel('state')
    plt.ylabel('density')
    plt.grid(True)
    plt.show()


distribution_logistic_map()