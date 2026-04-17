[cite_start]Dưới đây là bản `README.md` đã được mở rộng và tối ưu hóa chuyên sâu hơn dựa trên báo cáo khoa học của Nhóm 1[cite: 1, 3]. Bản này bổ sung thêm các phần về kiến trúc hệ thống, chi tiết kỹ thuật và định hướng phát triển để tăng tính chuyên nghiệp trên GitHub.

-----

# Online Luxury Car Shop Web Application

### Nền tảng thương mại điện tử xe hơi cao cấp tích hợp thanh toán trực tuyến

[](https://www.python.org/)
[](https://flask.palletsprojects.com/)
[](https://stripe.com/)
[](https://opensource.org/licenses/MIT)

## 📖 1. Giới thiệu dự án

[cite_start]Dự án tập trung vào việc xây dựng một giải pháp Web thương mại điện tử chuyên biệt cho phân khúc xe hơi cao cấp[cite: 14, 23]. [cite_start]Mục tiêu chính là tạo ra một nền tảng đơn giản, đầy đủ chức năng và dễ triển khai, giúp khách hàng có thể trải nghiệm quy trình từ xem sản phẩm đến thanh toán an toàn trong môi trường trực tuyến[cite: 24, 25].

[cite_start]Ứng dụng không chỉ giải quyết bài toán hiển thị sản phẩm mà còn quản lý toàn bộ vòng đời của một đơn hàng thông qua tích hợp API bên thứ ba (Stripe)[cite: 16, 29].

## 🛠 2. Công nghệ & Kiến trúc

### [cite_start]Danh mục công nghệ (Stack) [cite: 38]

  * [cite_start]**Backend:** Python 3.10+ kết hợp Micro-framework Flask[cite: 38].
  * [cite_start]**Database:** SQLite3 – Hệ quản trị cơ sở dữ liệu nhúng, không cần cấu hình server phức tạp[cite: 38, 44].
  * [cite_start]**Authentication:** Flask-Login quản lý phiên làm việc và xác thực người dùng[cite: 38, 45].
  * [cite_start]**Payment Gateway:** Stripe API (Test Mode)[cite: 38, 46].
  * [cite_start]**Frontend:** HTML5, CSS3 thuần (Pure CSS) và Template engine Jinja2[cite: 38, 47].

### [cite_start]Kiến trúc hệ thống (MVC Pattern) [cite: 51]

  * [cite_start]**Model:** Định nghĩa cấu trúc dữ liệu cho User, Car và Order bằng SQL thuần[cite: 51, 59].
  * [cite_start]**View:** Giao diện người dùng được thiết kế hiện đại, hỗ trợ Dark Mode và Responsive[cite: 18, 52].
  * [cite_start]**Controller:** Các Route Flask xử lý logic nghiệp vụ và điều phối request[cite: 53].

## ✨ 3. Tính năng cốt lõi

### [cite_start]Đối với Người dùng [cite: 55, 56]

  * [cite_start]**Khám phá:** Xem danh sách xe dưới dạng card hiện đại với hiệu ứng hover[cite: 126, 151].
  * [cite_start]**Đăng ký/Đăng nhập:** Quản lý tài khoản cá nhân thông qua Flask-Login[cite: 127].
  * [cite_start]**Thanh toán trực tuyến:** Tích hợp quy trình thanh toán an toàn qua Stripe Checkout[cite: 129, 132].
  * [cite_start]**Quản lý cá nhân:** Theo dõi lịch sử đơn hàng, tổng chi tiêu và ngày mua[cite: 131, 169].

### [cite_start]Đối với Quản trị viên (Admin) [cite: 57, 124]

  * [cite_start]**Đặc quyền:** Sở hữu toàn bộ quyền của người dùng cùng khả năng truy cập trang quản trị[cite: 57].
  * [cite_start]**Quản lý kho:** Thêm xe mới trực tiếp qua giao diện Web (Form nhập liệu tên, giá, mô tả, ảnh)[cite: 31, 128].

## [cite_start]📐 4. Thiết kế cơ sở dữ liệu [cite: 58]

[cite_start]Hệ thống sử dụng 3 bảng dữ liệu chính được khởi tạo tự động[cite: 59]:

  * [cite_start]**User:** Lưu trữ ID, Username, Password, Email và quyền Admin[cite: 60, 61, 62, 63, 64].
  * [cite_start]**Car:** Thông tin về tên xe, giá (lưu theo cent để tránh lỗi số thập phân), mô tả và URL hình ảnh[cite: 65, 66, 67, 68, 69, 70].
  * [cite_start]**Order:** Ghi lại ID người mua, ID xe, Stripe Payment ID và thời gian mua[cite: 71, 72, 73, 75, 76, 77].

## [cite_start]🎨 5. Giao diện (UI/UX Highlights) [cite: 148]

  * [cite_start]**Modern Design:** Sử dụng phong cách Glassmorphism cho thanh điều hướng[cite: 150].
  * [cite_start]**Dynamic Visuals:** Hero section với hiệu ứng Gradient text nổi bật[cite: 166].
  * [cite_start]**Adaptive Theme:** Tự động chuyển đổi Dark Mode dựa trên cấu hình hệ thống của người dùng (`prefers-color-scheme`)[cite: 153, 177].
  * [cite_start]**Fully Responsive:** Tối ưu hóa hiển thị trên mọi kích thước màn hình từ Desktop đến Mobile thông qua Media Queries[cite: 152, 176].

## 🚀 6. Hướng dẫn triển khai

### Yêu cầu hệ thống

  * [cite_start]Python 3.10+ [cite: 88]
  * [cite_start]Stripe Account (để lấy API Key) [cite: 182]

### [cite_start]Các bước cài đặt [cite: 90]

1.  **Clone dự án & Khởi tạo môi trường:**
    ```bash
    mkdir car_shop
    cd car_shop
    python -m venv venv
    source venv/bin/activate  # Win: venv\Scripts\activate
    ```
2.  [cite_start]**Cài đặt thư viện:** [cite: 96]
    ```bash
    pip install flask flask-login stripe
    ```
3.  **Cấu hình API:**
    [cite_start]Thay thế các placeholder bằng Secret Key từ Dashboard Stripe của bạn trong file `app.py`[cite: 182].
4.  [cite_start]**Khởi chạy:** [cite: 115]
    ```bash
    python app.py
    ```
    [cite_start]Truy cập tại địa chỉ: `http://127.0.0.1:5000`[cite: 145].

## 🚧 7. Thách thức & Hướng phát triển

### [cite_start]Thách thức đã vượt qua [cite: 179]

  * [cite_start]**Khắc phục lỗi thanh toán:** Đồng bộ hóa URL thành công giữa Flask và Stripe API[cite: 181, 183].
  * [cite_start]**Đồng bộ hóa UI:** Viết lại toàn bộ Template để khớp với hệ thống Class CSS mới[cite: 187].

### [cite_start]Định hướng nâng cấp [cite: 192]

  * [cite_start]**Security:** Triển khai Hash mật khẩu thay vì lưu dạng văn bản thuần[cite: 193].
  * [cite_start]**Performance:** Thêm tính năng phân trang (Pagination) cho danh sách xe[cite: 194].
  * [cite_start]**User Experience:** Tích hợp gửi Email xác nhận sau khi thanh toán thành công[cite: 197].

## [cite_start] 8. Đội ngũ thực hiện - Nhóm 1 [cite: 3]
  * [cite_start]**Hồ Hoàng Trí** [cite: 6]
  * [cite_start]**Võ Minh Trí** [cite: 7]

-----

*Dự án được thực hiện cho môn học Tin học. [cite_start]Ngày hoàn thành: 12/2.* [cite: 10, 11]
