import 'dart:io';
import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../services/api_service.dart';

class ResultScreen extends StatefulWidget {
  final File imageFile;
  const ResultScreen({super.key, required this.imageFile});

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  final ApiService _apiService = ApiService();
  bool _isLoading = true;
  List<dynamic> _products = [];
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _doSearch();
  }

  // Logic gọi API Search
  void _doSearch() async {
    try {
      final results = await _apiService.searchByImage(widget.imageFile);
      if (mounted) {
        setState(() {
          _products = results;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  // Logic hiển thị Stylist Advice (Dạng BottomSheet)
  void _showStylistAdvice(String productId, String productName) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => StylistAdviceSheet(productId: productId, productName: productName),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Kết quả AI")),
      body: Column(
        children: [
          // 1. Ảnh user upload (Thumbnail nhỏ)
          Container(
            height: 150,
            width: double.infinity,
            color: Colors.grey[100],
            child: Center(
              child: Image.file(widget.imageFile, fit: BoxFit.contain),
            ),
          ),
          const Divider(height: 1),
          
          // 2. Danh sách kết quả
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _errorMessage != null
                    ? Center(child: Padding(
                        padding: const EdgeInsets.all(20.0),
                        child: Text(_errorMessage!, textAlign: TextAlign.center, style: const TextStyle(color: Colors.red)),
                      ))
                    : _products.isEmpty
                        ? const Center(child: Text("Không tìm thấy sản phẩm nào phù hợp."))
                        : GridView.builder(
                            padding: const EdgeInsets.all(10),
                            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                              crossAxisCount: 2,
                              childAspectRatio: 0.75, // Tỷ lệ khung hình thẻ sản phẩm
                              crossAxisSpacing: 10,
                              mainAxisSpacing: 10,
                            ),
                            itemCount: _products.length,
                            itemBuilder: (context, index) {
                              final product = _products[index];
                              final metadata = product['metadata'] ?? {};
                              // URL ảnh từ Backend trả về (đã xử lý ở Phase 4)
                              final imageUrl = product['image_url'] ?? ""; 

                              return GestureDetector(
                                onTap: () => _showStylistAdvice(product['id'], metadata['name'] ?? "Sản phẩm"),
                                child: Card(
                                  elevation: 2,
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                  clipBehavior: Clip.antiAlias,
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      // Ảnh sản phẩm
                                      Expanded(
                                        child: imageUrl.isNotEmpty
                                            ? CachedNetworkImage(
                                                imageUrl: imageUrl, 
                                                fit: BoxFit.cover,
                                                width: double.infinity,
                                                placeholder: (context, url) => const Center(child: CircularProgressIndicator(strokeWidth: 2)),
                                                errorWidget: (context, url, error) => Container(
                                                  color: Colors.grey[200],
                                                  child: const Icon(Icons.broken_image, color: Colors.grey),
                                                ),
                                              )
                                            : Container(
                                                color: Colors.grey[200],
                                                child: const Center(child: Icon(Icons.image_not_supported)),
                                              ),
                                      ),
                                      // Thông tin sản phẩm
                                      Padding(
                                        padding: const EdgeInsets.all(8.0),
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              metadata['name'] ?? "Sản phẩm", 
                                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14), 
                                              maxLines: 1, 
                                              overflow: TextOverflow.ellipsis
                                            ),
                                            const SizedBox(height: 4),
                                            Text(
                                              "\$${metadata['price'] ?? 0}", 
                                              style: const TextStyle(color: Colors.green, fontWeight: FontWeight.w600)
                                            ),
                                            const SizedBox(height: 4),
                                            Row(
                                              children: [
                                                const Icon(Icons.auto_awesome, size: 12, color: Colors.purple),
                                                const SizedBox(width: 4),
                                                Text(
                                                  "Hỏi Stylist", 
                                                  style: TextStyle(fontSize: 10, color: Colors.purple.shade700)
                                                ),
                                              ],
                                            )
                                          ],
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              );
                            },
                          ),
          ),
        ],
      ),
    );
  }
}

// Widget con: Stylist Bottom Sheet
class StylistAdviceSheet extends StatefulWidget {
  final String productId;
  final String productName;
  const StylistAdviceSheet({super.key, required this.productId, required this.productName});

  @override
  State<StylistAdviceSheet> createState() => _StylistAdviceSheetState();
}

class _StylistAdviceSheetState extends State<StylistAdviceSheet> {
  final ApiService _apiService = ApiService();
  String _advice = "";
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    // Tự động hỏi AI câu mặc định khi mở modal
    _getAdvice("Tôi muốn mặc món này đi chơi, phối thế nào cho đẹp?");
  }

  void _getAdvice(String query) async {
    final advice = await _apiService.getStylistAdvice(widget.productId, query);
    if (mounted) {
      setState(() {
        _advice = advice;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      height: MediaQuery.of(context).size.height * 0.6, // Chiều cao 60% màn hình
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const CircleAvatar(
                backgroundColor: Colors.purple,
                child: Icon(Icons.face, color: Colors.white),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text("AI Stylist", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.purple)),
                    Text("Tư vấn cho: ${widget.productName}", style: const TextStyle(fontSize: 12, color: Colors.grey)),
                  ],
                ),
              ),
              IconButton(onPressed: () => Navigator.pop(context), icon: const Icon(Icons.close))
            ],
          ),
          const Divider(),
          const SizedBox(height: 10),
          Expanded(
            child: _isLoading
                ? const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        CircularProgressIndicator(),
                        SizedBox(height: 10),
                        Text("Đang suy nghĩ... ✨", style: TextStyle(color: Colors.grey)),
                      ],
                    ),
                  )
                : SingleChildScrollView(
                    child: Text(
                      _advice, 
                      style: const TextStyle(fontSize: 16, height: 1.5, color: Colors.black87),
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}