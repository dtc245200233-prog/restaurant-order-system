
# Restaurant Order System

Hệ thống quản lý nhà hàng triển khai bằng Docker Compose, sử dụng Flask, PostgreSQL và các công cụ giám sát.

## Công nghệ

- Flask + Gunicorn: ứng dụng web
- PostgreSQL 16: cơ sở dữ liệu
- pgAdmin: quản lý cơ sở dữ liệu
- Nginx: reverse proxy và HTTP security headers
- Prometheus: thu thập metrics
- Grafana: dashboard giám sát
- Loki và Promtail: thu thập, truy vấn log

## Yêu cầu

- Docker Engine
- Docker Compose plugin

## Cài đặt

1. Sao chép repository.
2. Tạo file môi trường:

   ```bash
   cp .env.example .env
   ```

3. Chỉnh `.env` và thay toàn bộ giá trị mẫu bằng thông tin riêng.
4. Khởi chạy:

   ```bash
   docker compose up -d --build
   ```

5. Kiểm tra dịch vụ:

   ```bash
   docker compose ps
   ```

## Địa chỉ truy cập trên máy triển khai

- Ứng dụng qua Nginx: http://localhost:8080
- Ứng dụng trực tiếp: http://localhost:5000
- pgAdmin: http://localhost:5050
- Prometheus: http://localhost:9090
- Prometheus Targets: http://localhost:9090/targets
- Grafana: http://localhost:3000

## Giám sát log

Mở Grafana, chọn Explore và sử dụng nguồn dữ liệu Loki.

Ví dụ truy vấn LogQL:

```logql
{job="docker"}
```

```logql
{job="docker"} |= "error"
```

```logql
{job="docker"} |= "status=200"
```

Kết quả truy vấn phụ thuộc vào log thực tế được thu thập.

## Bảo mật

- Không commit file `.env` hoặc mật khẩu thật lên Git.
- Thay các giá trị mẫu trong `.env.example` trước khi chạy.
- Các cổng pgAdmin, Prometheus và Grafana hiện được giới hạn ở localhost.
- Nginx thiết lập các HTTP security headers.

## Dữ liệu

PostgreSQL sử dụng Docker named volume `postgres_data` để lưu dữ liệu.
