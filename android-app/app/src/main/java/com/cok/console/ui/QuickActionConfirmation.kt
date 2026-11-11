package com.cok.console.ui

import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable

/** A lightweight guard before an action that changes game state. */
@Composable
fun QuickActionConfirmation(
    action: QuickAction,
    onDismiss: () -> Unit,
    onConfirm: () -> Unit,
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(action.confirmTitle) },
        text = { Text(action.confirmBody) },
        confirmButton = { Button(onClick = onConfirm) { Text("确认") } },
        dismissButton = { OutlinedButton(onClick = onDismiss) { Text("取消") } },
    )
}
