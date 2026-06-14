import 'package:flutter/material.dart';
import '../models/rag_response.dart';
import 'source_badge_text.dart';

class ChatMessage extends StatelessWidget {
  final Map<String, dynamic> message;
  final bool isSelected;
  final VoidCallback? onTap;

  const ChatMessage({
    super.key,
    required this.message,
    required this.isSelected,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final bool isUser = message['sender'] == 'user';
    final List<Citation> citations = List<Citation>.from(
      message['citations'] ?? [],
    );

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          constraints: const BoxConstraints(maxWidth: 620),
          margin: const EdgeInsets.only(bottom: 24),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
          decoration: BoxDecoration(
            color: isUser ? const Color(0xFF2A9D8F) : Colors.transparent,
            borderRadius: isUser
                ? const BorderRadius.only(
                    topLeft: Radius.circular(16),
                    topRight: Radius.circular(16),
                    bottomLeft: Radius.circular(16),
                    bottomRight: Radius.circular(0),
                  )
                : BorderRadius.zero,
            boxShadow: isUser
                ? [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.04),
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ]
                : [],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SourceBadgeText(
                text: message['text'] ?? '',
                baseColor: isUser ? Colors.white : const Color(0xFF2D3748),
              ),

              // Tap hint — only on bot messages that have citations
              if (!isUser && citations.isNotEmpty) ...[
                const SizedBox(height: 10),
                GestureDetector(
                  onTap: onTap,
                  child: Row(
                    children: [
                      Icon(
                        Icons.collections_bookmark_outlined,
                        size: 12,
                        color: const Color(0xFF2A9D8F).withOpacity(0.7),
                      ),
                      const SizedBox(width: 6),
                      const Text(
                        "Tap to view sources",
                        style: TextStyle(
                          fontSize: 11,
                          color: Color(0xFF2A9D8F),
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
