import tkinter
import customtkinter
from PIL import ImageTk, Image

import requests
from bs4 import BeautifulSoup

import sqlite3

# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("Light")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("1000x600")
app.title("Bookstore")

find_book_list = []
library_list = []


def button_callback():
    print("Button click", entry_1.get())
    book = entry_1.get()
    # print("get_book_info() = ", get_book_info())
    # label_book.configure(text = get_book_info(book))
    liste = []
    liste = get_book_info(book)

    if len(liste) > 0:
        optionmenu_1.set("Kitap Bulunmuştur. Tıklayınız.")
    else:
        optionmenu_1.set("Kitap bulunamadı.")

    optionmenu_1.configure(values=liste)


def save_image(link):
    print("link =", link)
    try:
        r = requests.get(link).content
        try:
            # possibility of decode
            r = str(r, 'utf-8')
        except UnicodeDecodeError:
            # After checking above condition, Image Download start
            with open("image.jpg", "wb+") as f:
                f.write(r)
    except:
        pass

    book_img = ImageTk.PhotoImage(Image.open("image.jpg").resize((300, 500)))

    book_img_button.configure(image=book_img)
    book_img_button.image = book_img


def get_book_info(book):
    url = "https://www.bkmkitap.com/kitap/cok-satan-kitaplar"

    response = requests.get(url)

    html_icerigi = response.content

    soup = BeautifulSoup(html_icerigi, "html.parser")

    fiyatlar = soup.find_all("div", {"class": "col col-12 currentPrice"})
    isimler = soup.find_all(
        "a", {"class": "fl col-12 text-description detailLink"})
    yazarlar = soup.find_all("a", {"class": "fl col-12 text-title"})
    yayınlar = soup.find_all("a", {"class": "col col-12 text-title mt"})
    resimler = soup.find_all("img", {"class": "stImage"})

    for i in resimler:
        print(i["data-src"])

    liste = list()

    for i in range(len(isimler)):
        isimler[i] = (isimler[i].text).strip("\n").strip()
        yazarlar[i] = (yazarlar[i].text).strip("\n").strip()
        yayınlar[i] = (yayınlar[i].text).strip("\n").strip()
        fiyatlar[i] = (fiyatlar[i].text).strip("\n")
        resimler[i] = resimler[i]["data-src"]

        liste.append([isimler[i], yazarlar[i], yayınlar[i],
                     fiyatlar[i], resimler[i]])
    # for döngüsü bu satırda bitti  yani bu satırdan sonra satır başı yapılmalıdır
    print(liste)

    find_book_list.clear()
    library_list.clear()

    for book_info in liste:
        if book.lower() in book_info[0].lower():
            book_dict = {}
            name = book_info[0]
            book_dict["isim"] = book_info[0]
            book_dict["yazar"] = book_info[1]
            book_dict["yayın"] = book_info[2]
            book_dict["fiyat"] = book_info[3]
            book_dict["resim"] = book_info[4]

            find_book_list.append(name)
            library_list.append(book_dict)

    print("library_list = ", library_list)

    with sqlite3.connect('library.db') as vt:
        im = vt.cursor()

        im.execute("""CREATE TABLE IF NOT EXISTS bookstore
            (id INTEGER PRIMARY KEY, isimler, yazarlar, yayınlar, fiyatlar, resimler)""")
        vt.commit()

        # Yeni bir arama için tüm kitapları siliyoruz

        im.execute("DELETE FROM bookstore")
        vt.commit()

        # Yeni arama ile doldurulan library_list insert işlemi yapılıyor

        for book_dict in library_list:
            im.execute("""INSERT INTO bookstore VALUES
                (NULL, ?, ?, ?, ?, ?)""", (book_dict["isim"], book_dict["yazar"], book_dict["yayın"], book_dict["fiyat"], book_dict["resim"]))
        vt.commit()

        obj = im.execute("""SELECT * FROM bookstore""")

        print(list(obj))

    return find_book_list


img = Image.open("bookstore.jpeg")
test = ImageTk.PhotoImage(img)
label_img = customtkinter.CTkLabel(master=app, image=test)
label_img.grid(row=0, column=0)

entry_1 = customtkinter.CTkEntry(
    master=label_img, placeholder_text="Kitap ismi giriniz")
entry_1.place(x=200, y=100)


button_1 = customtkinter.CTkButton(
    master=label_img, command=button_callback, text="ARA", bg_color="blue")
button_1.place(x=200, y=200)

optionmenu_1 = customtkinter.CTkOptionMenu(label_img, values=find_book_list)
optionmenu_1.place(x=200, y=300)
optionmenu_1.set("Henüz Kitap Aranmadı...")


def get_book_img():
    name = optionmenu_1.get()

    for book_dict in library_list:
        if book_dict["isim"] == name:
            link = book_dict["resim"]
            save_image(link)
            # son 3 karakteri alma \nTL
            label_price.configure(text=book_dict["fiyat"][:-3] + " TL")
            return


get_button = customtkinter.CTkButton(
    master=label_img, text="Kitap Bilgisi Getir", bg_color="green", command=get_book_img)
get_button.place(x=200, y=400)


def make_fav():
    if star_button.img == "empty":
        star_button.configure(image=star_full)
        star_button.img = "full"
    else:
        star_button.configure(image=star_empty)
        star_button.img = "empty"

    print(star_button.image)


star_empty = ImageTk.PhotoImage(Image.open("star_bos.png").resize((20, 20)))
star_full = ImageTk.PhotoImage(Image.open("star_full.png").resize((20, 20)))

star_button = customtkinter.CTkButton(
    master=label_img, text="", bg_color="blue", image=star_empty, command=make_fav)
star_button.place(x=140, y=300, width=25, height=25)
star_button.img = "empty"

first_book_img = ImageTk.PhotoImage(Image.open("image.jpg").resize((300, 600)))
book_img_button = customtkinter.CTkLabel(
    master=label_img, text="", bg_color="blue", image=first_book_img)
book_img_button.place(x=500, y=50, width=300, height=500)
book_img_button.turn = 1


label_price = customtkinter.CTkLabel(
    master=app, text="PRICE", bg_color="light blue")
label_price.place(x=500, y=560, width=300, height=20)

app.mainloop()
