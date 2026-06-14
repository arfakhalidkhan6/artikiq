import 'package:flutter/material.dart';

class Header extends StatelessWidget {
  final VoidCallback onMenuTap;
  final VoidCallback onLogoutTap;

  const Header({super.key, required this.onMenuTap, required this.onLogoutTap});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      // White header bar with a subtle bottom border
      decoration: const BoxDecoration(color: Colors.white),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Left: open session drawer
          IconButton(
            icon: const Icon(Icons.menu, color: Color(0xFF2D3748)),
            onPressed: onMenuTap,
          ),

          // Center: app name + connection status
          const Row(
            children: [
              Icon(Icons.verified_outlined, color: Color(0xFF2A9D8F), size: 16),
              SizedBox(width: 8),
              Text(
                "ArtikIQ",
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF2D3748),
                ),
              ),
              SizedBox(width: 6),
              Text(
                "Research Engine",
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w400,
                  color: Color(0xFF64748B),
                ),
              ),
            ],
          ),

          // Right: logout button
          IconButton(
            icon: const Icon(
              Icons.power_settings_new,
              color: Color(0xFFE76F51),
            ),
            onPressed: onLogoutTap,
          ),
        ],
      ),
    );
  }
}
