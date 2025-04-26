import copy
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

class Relationships:
    def __init__(self):
        self.file_path = ""
        self.variables_config = []
        self.variables_list = []
        self.matrix_config = []
        self.relation_matrix = []
        self.variables_paths = {}

    def init_variables_config(self):
        self.file_path = input("Введите путь к файлу: ")
        variables_input_data = input("Введите строку с именами узлов в формате A:Z_1:9: ")
        self.variables_config.append(variables_input_data.split("_")[0])
        self.variables_config.append(int(variables_input_data.split("_")[1].split(":")[0]))
        self.variables_config.append(int(variables_input_data.split("_")[1].split(":")[1]))
        self.variables_config.append(self.variables_config[2] - self.variables_config[1] + 1)

    def init_variables_list(self):
        data = pd.read_excel(self.file_path, usecols=self.variables_config[0],
               skiprows=self.variables_config[1] - 2, nrows=self.variables_config[3])
        self.variables_list = data.values[0]

    def print_variables_list(self):
        print(self.variables_list)

    def init_matrix_config(self):
        matrix_input_data = input("Введите конфигурацию матрицы в формате A:Z_1:9: ")
        self.matrix_config.append(matrix_input_data.split("_")[0])
        self.matrix_config.append(int(matrix_input_data.split("_")[1].split(":")[0]))
        self.matrix_config.append(int(matrix_input_data.split("_")[1].split(":")[1]))
        self.matrix_config.append(self.matrix_config[2] - self.matrix_config[1] + 1)

    def init_relation_matrix(self):
        data = pd.read_excel(self.file_path, usecols=self.matrix_config[0],
                skiprows=self.matrix_config[1] - 2, nrows=self.matrix_config[3])
        self.relation_matrix = data.values

    def print_relation_matrix(self):
        print(self.relation_matrix)

    def init_variables_paths(self):
        for variable in self.variables_list:
            self.variables_paths[variable] = []

        for x in range(len(self.variables_list)):
            for y in range(len(self.variables_list)):
                if self.relation_matrix[x][y] == 1:
                    self.variables_paths[self.variables_list[x]].append(self.variables_list[y])

    def print_variables_paths(self):
        print("> Зависимости узлов:")
        for variable in self.variables_paths.keys():
            print(variable, self.variables_paths[variable])

    def init_variables_tacts(self):
        variables_tacts = {}
        tact_input = int(input("\nВведите такт: "))

        for variable in self.variables_list:
            variables_tacts[variable] = {}
        variables_tacts["x1"][0] = []

        for tact in range(1, tact_input + 1):
            for x in range(len(self.relation_matrix)):
                if tact - 1 in variables_tacts[self.variables_list[x]].keys():
                    for y in range(len(self.relation_matrix)):
                        if self.relation_matrix[x][y] == 1:
                            if tact in variables_tacts[self.variables_list[y]].keys():
                                variables_tacts[self.variables_list[y]][tact].append(f"{self.variables_list[x]}[{tact-1}]")
                            else:
                                variables_tacts[self.variables_list[y]][tact] = []
                                variables_tacts[self.variables_list[y]][tact].append(f"{self.variables_list[x]}[{tact-1}]")
        print("> Такты:")
        for variable in variables_tacts.keys():
            print(variable, variables_tacts[variable])

    def init_paths_to_2vars(self):
        input_vars = []
        paths = {}
        print("\nВведите узлы для нахождения путей:")
        input_vars.append(input("Первый узел: "))
        input_vars.append(input("Второй узел: "))
        if input_vars[0] not in self.variables_paths.keys() or input_vars[1] not in self.variables_paths.keys():
            print("Некорректные имена узлов.")
            return
        var_start_name = input_vars[0]
        var_start_list = self.variables_paths[var_start_name]
        var_end_name = input_vars[1]
        var_end_list = self.variables_paths[var_end_name]

        def append_path(path):
            length = len(path) + 1
            if length not in paths.keys():
                paths[length] = []
            paths[length].append(path)

        def append_var(path, var):
            path.append(var)
            return path

        def recursion(var_list, path):
            for var in var_list:
                if var == var_start_name or var in path:
                    continue
                elif var == var_end_name:
                    append_path(path)
                    continue
                else:
                    new_path = copy.deepcopy(path)
                    recursion(self.variables_paths[var], append_var(new_path, var))

        recursion(var_start_list, [])

        count_length = {}
        count_length["всего"] = 0
        max_length = max(paths.keys())

        for length in range(max_length + 1):
            if length in paths.keys():
                print(length, paths[length])
                count_length[length] = len(paths[length])
                count_length["всего"] += len(paths[length])
        for length in count_length.keys():
            print(f"Путей с количеством связей {length}: {count_length[length]}")

    def delete_relationship(self):
        input_vars = []
        print("\nВведите узлы для изменения связи:")
        input_vars.append(input("Первый узел: "))
        input_vars.append(input("Второй узел: "))
        relationship = input("Введите номер связи: ")

        x = np.where(self.variables_list == input_vars[0])[0][0]
        y = np.where(self.variables_list == input_vars[1])[0][0]

        self.relation_matrix[x][y] = relationship
        self.print_relation_matrix()

    def plot_variable_graph(self):
        G = nx.DiGraph()
        block_dict = defaultdict(list)

        for var in self.variables_list:
            block_key = var[0]
            block_dict[block_key].append(var)

        for var in self.variables_list:
            G.add_node(var)

        for i in range(len(self.variables_list)):
            for j in range(len(self.variables_list)):
                if self.relation_matrix[i][j] == 1:
                    G.add_edge(self.variables_list[i], self.variables_list[j])

        pos = {}
        block_offset_x = 6
        block_offset_y = -2
        block_idx = 0

        def polygon_layout(n, center=(0, 0), radius=5):
            angles = np.linspace(0, 2*np.pi, n, endpoint=False)
            return [
                (
                    center[0] + radius * np.cos(angle),
                    center[1] + radius * np.sin(angle)
                )
                for angle in angles
            ]

        fig, ax = plt.subplots(figsize=(20, 10))

        # Цвета для фонов блоков
        color_cycle = ['#66cc66', '#66b2ff', '#ff66cc', '#ffeb3b', '#b266ff', '#ff9933']
        block_colors = {}

        for block, vars_in_block in block_dict.items():
            num_vars = len(vars_in_block)
            x_offset = block_idx * block_offset_x
            y_offset = block_idx * block_offset_y * (0.1 * (block_idx + 1))
            center = (x_offset, y_offset)

            if num_vars == 1:
                pos[vars_in_block[0]] = center
                positions = [center]
            elif num_vars <= 4:
                positions = polygon_layout(num_vars, center=center, radius=1.5)
            else:
                positions = polygon_layout(num_vars - 1, center=center, radius=1.5)
                positions.append(center)

            for var, p in zip(vars_in_block, positions):
                pos[var] = p

            # Сохраняем цвет блока
            block_colors[block] = color_cycle[block_idx % len(color_cycle)]

            # Рисуем фон — прямоугольник, охватывающий все узлы в блоке
            xs = [p[0] for p in positions]
            ys = [p[1] for p in positions]
            margin = 1.5
            min_x, max_x = min(xs) - margin, max(xs) + margin
            min_y, max_y = min(ys) - margin, max(ys) + margin
            width = max_x - min_x
            height = max_y - min_y

            from matplotlib.patches import Rectangle
            rect = Rectangle(
                (min_x, min_y),
                width, height,
                facecolor=block_colors[block],
                alpha=0.3,
                edgecolor='none',
                zorder=0
            )
            ax.add_patch(rect)

            block_idx += 1

        nx.draw(
            G, pos, with_labels=True,
            node_color='lightgreen', node_size=1500,
            edge_color='gray', arrows=True,
            font_size=10, font_weight='bold',
            ax=ax
        )
        plt.title("Граф связей между блоками узлов")
        plt.axis('off')
        plt.show()

    def plot_paths_between_two_vars(self):
        input_vars = []
        print("\nВведите узлы для отображения путей:")
        input_vars.append(input("Первый узел: "))
        input_vars.append(input("Второй узел: "))

        var_start = input_vars[0]
        var_end = input_vars[1]

        if var_start not in self.variables_paths or var_end not in self.variables_paths:
            print("Некорректные имена узлов.")
            return

        all_paths = []

        def dfs(current, path):
            if current == var_end:
                all_paths.append(path + [current])
                return
            for neighbor in self.variables_paths[current]:
                if neighbor not in path:  # избегаем циклов
                    dfs(neighbor, path + [current])

        dfs(var_start, [])

        if not all_paths:
            print("Пути не найдены.")
            return

        # Получаем узлы и связи, участвующие в путях
        sub_vars = set()
        edges = set()
        for path in all_paths:
            sub_vars.update(path)
            for i in range(len(path) - 1):
                edges.add((path[i], path[i + 1]))

        G = nx.DiGraph()
        G.add_nodes_from(sub_vars)
        G.add_edges_from(edges)

        # Блокировка по первой букве имени узлов
        from collections import defaultdict
        block_dict = defaultdict(list)
        for var in sub_vars:
            block_key = var[0]
            block_dict[block_key].append(var)

        def polygon_layout(n, center=(0, 0), radius=5):
            angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
            return [
                (
                    center[0] + radius * np.cos(angle),
                    center[1] + radius * np.sin(angle)
                )
                for angle in angles
            ]

        pos = {}
        block_offset_x = 6
        block_offset_y = -2
        block_idx = 0

        fig, ax = plt.subplots(figsize=(20, 10))
        color_cycle = ['#66cc66', '#66b2ff', '#ff66cc', '#ffeb3b', '#b266ff', '#ff9933']
        block_colors = {}

        for block, vars_in_block in block_dict.items():
            num_vars = len(vars_in_block)
            x_offset = block_idx * block_offset_x
            y_offset = block_idx * block_offset_y * (0.1 * (block_idx + 1))  # динамика
            center = (x_offset, y_offset)

            if num_vars == 1:
                positions = [center]
            elif num_vars <= 4:
                positions = polygon_layout(num_vars, center=center, radius=1.5)
            else:
                positions = polygon_layout(num_vars - 1, center=center, radius=1.5)
                positions.append(center)

            for var, p in zip(vars_in_block, positions):
                pos[var] = p

            # Цветной фон блока
            block_colors[block] = color_cycle[block_idx % len(color_cycle)]
            xs = [p[0] for p in positions]
            ys = [p[1] for p in positions]
            margin = 1.5
            min_x, max_x = min(xs) - margin, max(xs) + margin
            min_y, max_y = min(ys) - margin, max(ys) + margin
            width = max_x - min_x
            height = max_y - min_y

            from matplotlib.patches import Rectangle
            rect = Rectangle(
                (min_x, min_y),
                width, height,
                facecolor=block_colors[block],
                alpha=0.3,
                edgecolor='none',
                zorder=0
            )
            ax.add_patch(rect)

            block_idx += 1

        # Рисуем граф
        nx.draw(
            G, pos, with_labels=True,
            node_color='lightgreen', node_size=1500,
            edge_color='gray', arrows=True,
            font_size=10, font_weight='bold',
            ax=ax
        )
        plt.title(f"Граф путей от {var_start} до {var_end}")
        plt.axis('off')
        plt.show()

def start_program(restart):
    global object
    if restart is True:
        del object
    object = Relationships()

    object.init_variables_config()
    object.init_variables_list()
    object.print_variables_list()

    object.init_matrix_config()
    object.init_relation_matrix()
    object.print_relation_matrix()

    object.init_variables_paths()

    return object

object = start_program(False)
while True:
    # МЕНЮ
    print("\n0. Сменить конфигурацию матрицы;\n"
          "1. Вывести список узлов;\n"
          "2. Вывести матрицу связей;\n"
          "3. Вывести перечни зависимых узлов;\n"
          "4. Вывести перечень путей между двумя узлами;\n"
          "5. Вывести пути по тактам;\n"
          "6. Изменить связь между двумя узлами;\n"
          "7. Построить граф связей между узлами;\n"
          "8. Построить граф связей для двух узлов;")

    choice = input("Выберите один из пунктов (0-8): ")
    if choice == "0":
        start_program(True)
    elif choice == "1":
        object.print_variables_list()
    elif choice == "2":
        object.print_relation_matrix()
    elif choice == "3":
        object.print_variables_paths()
    elif choice == "4":
        object.init_paths_to_2vars()
    elif choice == "5":
        object.init_variables_tacts()
    elif choice == "6":
        object.delete_relationship()
    elif choice == "7":
        object.plot_variable_graph()
    elif choice == "8":
        object.plot_paths_between_two_vars()
    else:
        print("Нет такого пункта меню.\n")

        """relationships.xlsx"""
        """C:J_2:2"""
        """C:J_3:10"""
        """C:O_13:13"""
        """C:O_14:26"""
