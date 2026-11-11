package com.cok.console.ui

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import com.cok.console.MainActivity

/** Emits user-enabled, high-priority local alerts while the console is active. */
internal class LocalAlertController(private val context: Context) {

    fun notifyRisk(title: String, detail: String) {
        val manager = context.getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            manager.createNotificationChannel(
                NotificationChannel(CHANNEL_ID, "风险提醒", NotificationManager.IMPORTANCE_HIGH).apply {
                    description = "保护罩、连接等需要立即处理的状态"
                },
            )
        }
        val intent = PendingIntent.getActivity(
            context,
            0,
            Intent(context, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
            },
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val builder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            Notification.Builder(context, CHANNEL_ID)
        } else {
            Notification.Builder(context)
        }
        manager.notify(
            NOTIFICATION_ID,
            builder
                .setSmallIcon(android.R.drawable.stat_notify_error)
                .setContentTitle(title)
                .setContentText(detail)
                .setStyle(Notification.BigTextStyle().bigText(detail))
                .setContentIntent(intent)
                .setAutoCancel(true)
                .setCategory(Notification.CATEGORY_ERROR)
                .build(),
        )
    }

    private companion object {
        const val CHANNEL_ID = "risk-alerts"
        const val NOTIFICATION_ID = 3101
    }
}
