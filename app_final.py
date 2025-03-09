import customtkinter # pip / pip3 install customtkinter
import os 
from PIL import Image, ImageDraw, ImageOps # pip install pillow
import json
from phone_tree import AVLTree

print("Thư mục làm việc hiện tại:", os.getcwd())

#TODO 1: Tạo Product Frame
class Product(customtkinter.CTkFrame):
    # Tạo border-radius (độ cong của viền) cho ảnh
    def add_border_radius(self, image_path, radius):
        image = Image.open(image_path)
        mask = Image.new('L', image.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)
        result = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
        result.putalpha(mask)
        return result
    
    def buy_product(self):
        print(f"Mua sản phẩm {self.product['name']} này giá: ${self.product['price']}")
    
    def __init__(self, master, product):
        super().__init__(master=master, fg_color="black", corner_radius=10)
        self.product = product
        self.cart = self.winfo_toplevel().cart

        # Chia product_frame ra thành 2 phần trên dưới
        top_frame = customtkinter.CTkFrame(master=self, fg_color="black", corner_radius=10)
        top_frame.pack(expand=True, fill="both", pady=(10, 0)) # padding_top = 10, padding_bottom = 0

        bottom_frame = customtkinter.CTkFrame(master=self, fg_color="black", corner_radius=10)
        bottom_frame.pack(expand=True, fill="both", pady=(0, 10))

        #? Tạo khung chứa hình ảnh 
        image_path = os.path.join("img", product["image"])
        custom_image = self.add_border_radius(image_path=image_path, radius=20)
        # image = customtkinter.CTkImage(light_image=Image.open(image_path), dark_image=Image.open(image_path), size=(180, 180))
        image = customtkinter.CTkImage(light_image=custom_image, dark_image=custom_image, size=(180, 180))

        # 1. Hình ảnh (image)
        image_frame = customtkinter.CTkLabel(master=top_frame, image=image, text="")
        image_frame.pack(padx=15)

        #? Tạo khung chứa thông tin sản phẩm
        info_frame = customtkinter.CTkFrame(master=bottom_frame, fg_color="black")
        info_frame.pack(pady=10, padx=0)

        # 2. Tên sản phẩm (name)
        name = customtkinter.CTkLabel(master=info_frame, font=customtkinter.CTkFont("Arial", 18, "bold"), text_color="orange", text=product["name"]) # màu sắc: tên màu, hex, rgb
        name.pack()

        # 3. Loại sản phẩm (category)
        category_frame = customtkinter.CTkFrame(master=info_frame, fg_color="pink", corner_radius=15)
        category_frame.pack()

        category = customtkinter.CTkLabel(master=category_frame, font=customtkinter.CTkFont("Arial", 11, "bold"), text_color="black", text=product["category"])
        category.pack(anchor="center", padx=10)

        # 4. Mô tả (description)
        description = customtkinter.CTkLabel(master=info_frame, text_color="white", text=product["description"])
        description.pack(pady=(5, 0))

        # 5. Giá sản phẩm (price)
        price = customtkinter.CTkLabel(master=info_frame, font=customtkinter.CTkFont("Helvetica", 15, "bold"), text_color="yellow", text=f"$ {product["price"]}")
        price.pack()

        # Nút mua sản phẩm
        button = customtkinter.CTkButton(info_frame, fg_color="darkblue", text="Mua", command=self.buy_product)
        button.pack(pady=(10, 0))

        # Nút thêm vào giỏ hàng
        add_cart_button = customtkinter.CTkButton(self, text="Thêm vào giỏ", command=self.add_to_cart, fg_color="red")
        add_cart_button.pack(pady=(0, 10))
        add_cart_button.bind("<Enter>", lambda e: add_cart_button.configure(fg_color="darkred"))
        add_cart_button.bind("<Leave>", lambda e: add_cart_button.configure(fg_color="red"))
    
    def buy_product(self):
        print(f"Mua sản phẩm {self.product['name']} này giá: ${self.product['price']}")

    def add_to_cart(self):
        self.winfo_toplevel().cart.append(self.product)
        print(f"Đã thêm {self.product['name']} vào giỏ hàng!")
        self.winfo_toplevel().header_frame.update_cart_count()  # Cập nhật số lượng hiển thị

        
#TODO 2: Tạo ScrollView
class ScrollView(customtkinter.CTkScrollableFrame):
    def __init__(self, master, product_list):
        super().__init__(master=master)

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for i in range(len(product_list)):
            product_frame = Product(master=self, product=product_list[i])
            product_frame.grid(column = i % 4, row = i // 4, sticky="nesw", padx=(0, 10), pady=(0, 10)) 

#TODO 3: Tạo Header
class Header(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master=master, fg_color="black", corner_radius=0)

        self.master = master

        self.entry_min = customtkinter.CTkEntry(master=self, placeholder_text="Nhập giá thấp nhất")
        self.entry_min.pack(side="left", padx=(10,0))

        self.entry_max = customtkinter.CTkEntry(master=self, placeholder_text="Nhập giá cao nhất")
        self.entry_max.pack(side="left", padx=(10,0))

        search_button = customtkinter.CTkButton(self, fg_color="green", text="Lọc", width=150, command=master.filter)
        search_button.pack(side="left", padx=(25,0))

        # Nút giỏ hàng (ban đầu hiển thị "Giỏ hàng (0)")
        self.cart_button = customtkinter.CTkButton(self, text="Giỏ hàng (0)", command=self.master.show_cart)
        self.cart_button.pack(side="left", padx=(25, 0))

    def update_cart_count(self):
        """ Cập nhật số lượng sản phẩm trong giỏ hàng """
        count = len(self.master.cart)
        self.cart_button.configure(text=f"Giỏ hàng ({count})")



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.cart_window = None
        self.cart = []
        
        #? Cấu hình màu sắc mặc định của window
        customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"
        customtkinter.set_appearance_mode("light") # system (default), light, dark

        #? Cấu hình ứng dụng: tiêu đề, kích thước window, khả năng thay đổi tỉ lệ màn hình
        self.title("Phone Shop")
        self.geometry("1100x800") #1024x720
        self.resizable(True, False) # 1. width, 2. height
        
        self.products = self.get_data()
        
        self.avl_data = AVLTree()
        
        # Thêm sản phẩm vào cây AVL
        for product in self.products:
            self.avl_data.insert(product)
        
        #? Khởi tạo Header
        self.header_frame = Header(master=self)
        self.header_frame.place(relx=0, rely=0, relwidth=1, relheight=0.1)
        
        #? Khởi tạo ScrollView
        self.scroll_frame = ScrollView(master=self, product_list=self.products)
        self.scroll_frame.place(relx=0, rely=0.1, relwidth=1, relheight=0.9) 
        
    def get_data(self):
        file_path = os.path.join(os.path.dirname(__file__), "data", "data.json")

        print(f"Đường dẫn tuyệt đối: {file_path}")
        print(f"Tệp tồn tại không? {os.path.exists(file_path)}")

        if not os.path.exists(file_path):
            print("LỖI: Không tìm thấy file data.json")
            return []

        with open(file_path, "r", encoding="utf-8") as file:
            products = json.load(file)
    
        return products
    
    def filter(self):
        try:
            min_price = int(self.header_frame.entry_min.get())
            max_price = int(self.header_frame.entry_max.get())

            if min_price > max_price:
                print("Giá tối thiểu không được lớn hơn giá tối đa!")
                return
        
            data_search = self.avl_data.find_phones(self.avl_data.root, min_price=min_price, max_price=max_price)
        
            print(json.dumps(data_search, indent=4))

            # Xóa ScrollView cũ trước khi tạo mới
            self.scroll_frame.destroy()

            if not data_search:
            # Nếu không có sản phẩm nào phù hợp, hiển thị thông báo
                self.scroll_frame = customtkinter.CTkFrame(master=self)
                self.scroll_frame.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)

                label = customtkinter.CTkLabel(self.scroll_frame, text="Không tìm thấy sản phẩm nào!", font=("Arial", 32, "bold"), text_color="red")
                label.pack(expand=True)
            else:
            # Nếu có sản phẩm, hiển thị danh sách mới
                self.scroll_frame = ScrollView(master=self, product_list=data_search)
                self.scroll_frame.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)

        except ValueError:
            print("Vui lòng nhập số hợp lệ cho giá!")

    def show_cart(self):
        if self.cart_window and self.cart_window.winfo_exists():
            self.cart_window.destroy()

        self.cart_window = customtkinter.CTkToplevel(self)
        self.cart_window.title("Giỏ hàng")
        self.cart_window.geometry("400x400+200+150")  
        self.cart_window.grab_set()

        if not self.cart:
            label = customtkinter.CTkLabel(self.cart_window, text="Giỏ hàng trống!", font=("Arial", 16))
            label.pack(pady=20)
        else:
            total_price = sum(product["price"] for product in self.cart)

            # **Tạo Scrollable Frame bên trong cart_window**
            scroll_frame = customtkinter.CTkScrollableFrame(self.cart_window, width=380, height=250)
            scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # **Đảm bảo các sản phẩm được thêm vào scroll_frame**
            for product in self.cart:
                frame = customtkinter.CTkFrame(scroll_frame)  # 🔥 Thêm vào scroll_frame, không phải cart_window
                frame.pack(fill="x", padx=10, pady=5)

                # **Hiển thị hình ảnh**
                img_path = os.path.join("img", product["image"])
                img = Image.open(img_path).resize((50, 50))
                img = customtkinter.CTkImage(light_image=img, dark_image=img, size=(50, 50))
                img_label = customtkinter.CTkLabel(frame, image=img, text="")
                img_label.pack(side="left")

                # **Tên & giá sản phẩm**
                text_label = customtkinter.CTkLabel(frame, text=f"{product['name']} - ${product['price']}")
                text_label.pack(side="left", padx=10)

                # **Nút xóa**
                remove_button = customtkinter.CTkButton(frame, text="Xóa", fg_color="red",
                                                    command=lambda p=product: self.remove_from_cart(p))
                remove_button.pack(side="right")

            # **Tổng tiền**
            total_label = customtkinter.CTkLabel(self.cart_window, text=f"Tổng tiền: ${total_price}",
                                             font=("Arial", 14, "bold"), text_color="green")
            total_label.pack(pady=10)

        # **Nút đóng**
        close_button = customtkinter.CTkButton(self.cart_window, text="Đóng", fg_color="gray", command=self.cart_window.destroy)
        close_button.pack(pady=10)

    def remove_from_cart(self, product):
        self.cart.remove(product)
        self.header_frame.update_cart_count()  # Cập nhật số lượng giỏ hàng
        self.show_cart()  # Cập nhật lại popup thay vì mở popup mới


app = App()

app.mainloop()
