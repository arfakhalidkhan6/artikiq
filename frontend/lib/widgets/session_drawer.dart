import 'package:flutter/material.dart';

class SessionDrawer extends StatelessWidget {
  final List<Map<String, dynamic>> threads;
  final String? currentThreadId;
  final Function(String threadId, int index) onDeleteSession;
  final Function(String threadId) onOpenSession;
  final VoidCallback onNewChat;

  const SessionDrawer({
    super.key,
    required this.threads,
    required this.currentThreadId,
    required this.onDeleteSession,
    required this.onOpenSession,
    required this.onNewChat,
  });

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: Container(
        color: const Color(0xFF0F2C31),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Drawer header
            Container(
              padding: const EdgeInsets.fromLTRB(24, 64, 24, 24),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Row(
                    children: [
                      Icon(
                        Icons.spatial_audio_off_rounded,
                        color: Color(0xFFE6F4F1),
                        size: 18,
                      ),
                      SizedBox(width: 12),
                      Text(
                        "SESSIONS",
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 1.5,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                  // New chat button
                  IconButton(
                    icon: const Icon(
                      Icons.add_circle_outline,
                      size: 20,
                      color: Color(0xFFE6F4F1),
                    ),
                    onPressed: onNewChat,
                  ),
                ],
              ),
            ),

            const Divider(color: Colors.white12, height: 1),

            // Session list
            Expanded(
              child: threads.isEmpty
                  ? const Padding(
                      padding: EdgeInsets.all(24),
                      child: Text(
                        "No sessions yet.\nStart a new query above.",
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.white38,
                          height: 1.6,
                        ),
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 12,
                      ),
                      itemCount: threads.length,
                      itemBuilder: (context, index) {
                        final thread = threads[index];
                        final String threadId = thread['id'].toString();
                        final bool isSelected = threadId == currentThreadId;

                        return Container(
                          margin: const EdgeInsets.only(bottom: 4),
                          child: ListTile(
                            selected: isSelected,
                            selectedTileColor: Colors.white.withOpacity(0.08),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                            title: Text(
                              thread['title'] ?? 'Untitled Session',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                fontSize: 13,
                                color: isSelected
                                    ? Colors.white
                                    : Colors.white60,
                                fontWeight: isSelected
                                    ? FontWeight.w600
                                    : FontWeight.normal,
                              ),
                            ),
                            trailing: IconButton(
                              icon: Icon(
                                Icons.delete_outline,
                                size: 16,
                                color: Colors.white.withOpacity(0.35),
                              ),
                              onPressed: () => onDeleteSession(threadId, index),
                            ),
                            onTap: () => onOpenSession(threadId),
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
