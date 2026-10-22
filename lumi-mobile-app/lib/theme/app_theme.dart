import 'package:flutter/material.dart';
import 'lumi_colors.dart';

class AppTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: const ColorScheme(
        brightness: Brightness.light,
        primary: LumiColors.primary,
        onPrimary: LumiColors.onPrimary,
        primaryContainer: LumiColors.primaryContainer,
        onPrimaryContainer: LumiColors.onPrimaryContainer,
        secondary: LumiColors.secondary,
        onSecondary: LumiColors.onSecondary,
        secondaryContainer: LumiColors.secondaryContainer,
        onSecondaryContainer: LumiColors.onSecondaryContainer,
        surface: LumiColors.surface,
        onSurface: LumiColors.onBackground,
        error: LumiColors.emergency,
        onError: LumiColors.onEmergency,
        errorContainer: LumiColors.emergencyContainer,
        onErrorContainer: LumiColors.onEmergencyContainer,
      ),
      scaffoldBackgroundColor: LumiColors.background,
      appBarTheme: const AppBarTheme(
        backgroundColor: LumiColors.surface,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          color: LumiColors.onBackground,
          fontSize: 20,
          fontWeight: FontWeight.w600,
          letterSpacing: -0.2,
        ),
        iconTheme: IconThemeData(color: LumiColors.primary),
      ),
      cardTheme: CardTheme(
        color: LumiColors.surfaceContainer,
        elevation: 0.5,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          elevation: 0,
          backgroundColor: LumiColors.primary,
          foregroundColor: LumiColors.onPrimary,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          textStyle: const TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: LumiColors.surface,
        elevation: 2,
        indicatorColor: LumiColors.primaryContainer,
        labelTextStyle: MaterialStateProperty.resolveWith((states) {
          if (states.contains(MaterialState.selected)) {
            return const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w700,
              color: LumiColors.onPrimaryContainer,
            );
          }
          return const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w500,
            color: LumiColors.secondary,
          );
        }),
      ),
      dividerTheme: const DividerThemeData(
        color: LumiColors.surfaceDim,
        thickness: 1,
      ),
    );
  }
}
