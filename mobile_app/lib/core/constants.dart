class ApiConstants {
  // --- CẤU HÌNH ĐỊA CHỈ IP ---
  // 1. Nếu chạy trên Android Emulator: dùng '10.0.2.2'
  // 2. Nếu chạy trên điện thoại thật (chung Wifi): dùng IP LAN của máy tính (vd: '192.168.1.x')
  // 3. Nếu chạy trên iOS Simulator: dùng '127.0.0.1' hoặc localhost
  
  static const String baseUrl = "http://10.0.2.2:8000"; 
  // static const String baseUrl = "http://192.168.1.15:8000"; 

  static const String searchEndpoint = "$baseUrl/api/v1/search/visual";
  static const String adviceEndpoint = "$baseUrl/api/v1/stylist/advice";
}