import 'dart:io';
import 'package:dio/dio.dart';
import '../core/constants.dart';

class ApiService {
  final Dio _dio = Dio();

  // 1. Gửi ảnh tìm kiếm (Visual Search)
  Future<List<dynamic>> searchByImage(File imageFile) async {
    try {
      String fileName = imageFile.path.split('/').last;
      
      // Tạo Form Data để gửi file
      FormData formData = FormData.fromMap({
        "file": await MultipartFile.fromFile(
          imageFile.path,
          filename: fileName,
        ),
      });

      // Gọi API với timeout
      Response response = await _dio.post(
        ApiConstants.searchEndpoint,
        data: formData,
        options: Options(
          sendTimeout: const Duration(seconds: 10),
          receiveTimeout: const Duration(seconds: 10),
        )
      );

      // Backend trả về JSON: { "results": [...] }
      if (response.data != null && response.data['results'] != null) {
        return response.data['results'];
      }
      return [];
      
    } catch (e) {
      print("Error uploading image: $e");
      // Ném lỗi ra để UI xử lý hiển thị
      throw Exception("Không thể kết nối tới Server AI. Vui lòng kiểm tra IP.");
    }
  }

  // 2. Lấy lời khuyên Stylist (RAG + LLM)
  Future<String> getStylistAdvice(String productId, String userQuery) async {
    try {
      Response response = await _dio.post(
        ApiConstants.adviceEndpoint,
        data: {
          "product_id": productId,
          "user_question": userQuery
        }
      );
      
      if (response.data != null && response.data['advice'] != null) {
        return response.data['advice'];
      }
      return "Không nhận được phản hồi từ AI.";
      
    } catch (e) {
      print("Stylist Error: $e");
      return "Xin lỗi, stylist đang bận hoặc mất kết nối. Vui lòng thử lại sau.";
    }
  }
}