from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale
from pathlib import Path
import os
from datetime import datetime
from decimal import Decimal


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path
        # Создаем все файлы для дальнейшей записи данных. Где атрибут функции
        # это полный путь к директории где храняться файлы.
        self.models_file = root_directory_path + '/models.txt'
        self.models_index_file = root_directory_path + '/models_index.txt'
        self.cars_file = root_directory_path + '/cars.txt'
        self.cars_index_file = root_directory_path + '/cars_index.txt'
        self.sales_file = root_directory_path + '/sales.txt'
        self.sales_index_file = root_directory_path + '/sales_index.txt'
        Path(self.models_file).touch(exist_ok=True)
        Path(self.models_index_file).touch(exist_ok=True)
        Path(self.cars_file).touch(exist_ok=True)
        Path(self.cars_index_file).touch(exist_ok=True)
        Path(self.sales_file).touch(exist_ok=True)
        Path(self.sales_index_file).touch(exist_ok=True)

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        # Разбираем объект Model по атрибутам и записываем в строку через ;
        # с применением ljust(500)
        row_data = f'{model.id};{model.name};{model.brand}'.ljust(500)
        total_row_data = row_data + '\n'
        # Записываем полученные данные в конец файла models_file.
        with open(self.models_file, 'a', encoding='utf-8') as f:
            f.write(total_row_data)
        # Определеяем список с данными для индексного файла.
        list_data_index = []
        # Делаем проверку на пустой файл. Если пусто, то вносим значения
        # с индексом 0 и выходим из функции.
        if os.path.getsize(self.models_index_file) == 0:
            with open(self.models_index_file, 'a', encoding='utf-8') as f:
                f.write(f'{model.id};0\n')
                return model
        else:
            # Построчно читаем файл models_index_file. Передаем данные
            # в список для дальнейшей обработки.
            with open(self.models_index_file, 'r', encoding='utf-8') as f:
                for line in f:
                    list_data_index.append(line.strip().split(';'))
                # Определяем следующий индекс для файла по длине текущего.
                next_index = len(list_data_index)
                list_data_index.append([str(model.id), str(next_index)])
                list_data_index.sort(key=lambda x: x[0])
        # Преобразуем данные из списка в строку для записи в файл.
        write_data = ''
        for i in range(next_index + 1):
            write_data += ';'.join(list_data_index[i]) + '\n'

        with open(self.models_index_file, 'w', encoding='utf-8') as f:
            f.write(write_data)

        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        # Аналогично add_model
        row_data = (
            f'{car.vin};{car.model};{car.price};'
            f'{car.date_start};{car.status.value.strip()}'.ljust(500)
            )
        total_row_data = row_data + '\n'

        with open(self.cars_file, 'a', encoding='utf-8') as f:
            f.write(total_row_data)

        list_data_index = []
        if os.path.getsize(self.cars_index_file) == 0:
            with open(self.cars_index_file, 'a', encoding='utf-8') as f:
                f.write(f'{car.vin};0\n')
                return car
        else:
            with open(self.cars_index_file, 'r', encoding='utf-8') as f:
                for line in f:
                    list_data_index.append(line.strip().split(';'))
                # Определяем следующий индекс для файла по длине текущего.
                next_index = len(list_data_index)
                list_data_index.append([str(car.vin), str(next_index)])
                list_data_index.sort(key=lambda x: x[0])
        # Преобразуем данные из списка в строку для записи в файл.
        write_data = ''
        for i in range(next_index + 1):
            write_data += ';'.join(list_data_index[i]) + '\n'

        with open(self.cars_index_file, 'w', encoding='utf-8') as f:
            f.write(write_data)

        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        # Формируем данные из атрибутов объекта класса Sale для
        # дальнейшей записи в файлы.
        row_data = (
            f'{sale.sales_number};{sale.car_vin};'
            f'{sale.cost};{sale.sales_date}'.ljust(500)
            )
        total_row_data = row_data + '\n'

        with open(self.sales_file, 'a', encoding='utf-8') as f:
            f.write(total_row_data)

        # Ищем индекс в файле cars_index_file по номеру vin.
        with open(self.cars_index_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().split(';')[0] == sale.car_vin:
                    result_index = line.strip().split(';')[1]
        # По найденному индексу ищем строку в файле cars_file и изменяем
        # статус на sold.
        with open(self.cars_file, 'r+', encoding='utf-8') as f:
            f.seek(int(result_index) * 501)
            # Читаем только первые 500 символов в нужной строке (без \n).
            clean_data = f.read(500).strip().split(';')
            clean_data[-1] = CarStatus.sold.value
            new_data = ';'.join(clean_data).ljust(500)
            # Возвращаемся обратно с исходную позицию для дальнейшей записи.
            f.seek(int(result_index) * 501)
            f.write(new_data)
        # Формируем переменную типа datetime для преобразования данных
        # из clean_data в целях отражения обновленной информации в return.
        dt = datetime.strptime(clean_data[3], "%Y-%m-%d %H:%M:%S")
        # Вносим изменения в индексный файл продаж sales_index_file.
        list_data_index = []
        if os.path.getsize(self.sales_index_file) == 0:
            with open(self.sales_index_file, 'a') as f:
                f.write(f'{sale.sales_number};0\n')
                return Car(
                    vin=clean_data[0],
                    model=int(clean_data[1]),
                    price=Decimal(clean_data[2]),
                    date_start=dt,
                    status=CarStatus.sold
                    )
        else:
            with open(self.sales_index_file, 'r', encoding='utf-8') as f:
                for line in f:
                    list_data_index.append(line.strip().split(';'))
                # Определяем следующий индекс для файла по длине текущего.
                next_index = len(list_data_index)
                list_data_index.append(
                    [str(sale.sales_number),
                     str(next_index)]
                     )
                list_data_index.sort(key=lambda x: x[0])
        # Преобразуем данные из списка в строку для записи в файл.
        write_data = ''
        for i in range(next_index + 1):
            write_data += ';'.join(list_data_index[i]) + '\n'

        with open(self.sales_index_file, 'w', encoding='utf-8') as f:
            f.write(write_data)

        return Car(
            vin=clean_data[0],
            model=int(clean_data[1]),
            price=Decimal(clean_data[2]),
            date_start=dt,
            status=CarStatus.sold
            )

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        cars = []
        with open(self.cars_file, 'r', encoding='utf-8') as f:
            # Читаем построчно файл.
            for line in f:
                # Ищем условие, что в строке есть статус из атрибута
                # функции get_cars.
                if line.strip().split(';')[-1] == status.value.strip():
                    clean_data = line.strip().split(';')
                    dt = datetime.strptime(clean_data[3], "%Y-%m-%d %H:%M:%S")
                    price = Decimal(clean_data[2])
                    # Если строка с требуемым статусом найдена, то добавляем
                    # в список объект класса Car.
                    cars.append(Car(
                        vin=clean_data[0],
                        model=int(clean_data[1]),
                        price=price,
                        date_start=dt,
                        status=CarStatus(clean_data[4])
                    )
                    )

        return cars

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        index = None
        # Ищем в файле cars_index_file строку с искомым vin.
        with open(self.cars_index_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Если строка найдена, то извлекаем номер индекса по vin.
                if vin in line:
                    index = line.strip().split(';')[1]
                    break
        if index is None:
            return None
        # Ищем в файле cars_file строку по найденному индексу.
        with open(self.cars_file, 'r', encoding='utf-8') as f:
            f.seek(int(index) * 501)
            # В data содержится [0] - vin, [1] - ключ из Model, [2] - price,
            # [3] - data, [4] - status.
            data = f.read(500).strip().split(';')
            # Делаем сразу проверку статуса автомобиля. Если статус sold,
            # то ищем информацию в файле sales_file.
            if data[4] == 'sold':
                with open(self.sales_file, 'r', encoding='utf-8') as sf:
                    for line in sf:
                        # Делаем проверку вхождения искомого vin в строки
                        # файла продаж и извлекаем данные о дате и цене
                        # продажи. Иначе значение цены None.
                        if line.strip().split(';')[1] == data[0]:
                            data_sale = line.strip().split(';')[-1]
                            cost_sale = line.strip().split(';')[-2]
            else:
                cost_sale = None
        # Ищем в файле с индексами брендов model_index_file данные
        # по id модели data[1].
        with open(self.models_index_file, 'r', encoding='utf-8') as f:
            for line in f:
                model_id = line.strip().split(';')[0]
                if model_id == data[1]:
                    model_index = line.strip().split(';')[1]
        # Ищем модель и наименование бренда в файле models_file по полученному
        # индексу model_index.
        with open(self.models_file, 'r', encoding='utf-8') as f:
            f.seek(int(model_index) * 501)
            data_model = f.read(500).strip().split(';')

        dt = datetime.strptime(data[3], "%Y-%m-%d %H:%M:%S")
        if cost_sale is not None:
            dt_sale = datetime.strptime(data_sale, "%Y-%m-%d %H:%M:%S")
        else:
            dt_sale = None
        # Наполняем соответсвующими атрибутами объект CarFullInfo.
        return CarFullInfo(
            vin=data[0],
            car_model_name=data_model[1],
            car_model_brand=data_model[2],
            price=Decimal(data[2]),
            date_start=dt,
            status=CarStatus(data[4]),
            sales_date=dt_sale,
            sales_cost=Decimal(cost_sale) if cost_sale is not None else None
            )

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        # Ищем старый vin в файле с индексами и исправляем на new_vin.
        with open(self.cars_index_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().split(';')[0] == vin:
                    index = line.strip().split(';')[1]
                    break
        # Теперь ищем по индексу из файла cars_index_file нужную строку
        # и обновляем в ней vin - find_data[0].
        with open(self.cars_file, 'r+', encoding='utf-8') as f:
            f.seek(int(index) * 501)
            find_data = f.read(500).strip().split(';')
            find_data[0] = new_vin
            f.seek(int(index) * 501)
            update_data = ';'.join(find_data).ljust(500)
            f.write(update_data)

        dt = datetime.strptime(find_data[-2], "%Y-%m-%d %H:%M:%S")

        list_data_index = []
        with open(self.cars_index_file, 'r', encoding='utf-8') as f:
            for line in f:
                list_data_index.append(line.strip().split(';'))
        for i, value in enumerate(list_data_index):
            if value[0] == vin:
                list_data_index[i][0] = new_vin
                break
        list_data_index.sort(key=lambda x: x[0])
        # Преобразуем данные из списка в строку для записи в файл.
        write_data = ''
        for i in range(len(list_data_index)):
            write_data += ';'.join(list_data_index[i]) + '\n'

        with open(self.cars_index_file, 'w', encoding='utf-8') as f:
            f.write(write_data)

        return Car(
            vin=find_data[0],
            model=int(find_data[1]),
            price=Decimal(find_data[2]),
            date_start=dt,
            status=CarStatus(find_data[-1])
        )

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        # Читаем индексный файл sales_index_file и находим
        # индекс номера продажи.
        with open(self.sales_index_file, 'r', encoding='utf-8') as f:
            for line in f:
                if sales_number in line:
                    index = line.strip().split(';')[1]
                    break
        # Ищем vin и обновляем информацию в основном файле.
        with open(self.sales_file, 'r+', encoding='utf-8') as f:
            f.seek(int(index) * 501)
            sales_info = f.read(500).strip().split(';')
            car_vin = sales_info[1]
            f.seek(int(index) * 501)
            # Добавляем информацию о том, что запись удалена.
            sales_info.append('deleted')
            update_line = ';'.join(sales_info).ljust(500)
            f.write(update_line)
        # Читаем индексный файл cars_index_file для поиска индекса авто.
        with open(self.cars_index_file, 'r', encoding='utf-8') as f:
            for line in f:
                if car_vin in line:
                    car_index = line.strip().split(';')[1]
                    break
        # Ищем соответствующую строку в основном файле и меняем статус
        # на available.
        with open(self.cars_file, 'r+', encoding='utf-8') as f:
            f.seek(int(car_index) * 501)
            target_car = f.read(500).strip().split(';')
            if target_car[-1] == CarStatus.sold.value:
                target_car[-1] = CarStatus.available.value
            f.seek(int(car_index) * 501)
            update_data = ';'.join(target_car).ljust(500)
            f.write(update_data)

        dt = datetime.strptime(target_car[-2], "%Y-%m-%d %H:%M:%S")

        return Car(
            vin=target_car[0],
            model=int(target_car[1]),
            price=Decimal(target_car[2]),
            date_start=dt,
            status=CarStatus.available
        )

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        # Наполняем словарь с key - vin и value - индексами.
        vin_index = {}
        with open(self.cars_index_file, 'r', encoding='utf-8') as f:
            for line in f:
                vin_info = line.strip().split(';')
                vin_index[vin_info[0]] = vin_info[1]
        # Наполняем словарь с информацией о моделях: key - id,
        # value - (name, brand).
        model_info = {}
        with open(self.models_file, 'r', encoding='utf-8') as f:
            for line in f:
                model_data = line.strip().split(';')
                model_id = model_data[0]
                model_name = model_data[1]
                model_brand = model_data[2]
                model_info[model_id] = (model_name, model_brand)
        # Формируем основной словарь с продажами. Словарь с key - model_id,
        # value - список [количество продаж, цена продажи].
        sales_dict: dict = {}
        with open(self.sales_file, 'r', encoding='utf-8') as f:
            for line in f:
                vin = line.strip().split(';')[1]
                if vin in vin_index:
                    index = vin_index[vin]

                with open(self.cars_file, 'r', encoding='utf-8') as car_f:
                    car_f.seek(int(index) * 501)
                    car_info = car_f.read(500).strip().split(';')
                    model_id = car_info[1]
                    price = car_info[2]
                    if model_id in sales_dict:
                        sales_dict[model_id][0] += 1
                    else:
                        sales_dict[model_id] = [1, Decimal(price)]

        sorted_items = sorted(
            sales_dict.items(),
            key=lambda x: (-x[1][0], -x[1][1])
            )

        result = []
        for i, (key, value) in enumerate(sorted_items):
            if i >= 3:
                break
            count = int(value[0])
            model_name = model_info[key][0]
            brand_name = model_info[key][1]
            result.append(ModelSaleStats(
                        car_model_name=model_name,
                        brand=brand_name,
                        sales_number=count
                    ))

        return result
