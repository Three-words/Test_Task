from pylibdmtx.pylibdmtx import encode  # type: ignore
from PIL import Image, ImageOps


class DataMatrixGenerator:
    def __init__(self):
        self.module_mm = 0.381
        self.dpi = 600
        self.quiet_zone_modules = 4
        self.encoding = "utf-8"
        self.output_file = "datamatrix.svg"

        # Названия типов
        self.type_names = [
            "Тип 1",
            "Тип 2"
        ]

        # Префиксы
        self.prefixes = [
            b"[)>\x1e06\x1d25S",
            b"[)>\x1e06\x1d68P"
        ]

        # Размеры в модулях
        self.module_sizes = [
            20,  
            18    
        ]

        # Общий суффикс
        self.suffix = b"\x1e\x04"

    def show_types(self):
        print("Доступные типы:")
        for i, type_name in enumerate(self.type_names):
            print(
                f"{i + 1} — {type_name}, "
                f"{self.module_sizes[i]}x{self.module_sizes[i]} модулей"
            )

    def get_type_index(self, user_type):
        """
        Преобразуем номер типа в индекс массива
        """
        try:
            index = int(user_type) - 1
        except ValueError:
            raise ValueError("Тип должен быть числом")

        if index < 0 or index >= len(self.type_names):
            raise ValueError("Такого типа нет")

        return index

    def build_data(self, type_index, body):
        """
        Собираем байтовую строку:
        префикс + тело + суффикс
        """
        prefix = self.prefixes[type_index]
        body_bytes = body.encode(self.encoding)
        data = prefix + body_bytes + self.suffix
        return data

    def get_symbol_bitmap(self, symbol_modules, data):
        """
        Получаем матрицу Data Matrix из библиотеки,
        убираем белые поля и приводим к сетке N x N модулей.
        """

        datamatrix_size = f"{symbol_modules}x{symbol_modules}"

        try:
            encoded = encode(
                data,
                size=datamatrix_size
            )
        except Exception as error:
            raise ValueError(
                f"Данные не помещаются в Data Matrix {datamatrix_size}"
            ) from error

        image = Image.frombytes(
            "RGB",
            (encoded.width, encoded.height),
            encoded.pixels
        ).convert("L")

        bbox = ImageOps.invert(image).getbbox()

        if bbox is None:
            raise RuntimeError(
                "Не удалось определить границы Data Matrix"
            )

        symbol = image.crop(bbox)

        symbol = symbol.resize(
            (symbol_modules, symbol_modules),
            Image.Resampling.NEAREST
        )

        return symbol

    def create_svg(self, user_type, body):
        """
        Создаём Data Matrix ECC200 и сохраняем в SVG.
        """

        type_index = self.get_type_index(user_type)

        type_name = self.type_names[type_index]
        symbol_modules = self.module_sizes[type_index]
        data = self.build_data(type_index, body)

        print()
        print("Формируемые данные:")
        print(repr(data))
        print("Количество байт:", len(data))

        symbol = self.get_symbol_bitmap(symbol_modules, data)

        full_modules = symbol_modules + 2 * self.quiet_zone_modules

        symbol_size_mm = symbol_modules * self.module_mm
        quiet_zone_mm = self.quiet_zone_modules * self.module_mm
        full_size_mm = full_modules * self.module_mm

        rects = []

        # Фон
        rects.append(
            f'<rect x="0" y="0" width="{full_size_mm:.3f}" '
            f'height="{full_size_mm:.3f}" fill="white"/>'
        )

        # Чёрные модули
        for y in range(symbol_modules):
            for x in range(symbol_modules):
                pixel = symbol.getpixel((x, y))

                # Чёрный модуль
                if pixel < 128:
                    rect_x = (x + self.quiet_zone_modules) * self.module_mm
                    rect_y = (y + self.quiet_zone_modules) * self.module_mm

                    rects.append(
                        f'<rect x="{rect_x:.3f}" y="{rect_y:.3f}" '
                        f'width="{self.module_mm:.3f}" '
                        f'height="{self.module_mm:.3f}" '
                        f'fill="black"/>'
                    )

        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg xmlns="http://www.w3.org/2000/svg"
            width="{full_size_mm:.3f}mm"
            height="{full_size_mm:.3f}mm"
            viewBox="0 0 {full_size_mm:.3f} {full_size_mm:.3f}"
            version="1.1">
            <title>Data Matrix ECC200</title>
            <desc>
                Тип: {type_name}
                Размер модуля: {self.module_mm} мм
                Зона молчания: {self.quiet_zone_modules} модуля
                Размер матрицы: {symbol_modules}x{symbol_modules}
                DPI (справочно): {self.dpi}
            </desc>
            <g shape-rendering="crispEdges">
                {"".join(rects)}
            </g>
        </svg>
        '''

        with open(self.output_file, "w", encoding="utf-8") as file:
            file.write(svg_content)

        self.print_info(type_name, symbol_modules, data)

    def print_info(self, type_name, symbol_modules, data):
        """
        Вывод параметров созданного кода.
        """

        symbol_size_mm = symbol_modules * self.module_mm
        quiet_zone_mm = self.quiet_zone_modules * self.module_mm
        full_size_mm = (
            symbol_modules + 2 * self.quiet_zone_modules
        ) * self.module_mm

        print()
        print("DATA MATRIX ECC200 СОЗДАН")
        print("-------------------------")
        print(f"Тип: {type_name}")
        print(f"Количество байт: {len(data)}")
        print(
            f"Размер Data Matrix: "
            f"{symbol_modules}x{symbol_modules} модулей"
        )
        print(f"Размер модуля: {self.module_mm} мм")
        print(
            f"Размер без зоны молчания: "
            f"{symbol_size_mm:.3f} мм"
        )
        print(
            f"Зона молчания: "
            f"{quiet_zone_mm:.3f} мм"
        )
        print(
            f"Полный размер: "
            f"{full_size_mm:.3f} мм"
        )
        print(f"DPI: {self.dpi} (справочно для SVG)")
        print(f"Файл: {self.output_file}")


if __name__ == "__main__":
    generator = DataMatrixGenerator()

    generator.show_types()

    user_type = input("Выберите тип: ").strip()
    body = input("Введите основное тело: ")

    generator.create_svg(user_type, body)