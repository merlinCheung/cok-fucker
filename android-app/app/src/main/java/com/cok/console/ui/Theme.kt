package com.cok.console.ui

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

/** Calm, utilitarian dark palette tuned for an at-a-glance control console. */
object CokPalette {
    val bg = Color(0xFF0F141C)
    val surface = Color(0xFF18212C)
    val surfaceHigh = Color(0xFF202B38)
    val surfaceHigher = Color(0xFF283545)
    val line = Color(0xFF2C3A4C)
    val fg = Color(0xFFF4F7FB)
    val dim = Color(0xFFB1BDCC)
    val dim2 = Color(0xFF8795A8)
    val accent = Color(0xFF4F9BD7)
    val accentText = Color(0xFFDFF3FF)
    val ok = Color(0xFF52BD93)
    val warn = Color(0xFFE1B45C)
    val err = Color(0xFFEF7770)
}

private val CokColors = darkColorScheme(
    primary = CokPalette.accent,
    onPrimary = Color.White,
    background = CokPalette.bg,
    onBackground = CokPalette.fg,
    surface = CokPalette.surface,
    onSurface = CokPalette.fg,
    surfaceVariant = CokPalette.surfaceHigh,
    onSurfaceVariant = CokPalette.dim,
    error = CokPalette.err,
    outline = CokPalette.line,
)

@Composable
fun CokTheme(content: @Composable () -> Unit) {
    @Suppress("UNUSED_EXPRESSION")
    isSystemInDarkTheme()
    MaterialTheme(colorScheme = CokColors, content = content)
}
