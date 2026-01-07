import 'dart:io';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../core/app_theme.dart';
import 'result_screen.dart';

class HomeScreen extends StatelessWidget {
  final ImagePicker _picker = ImagePicker();

  HomeScreen({super.key});

  Future<void> _pickImage(BuildContext context, ImageSource source) async {
    try {
      final XFile? image = await _picker.pickImage(source: source);
      if (image != null) {
        if (context.mounted) {
          // Add a small delay for touch feedback interaction before navigating
          await Future.delayed(const Duration(milliseconds: 200));
          Navigator.push(
            context,
            PageRouteBuilder(
              pageBuilder: (_, __, ___) => ResultScreen(imageFile: File(image.path)),
              transitionsBuilder: (_, animation, __, child) {
                return FadeTransition(opacity: animation, child: child);
              },
            ),
          );
        }
      }
    } catch (e) {
      debugPrint("Error picking image: $e");
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Error: ${e.toString()}"),
            backgroundColor: AppTheme.errorColor,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // 1. Dynamic Background
          _buildBackground(),

          // 2. Main Content
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                   const Spacer(flex: 2),
                  
                  // Title & Description
                  Column(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(24),
                        decoration: BoxDecoration(
                          color: AppTheme.primaryColor.withOpacity(0.15),
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: AppTheme.primaryColor.withOpacity(0.5),
                            width: 2,
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: AppTheme.primaryColor.withOpacity(0.3),
                              blurRadius: 30,
                              spreadRadius: 10,
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.shopping_bag_outlined,
                          size: 64,
                          color: AppTheme.secondaryColor,
                        ),
                      )
                      .animate(onPlay: (controller) => controller.repeat(reverse: true))
                      .scale(begin: const Offset(0.95, 0.95), end: const Offset(1.05, 1.05), duration: 2000.ms, curve: Curves.easeInOut),
                      
                      const SizedBox(height: 32),
                      
                      const Text(
                        "SHOPPING\nBUDDY AI",
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 40,
                          fontWeight: FontWeight.w900,
                          height: 1.0,
                          letterSpacing: 2,
                        ),
                      ).animate().fadeIn(duration: 800.ms).slideY(begin: 0.3, end: 0),
                      
                      const SizedBox(height: 16),
                      
                      Text(
                        "Discover products, check prices,\nand find the best deals around you.",
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          color: Colors.white70,
                          height: 1.5,
                        ),
                      ).animate().fadeIn(delay: 300.ms, duration: 800.ms),
                    ],
                  ),

                  const Spacer(flex: 3),

                  // Action Buttons
                  Column(
                    children: [
                      _buildLargeButton(
                        context,
                        label: "Scan Product",
                        icon: Icons.camera_alt_rounded,
                        color: AppTheme.primaryColor,
                        onTap: () => _pickImage(context, ImageSource.camera),
                        isPrimary: true,
                      ).animate().fadeIn(delay: 600.ms).slideY(begin: 0.5, end: 0),
                      
                      const SizedBox(height: 16),
                      
                      _buildLargeButton(
                        context,
                        label: "Upload from Gallery",
                        icon: Icons.photo_library_rounded,
                        color: AppTheme.surfaceColor,
                        onTap: () => _pickImage(context, ImageSource.gallery),
                        isPrimary: false,
                      ).animate().fadeIn(delay: 800.ms).slideY(begin: 0.5, end: 0),
                    ],
                  ),

                  const Spacer(flex: 1),
                  
                  const Text(
                    "Powered by AI Vision & Deep Learning",
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.white30,
                      fontSize: 12,
                    ),
                  ).animate().fadeIn(delay: 1500.ms),
                  const SizedBox(height: 16),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBackground() {
    return Positioned.fill(
      child: Stack(
        children: [
          Container(
            color: AppTheme.backgroundColor,
          ),
          Positioned(
            top: -100,
            left: -100,
            child: Container(
              width: 400,
              height: 400,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: AppTheme.primaryColor.withOpacity(0.2),
              ),
            ).animate(onPlay: (controller) => controller.repeat()).rotate(duration: 10.seconds),
          ),
          Positioned(
            bottom: -100,
            right: -100,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: AppTheme.secondaryColor.withOpacity(0.15),
              ),
            ).animate(onPlay: (controller) => controller.repeat(reverse: true)).scale(duration: 5.seconds, begin: const Offset(0.8, 0.8), end: const Offset(1.2, 1.2)),
          ),
          BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 80, sigmaY: 80),
            child: Container(color: Colors.transparent),
          ),
        ],
      ),
    );
  }

  Widget _buildLargeButton(
    BuildContext context, {
    required String label,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
    bool isPrimary = true,
  }) {
    return SizedBox(
      width: double.infinity,
      height: 64,
      child: isPrimary 
        ? ElevatedButton(
            onPressed: onTap,
            style: ElevatedButton.styleFrom(
              backgroundColor: color,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
              elevation: 8,
              shadowColor: color.withOpacity(0.5),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(icon, size: 26),
                const SizedBox(width: 12),
                Text(label, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              ],
            ),
          )
        : OutlinedButton(
            onPressed: onTap,
            style: OutlinedButton.styleFrom(
              side: const BorderSide(color: Colors.white24, width: 1.5),
              backgroundColor: Colors.white.withOpacity(0.05),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(icon, size: 26, color: Colors.white70),
                const SizedBox(width: 12),
                Text(label, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: Colors.white)),
              ],
            ),
          ),
    );
  }
}