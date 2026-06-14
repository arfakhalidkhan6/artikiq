import 'package:flutter/material.dart';

class SignUpScreen extends StatelessWidget {
  final TextEditingController nameController;
  final TextEditingController emailController;
  final TextEditingController passwordController;
  final String? selectedGender;
  final bool isLoading;
  final ValueChanged<String?> onGenderChanged;
  final VoidCallback onSignUpPressed;
  final VoidCallback onToggleMode;

  const SignUpScreen({
    super.key,
    required this.nameController,
    required this.emailController,
    required this.passwordController,
    required this.selectedGender,
    required this.isLoading,
    required this.onGenderChanged,
    required this.onSignUpPressed,
    required this.onToggleMode,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 420,
      padding: const EdgeInsets.all(32.0),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 24,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Center(
            child: Column(
              children: [
                Icon(Icons.local_hospital, size: 48, color: Color(0xFF0A8491)),
                SizedBox(height: 12),
                Text(
                  "ArtikIQ Workspace",
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1E293B),
                  ),
                ),
                SizedBox(height: 6),
                Text(
                  "Create your account parameters below",
                  style: TextStyle(fontSize: 13, color: Color(0xFF64748B)),
                ),
              ],
            ),
          ),
          const SizedBox(height: 28),
          const Text(
            "FULL NAME",
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              color: Color(0xFF64748B),
              letterSpacing: 1.1,
            ),
          ),
          const SizedBox(height: 6),
          TextField(
            controller: nameController,
            style: const TextStyle(color: Color(0xFF1E293B)),
            decoration: InputDecoration(
              hintText: "Enter full name",
              filled: true,
              fillColor: const Color(0xFFF8FAFC),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: BorderSide.none,
              ),
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            "GENDER",
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              color: Color(0xFF64748B),
              letterSpacing: 1.1,
            ),
          ),
          const SizedBox(height: 6),
          DropdownButtonFormField<String>(
            value: selectedGender,
            dropdownColor: Colors.white,
            style: const TextStyle(color: Color(0xFF1E293B)),
            decoration: InputDecoration(
              filled: true,
              fillColor: const Color(0xFFF8FAFC),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: BorderSide.none,
              ),
            ),
            hint: const Text(
              "Select Gender",
              style: TextStyle(color: Colors.black38),
            ),
            items: ["Male", "Female", "Other"].map((String value) {
              return DropdownMenuItem<String>(
                value: value,
                child: Text(
                  value,
                  style: const TextStyle(color: Color(0xFF1E293B)),
                ),
              );
            }).toList(),
            onChanged: isLoading ? null : onGenderChanged,
          ),
          const SizedBox(height: 16),
          const Text(
            "EMAIL ADDRESS",
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              color: Color(0xFF64748B),
              letterSpacing: 1.1,
            ),
          ),
          const SizedBox(height: 6),
          TextField(
            controller: emailController,
            style: const TextStyle(color: Color(0xFF1E293B)),
            decoration: InputDecoration(
              hintText: "name@clinic.com",
              filled: true,
              fillColor: const Color(0xFFF8FAFC),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: BorderSide.none,
              ),
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            "SECURITY PASSWORD",
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              color: Color(0xFF64748B),
              letterSpacing: 1.1,
            ),
          ),
          const SizedBox(height: 6),
          TextField(
            controller: passwordController,
            obscureText: true,
            style: const TextStyle(color: Color(0xFF1E293B)),
            decoration: InputDecoration(
              hintText: "••••••••",
              filled: true,
              fillColor: const Color(0xFFF8FAFC),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: BorderSide.none,
              ),
            ),
          ),
          const SizedBox(height: 28),
          ElevatedButton(
            onPressed: isLoading ? null : onSignUpPressed,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0A8491),
              minimumSize: const Size(double.infinity, 48),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
            ),
            child: isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      color: Colors.white,
                      strokeWidth: 2,
                    ),
                  )
                : const Text(
                    "Sign Up",
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
          ),
          const SizedBox(height: 16),
          Center(
            child: TextButton(
              onPressed: isLoading ? null : onToggleMode,
              child: const Text(
                "Already have an account? Sign In",
                style: TextStyle(color: Color(0xFF0A8491)),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
