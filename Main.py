# библиотека OpenCV для работы с изображениями и видео
import cv2
# библиотека для создания GUI
import tkinter as tk
# модули для диалоговых окон
from tkinter import filedialog, messagebox
# библиотека для работы и изображениями
from PIL import Image, ImageTk
# библиотека для числовых операций
import numpy as np
# модуль для работы с операционной системой
import os

class ImageEditApp:
  def __init__(self, root):
    # инициализация главного окна приложения
    self.root = root
    self.root.title("Приложение для учебной практики по обработке изображений")
    # задаем размер окна
    window_width = 800
    window_height = 900
    # присваиваем размеры и запрещаем их изменять
    self.root.geometry(f"{window_width}x{window_height}")
    self.root.resizable(False, False)
    # Основные переменные класса
    self.image = None # для хранения загруженного изображения
    self.photo = None # для хранения изображения в формате Tkinter
    self.camera = None # переменная для работы с камерой
    # Создание элементов интерфейса
    self.create_widgets()

  # создаем GUI
  def create_widgets(self):
    # Создание фрейма для кнопок загрузки изображения
    button_frame = tk.Frame(self.root) # создание контейнера
    button_frame.pack(padx=10, pady=(20,0)) # задаем отступ сверху 20 пикселей,
    # снизу 0 пикселей
    # Кнопки загрузки изображения
    tk.Button(button_frame, text="Загрузить изображение",
              command=self.load_image, bg="#9bcbeb", width=25,
              height=2).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Сделать снимок с веб-камеры",
              command=self.capture_image, bg="#c3a2e8", width=25,
              height=2).pack(side=tk.LEFT, padx=10)
    # tk.Button(button_frame, text="Обновить изображение",
              # command=self.reload_image).pack(side=tk.LEFT, padx=10)

    # Фрейм с заголовком выбора канала по ширине окна с отступом 30 от краев
    channel_frame = tk.LabelFrame(self.root, text="Цветовые каналы",
                                  font=("Tahoma", 10, "bold"), fg="#9e706c",
                                  labelanchor="n", relief=tk.GROOVE,
                                  highlightcolor="#4CAF50",
                                  highlightthickness=2, bd=2, pady=15, padx=10)
    channel_frame.pack(pady=(20,10),padx=30, fill=tk.X)
    # создаем контейнер для центровки содержимого фрейма
    center_container = tk.Frame(channel_frame)
    center_container.pack(expand=True, pady=0)
    (tk.Label(center_container, text="ВЫБОР ФИЛЬТРА ИЗОБРАЖЕНИЯ:    ")
     .pack(side=tk.LEFT))
    # присваиваем переменной выбор канала по умолчанию = оригинал
    self.channel_var = tk.StringVar(value="original")
    # создаем кнопки с выбором канала
    (tk.Radiobutton(center_container, text="Оригинал",
                    variable=self.channel_var, value="original",
                    command=self.update_image).pack(side=tk.LEFT))
    tk.Radiobutton(center_container, text="  Красный  ",
                   variable=self.channel_var, value="red",
                   command=self.update_image, fg='#d32f2f').pack(side=tk.LEFT)
    tk.Radiobutton(center_container, text="  Зеленый  ",
                   variable=self.channel_var, value="green",
                   command=self.update_image, fg='#388e3c').pack(side=tk.LEFT)
    tk.Radiobutton(center_container, text="  Синий  ",
                   variable=self.channel_var, value="blue",
                   command=self.update_image, fg='#1976d2').pack(side=tk.LEFT)
    # Основной фрейм для редактирования изображения по ширине окна с отступом 30
    edit_frame = tk.LabelFrame(self.root, text="Редактирование изображения",
                               font=("Tahoma", 10, "bold"), fg="#2f11d6",
                               labelanchor="n", padx=10, pady=10,
                               relief=tk.GROOVE, bd=2, width=10)
    edit_frame.pack(pady=10,padx=30, fill=tk.X)
    #edit_frame.pack_propagate(False)
    # Фрейм для усреднения
    blur_frame = tk.Frame(edit_frame)
    blur_frame.pack(pady=(5,10))
    tk.Label(blur_frame, text="Усреднение (размер ядра):").pack(side=tk.LEFT)
    # Проверка ввода с клавиатуры (для ввода только чисел)
    vcmd = (self.root.register(self.validate_number), '%P')
    self.blur_val = tk.Entry(blur_frame, validate="key", validatecommand=vcmd,
                               width=10)
    self.blur_val.pack(side=tk.LEFT, padx=5)
    # кнопка для усренения изображения
    (tk.Button(blur_frame, text="Применить", command=self.apply_blur)
    .pack(side=tk.LEFT))
    # Кнопка оттенков серого
    tk.Button(edit_frame, text="Оттенки серого",
              command=self.convert_to_gray, bg="#857f7e", fg="white",
              width=25, height=2, font=("Tahoma", 10, "bold")).pack(pady=5)
    # Фрейм для отрисовки прямоугольника
    rect_frame = tk.Frame(edit_frame)
    rect_frame.pack(pady=(10,5))
    tk.Label(rect_frame, text="Добавить прямоугольник на изображение по "
                              "координатам (x1,y1,x2,y2)").pack()
    # Фрейм для координат
    coords_frame = tk.Frame(rect_frame)
    coords_frame.pack(pady=5)
    tk.Label(coords_frame, text="X1:").grid(row=0, column=0)
    self.x1_entry = tk.Entry(coords_frame, validate="key", validatecommand=vcmd,
                             width=8)
    self.x1_entry.grid(row=0, column=1, padx=5)
    tk.Label(coords_frame, text="Y1:").grid(row=0, column=2)
    self.y1_entry = tk.Entry(coords_frame, validate="key", validatecommand=vcmd,
                             width=8)
    self.y1_entry.grid(row=0, column=3, padx=5)
    tk.Label(coords_frame, text="X2:").grid(row=1, column=0)
    self.x2_entry = tk.Entry(coords_frame, validate="key", validatecommand=vcmd,
                             width=8)
    self.x2_entry.grid(row=1, column=1, padx=5)
    tk.Label(coords_frame, text="Y2:").grid(row=1, column=2)
    self.y2_entry = tk.Entry(coords_frame, validate="key", validatecommand=vcmd,
                             width=8)
    self.y2_entry.grid(row=1, column=3, padx=5)
    # добавляем кнопки для отрисовки прямоугольника справа от поля Y2
    tk.Button(coords_frame, text="   Добавить!   ",
              command=self.get_rectangle).grid(row=1, column=4, padx=(20,5))
    # Формируем поле для отображения изображения
    self.imgField = tk.Canvas(self.root, width=600, height=400, bg='gray')
    self.imgField.pack(pady=10)
    # Кнопка выхода
    tk.Button(self.root, text="   ЗАКРЫТЬ ПРИЛОЖЕНИЕ   ",
              command=self.root.quit, bg="#f0bd84", width=25, height=2,
              font=("Tahoma", 10, "bold")).pack(pady=10)
  # функция для проверки ввода символов с клавиатуры
  def validate_number(self, P):
    if P == "":
      return True
    try:
      int(P)
      return True
    except ValueError:
      return False

  # функция запускаемая при нажатии кнопки "Загрузить изображение"
  def load_image(self):
    # запускаем файловое диалоговое окно с возможностью выбора только
    # изображений, путь к выбранному изображению записываем в переменную
    file_path = filedialog.askopenfilename(
        filetypes=[("Изображения", "*.jpg *.jpeg *.png")]
    )
    if not file_path:
      messagebox.showinfo("Отмена выбора файла","Файл не выбран!")
      return
    try:
      # Проверка расширения файла
      ext = os.path.splitext(file_path)[1].lower() # получаем расширение в
      # переменную ext (кортеж: [0] - путь; [1] - расширение)
      if ext not in ('.jpg', '.jpeg', '.png'):
        messagebox.showerror("Ошибка",
                            "Поддерживаются только файлы JPG/JPEG/PNG")
        return
      # Загрузка изображения с помощью OpenCV
      with open(file_path, 'rb') as f: # открываем файл в бинарном режиме +
        # чтобы корректно считывал кириллицу
        file_bytes = bytearray(f.read()) # читаем содержимое файла
      # декодируем изображение из массива байтов и присваиваем переменной для
      # хранения загруженного изображения
      self.image = cv2.imdecode(np.asarray(file_bytes, dtype=np.uint8),
                                cv2.IMREAD_COLOR)
      if self.image is None:
        raise Exception("Не удалось загрузить изображение")
      # Конвертация из BGR (формат OpenCV) в RGB (формат для отображения)
      self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
      # Обновляем отображение (функция update_image)
      self.update_image()
    except Exception as e:
      messagebox.showerror("Ошибка",
                          f"Ошибка при загрузке изображения: {str(e)}")

  # функция запускаемая при нажатии кнопки "Сделать снимок с веб-камеры"
  def capture_image(self):
    # попытка подключится к веб-камере
    try:
      # Проверяем не подключена ли камера ранее
      if self.camera is None:
        # инициализируем подключение к камере (0 - индекс камеры по умолчанию)
        self.camera = cv2.VideoCapture(0)
        # проверяем успешность подключения к камере
        if not self.camera.isOpened():
          # если камера не доступна генерируем исключение
          raise Exception("Не удалось подключиться к веб-камере")
      # Создание окна для предпросмотра камеры (Toplevel - всплывающее окно)
      preview = tk.Toplevel(self.root)
      preview.title("Предпросмотр камеры")
      # создаем метку (Label) для отображения изображения с камеры
      label = tk.Label(preview)
      label.pack() # размещаем метку в окне
      # кнопка для снимка с веб-камеры
      # lambda используется для передачи параметра (окна предосмотра) в функцию
      # take_photo
      tk.Button(preview, text="Сделать снимок",
                command=lambda: self.take_photo(preview)).pack(pady=10)
      # внутренняя функция для обновления изображения в окне предпросмотра,
      # читает кадр с камеры, конвертирует его в формат RGB? преобразует в
      # формат для Tkinter и обновляет изображение в метке
      def update_preview():
        # читает кадр с камеры (ret - флаг успешности чтения (true/false);
        # frame - сам кадр (numpy array)
        ret, frame = self.camera.read()
        if ret: # если кадр успешно прочитан
          # Конвертация из BGR (формат OpenCV) в RGB (формат для отображения)
          frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
          # преобразуем numpy array  в изображение PIL
          img = Image.fromarray(frame)
          # создаем совместимый с Tkinter объект изображения
          imgtk = ImageTk.PhotoImage(image=img)
          # сохраняем ссылку на изображение, чтобы оно не удалилось сборщиком
          # мусора
          label.imgtk = imgtk
          # обновляем изображение в метке
          label.configure(image=imgtk)
        # планируем следующий вызов функции через 10mc
        label.after(10, update_preview)
      # первый вызов функции обновления препросмотра
      update_preview()
    except Exception as e:
      messagebox.showerror("Ошибка",
                           f"Ошибка при работе с камерой: {str(e)}\n\n"
                           "Возможные решения:\n"
                           "1. Проверьте подключение камеры\n"
                           "2. Убедитесь, что камера не используется другим "
                           "приложением\n"
                           "3. Проверьте права доступа к камере\n"
                           "4. Установите драйверы для вашей камеры")
      # если камера была подключена, освобождаем ресурсы
      if self.camera:
        self.camera.release()
        self.camera = None
  #def reload_image(self):
    #messagebox.showinfo("",":))))))")

  # функция, которая захватывает текущий кадр с веб-камеры и сохраняет его как
  # изображение
  def take_photo(self, preview_window):
    # проверяем инициализирована ли камера (защита от вызова без
    # предварительного открытия камеры)
    if self.camera:
      # читаем кадр с камеры (ret - флаг успешности чтения (true/false);
      # frame - сам кадр (numpy array)
      ret, frame = self.camera.read()
      if ret:
        # # Конвертация полученного изображения с веб-камеры из BGR (формат
        # OpenCV) в RGB (формат для отображения)
        self.image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Обновляем отображение (функция update_image)
        self.update_image()
        # закрываем окно предпросмотра
        preview_window.destroy()
        # Освобождение камеры после съемки
        self.camera.release()
        self.camera = None

  # функция для обновления изображения в основном экране
  def update_image(self):
    # проверка наличия изображения (переменная не пуста)
    if self.image is None:
      return
    # в переменную записываем значение выбранного канала
    channel = self.channel_var.get()
    # в переменную display_image копируем изображение, чтобы не менять оригинал,
    # после применяем выбранный канал и масштабируем его для вывода в форме
    display_image = self.image.copy()
    # применяем выбранный цветовой фильтр (оставляем только выбранный канал)
    if channel == "red":
      display_image[:, :, 1] = 0  # Обнуляем зеленый канал
      display_image[:, :, 2] = 0  # Обнуляем синий канал
    elif channel == "green":
      display_image[:, :, 0] = 0  # Обнуляем красный канал
      display_image[:, :, 2] = 0  # Обнуляем синий канал
    elif channel == "blue":
      display_image[:, :, 0] = 0  # Обнуляем красный канал
      display_image[:, :, 1] = 0  # Обнуляем зеленый канал
    # Масштабирование изображения для отображения
    # получаем размеры изображения
    h, w = display_image.shape[:2]
    # вычисляем коэффициент масштабирования для вписывания в окно 600х400 с
    # сохранением пропорций
    ratio = min(600 / w, 400 / h)
    # вычисляем новые размеры с учетом полученного коэф-та
    new_w, new_h = int(w * ratio), int(h * ratio)
    img = Image.fromarray(display_image)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    # конвертируем в формат, совместимый с Tkinter
    self.photo = ImageTk.PhotoImage(image=img)
    # Очистка содержимого окна и отображение в нем нового изображения
    self.imgField.delete("all")
    # обновляем размеры поля для нового изображения
    self.imgField.config(width=new_w, height=new_h)
    # размещаем изображение по центру
    self.imgField.create_image(new_w // 2, new_h // 2, image=self.photo)

  # функция для усреднения изображения
  def apply_blur(self):
    if self.image is None:
      messagebox.showwarning("Ошибка", "Сначала загрузите "
                                       "изображение")
      return
    # получаем значение размытия изображения
    blur_val = self.blur_val.get()
    if not blur_val:
      messagebox.showwarning("Ошибка", "Введите размер ядра")
      return
    try:
      # проверяем что целое число
      kernel_size = int(blur_val)
      # проверяем что число удовлетворяет условиям
      if kernel_size < 3:
        messagebox.showwarning("Ошибка", "Размер ядра должен быть"
                                         " не менее 3")
        return
      if kernel_size % 2 == 0:
        messagebox.showwarning("Ошибка", "Размер ядра должен быть"
                                         " нечетным")
        return
      # Применение размытия
      blurred = cv2.blur(self.image, (kernel_size, kernel_size))
      self.image = blurred
      # вызов функция обновления изображения в приложении
      self.update_image()
      self.blur_val.delete(0, tk.END)
    except Exception as e:
      messagebox.showerror("Ошибка", f"Ошибка при усреднении: "
                                     f"{str(e)}")
      self.blur_val.delete(0, tk.END)
  
  # функция вызываемая при нажатии кнопки "Оттенки серого"
  def convert_to_gray(self):
    if self.image is None:
      messagebox.showwarning("Ошибка", "Сначала загрузите "
                                       "изображение")
      return
    try:
      # Конвертация в оттенки серого
      gray = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
      # Преобразуем обратно в 3-канальное изображение для отображения
      self.image = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
      # вызов функция обновления изображения в приложении
      self.update_image()
    except Exception as e:
      messagebox.showerror("Ошибка", f"Ошибка при конвертации: "
                                     f"{str(e)}")

  def get_rectangle(self):
    if self.image is None:
      messagebox.showwarning("Ошибка", "Сначала загрузите "
                                       "изображение")
      return
    # Получаем значения из полей ввода
    x1_str = self.x1_entry.get()
    y1_str = self.y1_entry.get()
    x2_str = self.x2_entry.get()
    y2_str = self.y2_entry.get()
    # Проверяем, что все поля заполнены
    if not all([x1_str, y1_str, x2_str, y2_str]):
      messagebox.showwarning("Ошибка", "Не все поля заполнены")
      return
    try:
      # Проверяем что все поля конвертируются в число
      x1 = int(x1_str)
      y1 = int(y1_str)
      x2 = int(x2_str)
      y2 = int(y2_str)
      # Проверка, что координаты в пределах изображения
      h, w = self.image.shape[:2]
      if (x1 >= w or x2 >= w or y1 >= h or y2 >= h or x1 < 0 or x2 < 0 or y1 < 0 
          or y2 < 0):
        messagebox.showwarning("Ошибка",
                      "Координаты выходят за пределы изображения")
        self.clear_inputFields()
        return
      # Проверка, что прямоугольник можно нарисовать (x1 < x2 и y1 < y2)
      if x1 >= x2 or y1 >= y2:
        messagebox.showwarning("Ошибка",
                      "Невозможно нарисовать прямоугольник: X1 должен "
                      "быть меньше X2, Y1 должен быть меньше Y2")
        self.clear_inputFields()
        return
      # Рисуем прямоугольник (синий цвет в RGB - (0, 0, 255))
      cv2.rectangle(
          self.image,
          (x1, y1),
          (x2, y2),
          (0, 0, 255),
          3  # Толщина линии
      )
      # обновляем изображение
      self.update_image()
      # очищаем поля
      self.clear_inputFields()
    except Exception as e:
      messagebox.showerror("Ошибка", f"Ошибка при рисовании: "
                                     f"{str(e)}")
      self.clear_inputFields()

  # функция для очистки полей ввода координат после отрисовки треугольника
  def clear_inputFields(self):
    self.x1_entry.delete(0, tk.END)
    self.y1_entry.delete(0, tk.END)
    self.x2_entry.delete(0, tk.END)
    self.y2_entry.delete(0, tk.END)

  # функция для завершения работы по кнопке ВЫХОД, освобождение системных
  # ресурсов (камеры) и закрытие всех компонентов
  def on_closing(self):
    if self.camera:
      self.camera.release()
    self.root.quit()
# для четкого разделения кода на импортируемый и исполняемый, создании точки
# входа в приложение
if __name__ == "__main__":
  # Инициализация движка Tkinter
  root = tk.Tk()
  # Создание экземпляра класса
  app = ImageEditApp(root)
  # привязка корректного завершения
  root.protocol("WM_DELETE_WINDOW", app.on_closing)
  # Бесконечный цикл обработки событий
  root.mainloop()