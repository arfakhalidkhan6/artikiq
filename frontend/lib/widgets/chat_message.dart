import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/rag_response.dart';
import 'source_badge_text.dart';

class ChatMessage extends StatefulWidget {
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
  State<ChatMessage> createState() => _ChatMessageState();
}

class _ChatMessageState extends State<ChatMessage> {
  bool? _feedbackGiven;
  bool _isSubmittingFeedback = false;

  void _copyToClipboard(BuildContext context, String text) {
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text("Copied to clipboard"),
        duration: Duration(seconds: 1),
        backgroundColor: Color(0xFF2A9D8F),
      ),
    );
  }

  Future<void> _submitFeedback(bool isPositive) async {
    final String? traceId = widget.message['trace_id'];

    if (traceId == null ||
        _isSubmittingFeedback ||
        _feedbackGiven == isPositive) {
      return;
    }

    setState(() {
      _isSubmittingFeedback = true;
    });

    try {
      final response = await http.post(
        Uri.parse('http://127.0.0.1:8000/api/feedback'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'trace_id': traceId, 'is_positive': isPositive}),
      );

      if (response.statusCode == 200) {
        setState(() {
          _feedbackGiven = isPositive;
        });
      }
    } catch (e) {
      // Silently fail — feedback is non-critical
    } finally {
      setState(() {
        _isSubmittingFeedback = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final bool isUser = widget.message['sender'] == 'user';
    final String text = widget.message['text'] ?? '';
    final List<Citation> citations = List<Citation>.from(
      widget.message['citations'] ?? [],
    );

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: GestureDetector(
        onTap: widget.onTap,
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
                text: text,
                baseColor: isUser ? Colors.white : const Color(0xFF2D3748),
              ),

              // Only show the action row once there's real text to act on —
              // prevents Copy/Sources/Thumbs from appearing on an empty
              // streaming placeholder before any words have arrived.
              if (!isUser && text.isNotEmpty) ...[
                const SizedBox(height: 10),
                Row(
                  children: [
                    GestureDetector(
                      onTap: () => _copyToClipboard(context, text),
                      child: Row(
                        children: [
                          Icon(
                            Icons.copy_outlined,
                            size: 13,
                            color: const Color(0xFF64748B).withOpacity(0.8),
                          ),
                          const SizedBox(width: 5),
                          const Text(
                            "Copy",
                            style: TextStyle(
                              fontSize: 11,
                              color: Color(0xFF64748B),
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),

                    if (citations.isNotEmpty) ...[
                      const SizedBox(width: 18),
                      GestureDetector(
                        onTap: widget.onTap,
                        child: Row(
                          children: [
                            Icon(
                              Icons.collections_bookmark_outlined,
                              size: 13,
                              color: const Color(0xFF2A9D8F).withOpacity(0.7),
                            ),
                            const SizedBox(width: 5),
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

                    const SizedBox(width: 18),

                    GestureDetector(
                      onTap: () => _submitFeedback(true),
                      child: Icon(
                        _feedbackGiven == true
                            ? Icons.thumb_up
                            : Icons.thumb_up_outlined,
                        size: 14,
                        color: _feedbackGiven == true
                            ? const Color(0xFF2A9D8F)
                            : const Color(0xFF64748B).withOpacity(0.8),
                      ),
                    ),

                    const SizedBox(width: 10),

                    GestureDetector(
                      onTap: () => _submitFeedback(false),
                      child: Icon(
                        _feedbackGiven == false
                            ? Icons.thumb_down
                            : Icons.thumb_down_outlined,
                        size: 14,
                        color: _feedbackGiven == false
                            ? const Color(0xFFE76F51)
                            : const Color(0xFF64748B).withOpacity(0.8),
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
