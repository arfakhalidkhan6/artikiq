import 'package:flutter/material.dart';

class QueryInputBar extends StatelessWidget {
  final TextEditingController controller;
  final Function(String) onSubmit;

  const QueryInputBar({
    super.key,
    required this.controller,
    required this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.center,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 850),
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: controller,
                style: const TextStyle(
                  color: Color(0xFF2D3748),
                  fontSize: 14.5,
                ),
                decoration: InputDecoration(
                  hintText: "Ask the SLP clinical knowledge base...",
                  hintStyle: const TextStyle(color: Color(0xFF94A3B8)),
                  filled: true,
                  fillColor: Colors.white,
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 18,
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(30),
                    borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(30),
                    borderSide: const BorderSide(
                      color: Color(0xFF2A9D8F),
                      width: 1.5,
                    ),
                  ),
                ),
                onSubmitted: (value) {
                  if (value.trim().isNotEmpty) onSubmit(value);
                  controller.clear();
                },
              ),
            ),
            const SizedBox(width: 12),
            CircleAvatar(
              radius: 26,
              backgroundColor: const Color(0xFFE9C46A),
              child: IconButton(
                icon: const Icon(
                  Icons.send_rounded,
                  color: Color(0xFF264653),
                  size: 18,
                ),
                onPressed: () {
                  if (controller.text.trim().isNotEmpty) {
                    onSubmit(controller.text);
                    controller.clear();
                  }
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
